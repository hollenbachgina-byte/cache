from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Item
from app.services.storage import PhotoUploadError, delete_item_photo, upload_item_photo

items_bp = Blueprint("items", __name__)

PRESET_CATEGORIES = [
    "Watches",
    "Bags",
    "Shoes",
    "Clothing",
    "Accessories",
    "Jewelry",
    "Electronics",
    "Home",
    "Other",
]


def get_suggested_categories(user_id):
    """Preset categories first (curated order), then any categories this
    user has already used that aren't already in the preset list."""
    user_categories = sorted(
        row[0]
        for row in db.session.query(Item.category)
        .filter_by(user_id=user_id)
        .distinct()
        .all()
    )
    extra = [c for c in user_categories if c not in PRESET_CATEGORIES]
    return PRESET_CATEGORIES + extra


@items_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_item():
    if request.method == "GET":
        return render_template(
            "items/add.html",
            suggested_categories=get_suggested_categories(current_user.id),
        )

    form = request.form
    name = form.get("name", "").strip()
    brand = form.get("brand", "").strip()
    category = form.get("category", "").strip()
    date_str = form.get("date_purchased", "").strip()
    price_str = form.get("price_purchased", "").strip()
    description = form.get("description", "").strip()
    photo = request.files.get("photo")

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

    if not photo or photo.filename == "":
        errors["photo"] = "Add a photo."

    if errors:
        return render_template(
            "items/add.html",
            errors=errors,
            form=form,
            suggested_categories=get_suggested_categories(current_user.id),
        ), 400

    try:
        photo_url = upload_item_photo(photo, current_user.id)
    except PhotoUploadError as exc:
        return render_template(
            "items/add.html",
            errors={"photo": str(exc)},
            form=form,
            suggested_categories=get_suggested_categories(current_user.id),
        ), 400

    item = Item(
        user_id=current_user.id,
        name=name,
        brand=brand or None,
        date_purchased=date_purchased,
        price_purchased=price_purchased,
        photo_url=photo_url,
        description=description or None,
        category=category,
    )
    db.session.add(item)
    db.session.commit()

    all_items = Item.query.filter_by(user_id=current_user.id).all()
    new_total = sum((i.resale_value for i in all_items), Decimal("0.00"))
    delta = item.resale_value
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


@items_bp.route("/item/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    item = _get_owned_item_or_404(item_id)

    delete_item_photo(item.photo_url)
    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("cache.dashboard"))
