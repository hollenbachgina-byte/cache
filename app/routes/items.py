from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Item, ItemCondition
from app.services.storage import PhotoUploadError, delete_item_photo, upload_photo

items_bp = Blueprint("items", __name__)

PRESET_CATEGORIES = [
    "Clothing",
    "Shoes",
    "Bags",
    "Accessories",
    "Electronics",
    "Home",
    "Other",
]

OPTIONAL_TEXT_FIELDS = ["brand", "retailer", "size", "material", "color", "dimensions", "storage_capacity"]


def get_suggested_categories(user_id):
    """Preset categories plus anything this user has already used, merged
    into one alphabetized list."""
    user_categories = {
        row[0]
        for row in db.session.query(Item.category)
        .filter_by(user_id=user_id)
        .distinct()
        .all()
    }
    return sorted(set(PRESET_CATEGORIES) | user_categories)


def _parse_condition(raw):
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return ItemCondition[raw]
    except KeyError:
        return None


def _validate_item_form(form, files, require_photo):
    """Shared between add and edit — returns (parsed_values, errors).
    parsed_values has real Python types (Decimal, date, enum); errors is
    keyed by field name for inline display."""
    name = form.get("name", "").strip()
    category = form.get("category", "").strip()
    date_str = form.get("date_purchased", "").strip()
    price_str = form.get("price_purchased", "").strip()
    description = form.get("description", "").strip()
    photo = files.get("photo")

    errors = {}

    if not name:
        errors["name"] = "Enter a name for this item."

    if not category:
        errors["category"] = "Enter a category."

    date_purchased = None
    if not date_str:
        errors["date_purchased"] = "Enter the date you bought this."
    else:
        try:
            date_purchased = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            errors["date_purchased"] = "Enter a valid date."

    price_purchased = None
    if not price_str:
        errors["price_purchased"] = "Enter what you paid."
    else:
        try:
            price_purchased = Decimal(price_str)
            if price_purchased < 0:
                raise InvalidOperation
        except InvalidOperation:
            errors["price_purchased"] = "Enter a valid price."

    if require_photo and (not photo or photo.filename == ""):
        errors["photo"] = "Add a photo."

    parsed = {
        "name": name,
        "category": category,
        "date_purchased": date_purchased,
        "price_purchased": price_purchased,
        "description": description or None,
        "condition": _parse_condition(form.get("condition")),
        "photo": photo,
    }
    for field in OPTIONAL_TEXT_FIELDS:
        parsed[field] = form.get(field, "").strip() or None

    return parsed, errors


@items_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_item():
    if request.method == "GET":
        return render_template(
            "items/add.html",
            values={},
            suggested_categories=get_suggested_categories(current_user.id),
        )

    parsed, errors = _validate_item_form(request.form, request.files, require_photo=True)

    if errors:
        return render_template(
            "items/add.html",
            errors=errors,
            values=request.form,
            suggested_categories=get_suggested_categories(current_user.id),
        ), 400

    try:
        photo_url = upload_photo(parsed["photo"], current_user.id)
    except PhotoUploadError as exc:
        return render_template(
            "items/add.html",
            errors={"photo": str(exc)},
            values=request.form,
            suggested_categories=get_suggested_categories(current_user.id),
        ), 400

    item = Item(
        user_id=current_user.id,
        name=parsed["name"],
        date_purchased=parsed["date_purchased"],
        price_purchased=parsed["price_purchased"],
        photo_url=photo_url,
        description=parsed["description"],
        category=parsed["category"],
        condition=parsed["condition"],
        **{field: parsed[field] for field in OPTIONAL_TEXT_FIELDS},
    )
    db.session.add(item)
    db.session.commit()

    all_items = Item.query.filter_by(user_id=current_user.id).all()
    new_total = sum((i.displayed_resale_value for i in all_items), Decimal("0.00"))
    delta = item.displayed_resale_value
    previous_total = new_total - delta

    return render_template(
        "items/add_success.html",
        previous_total=previous_total,
        new_total=new_total,
        delta=delta,
    )


def _get_owned_item_or_404(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        # 404, not 403 — don't reveal that another user's item exists at all.
        abort(404)
    return item


@items_bp.route("/item/<int:item_id>")
@login_required
def item_detail(item_id):
    item = _get_owned_item_or_404(item_id)
    return render_template("items/detail.html", item=item)


def _item_to_values(item):
    values = {
        "name": item.name,
        "category": item.category,
        "date_purchased": item.date_purchased.isoformat() if item.date_purchased else "",
        "price_purchased": item.price_purchased,
        "description": item.description or "",
        "condition": item.condition.name if item.condition else "",
    }
    for field in OPTIONAL_TEXT_FIELDS:
        values[field] = getattr(item, field) or ""
    return values


@items_bp.route("/item/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(item_id):
    item = _get_owned_item_or_404(item_id)

    if request.method == "GET":
        return render_template(
            "items/edit.html",
            item=item,
            values=_item_to_values(item),
            suggested_categories=get_suggested_categories(current_user.id),
        )

    # Photo is optional on edit — only replace it if a new one was chosen.
    parsed, errors = _validate_item_form(request.form, request.files, require_photo=False)

    if errors:
        return render_template(
            "items/edit.html",
            item=item,
            errors=errors,
            values=request.form,
            suggested_categories=get_suggested_categories(current_user.id),
        ), 400

    new_photo = parsed["photo"]
    if new_photo and new_photo.filename != "":
        try:
            new_photo_url = upload_photo(new_photo, current_user.id)
        except PhotoUploadError as exc:
            return render_template(
                "items/edit.html",
                item=item,
                errors={"photo": str(exc)},
                values=request.form,
                suggested_categories=get_suggested_categories(current_user.id),
            ), 400
        old_photo_url = item.photo_url
        item.photo_url = new_photo_url
        delete_item_photo(old_photo_url)

    item.name = parsed["name"]
    item.category = parsed["category"]
    item.date_purchased = parsed["date_purchased"]
    item.price_purchased = parsed["price_purchased"]
    item.description = parsed["description"]
    item.condition = parsed["condition"]
    for field in OPTIONAL_TEXT_FIELDS:
        setattr(item, field, parsed[field])

    db.session.commit()
    return redirect(url_for("items.item_detail", item_id=item.id))


@items_bp.route("/item/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    item = _get_owned_item_or_404(item_id)

    delete_item_photo(item.photo_url)
    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("cache.dashboard"))


@items_bp.route("/item/<int:item_id>/archive", methods=["POST"])
@login_required
def toggle_archived(item_id):
    item = _get_owned_item_or_404(item_id)
    item.is_archived = not item.is_archived
    db.session.commit()
    return redirect(url_for("items.item_detail", item_id=item.id))


@items_bp.route("/item/<int:item_id>/resale_override", methods=["POST"])
@login_required
def update_resale_override(item_id):
    item = _get_owned_item_or_404(item_id)
    raw_price = request.form.get("resale_price_override", "").strip()
    if raw_price:
        try:
            item.resale_price_override = Decimal(raw_price)
        except InvalidOperation:
            pass
    else:
        item.resale_price_override = None  # blank clears the override, back to computed resale_value
    db.session.commit()
    return redirect(url_for("items.item_detail", item_id=item.id))
