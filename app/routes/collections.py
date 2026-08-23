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
    if name:
        db.session.add(Collection(user_id=current_user.id, name=name))
        db.session.commit()
    return redirect(url_for("profile.profile"))


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

    return render_template(
        "collections/detail.html",
        collection=collection,
        items=items,
        available_items=available_items,
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
