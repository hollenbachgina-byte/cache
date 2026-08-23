from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Collection, CollectionItem, Item

collections_bp = Blueprint("collections", __name__)


def _get_owned_collection_or_404(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    if collection.user_id != current_user.id:
        abort(404)
    return collection


@collections_bp.route("/collections", methods=["POST"])
@login_required
def create_collection():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if not name:
        return redirect(url_for("profile.profile"))

    collection = Collection(user_id=current_user.id, name=name, description=description or None)
    db.session.add(collection)
    db.session.commit()
    return redirect(url_for("collections.collection_detail", collection_id=collection.id, created=1))


@collections_bp.route("/collections/<int:collection_id>")
@login_required
def collection_detail(collection_id):
    collection = _get_owned_collection_or_404(collection_id)
    in_collection_ids = {ci.item_id for ci in collection.collection_items}
    items = [ci.item for ci in collection.collection_items]

    available_query = Item.query.filter_by(user_id=current_user.id)
    if in_collection_ids:
        available_query = available_query.filter(~Item.id.in_(in_collection_ids))
    available_items = available_query.order_by(Item.created_at.desc()).all()

    share_url = url_for("collections.public_collection", share_token=collection.share_token, _external=True)
    just_created = request.args.get("created") == "1"

    return render_template(
        "collections/detail.html",
        collection=collection,
        items=items,
        available_items=available_items,
        share_url=share_url,
        just_created=just_created,
    )


@collections_bp.route("/collections/<int:collection_id>/add_item", methods=["POST"])
@login_required
def add_item_to_collection(collection_id):
    collection = _get_owned_collection_or_404(collection_id)
    item_ids = {int(i) for i in request.form.getlist("item_id")}

    existing_ids = {ci.item_id for ci in collection.collection_items}
    for item_id in item_ids - existing_ids:
        item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
        if item:
            db.session.add(CollectionItem(collection_id=collection.id, item_id=item.id))

    db.session.commit()
    return redirect(url_for("collections.collection_detail", collection_id=collection.id))


@collections_bp.route("/collections/<int:collection_id>/item/<int:item_id>/price", methods=["POST"])
@login_required
def update_asking_price(collection_id, item_id):
    collection = _get_owned_collection_or_404(collection_id)
    collection_item = CollectionItem.query.filter_by(
        collection_id=collection.id, item_id=item_id
    ).first_or_404()

    raw_price = request.form.get("asking_price", "").strip()
    if raw_price:
        try:
            collection_item.asking_price = Decimal(raw_price)
        except InvalidOperation:
            pass
    else:
        collection_item.asking_price = None  # blank clears the override, back to computed resale_value

    db.session.commit()
    return redirect(url_for("collections.collection_detail", collection_id=collection.id))


@collections_bp.route("/c/<share_token>")
def public_collection(share_token):
    """Public, unauthenticated view — anyone with the link can see this,
    by design. Looked up by the random share_token, never by the
    sequential id, so a shared collection doesn't expose the ability to
    enumerate every other collection in the app."""
    collection = Collection.query.filter_by(share_token=share_token).first_or_404()
    items = [ci for ci in collection.collection_items]
    return render_template("collections/public.html", collection=collection, collection_items=items)
