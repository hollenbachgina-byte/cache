from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Collection, CollectionItem, Item
from app.models.collection import generate_share_token

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
    return redirect(url_for("collections.collection_detail", collection_id=collection.id))


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

    share_url = None
    if collection.is_public and collection.share_token:
        share_url = url_for("collections.public_collection", share_token=collection.share_token, _external=True)

    return render_template(
        "collections/detail.html",
        collection=collection,
        items=items,
        available_items=available_items,
        share_url=share_url,
    )


@collections_bp.route("/collections/<int:collection_id>/edit", methods=["POST"])
@login_required
def edit_collection(collection_id):
    collection = _get_owned_collection_or_404(collection_id)
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if name:
        collection.name = name
        collection.description = description or None
        db.session.commit()
    return redirect(url_for("collections.collection_detail", collection_id=collection.id))


@collections_bp.route("/collections/<int:collection_id>/toggle_visibility", methods=["POST"])
@login_required
def toggle_visibility(collection_id):
    collection = _get_owned_collection_or_404(collection_id)
    collection.is_public = not collection.is_public
    if collection.is_public:
        collection.share_token = generate_share_token()
    else:
        collection.share_token = None  # invalidates any existing link immediately
    db.session.commit()
    return redirect(url_for("collections.collection_detail", collection_id=collection.id, share_modal=1))


@collections_bp.route("/collections/<int:collection_id>/delete", methods=["POST"])
@login_required
def delete_collection(collection_id):
    collection = _get_owned_collection_or_404(collection_id)
    db.session.delete(collection)  # cascades to CollectionItem rows only — Items are untouched
    db.session.commit()
    return redirect(url_for("profile.profile"))


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


@collections_bp.route("/collections/<int:collection_id>/item/<int:item_id>/remove", methods=["POST"])
@login_required
def remove_item_from_collection(collection_id, item_id):
    collection = _get_owned_collection_or_404(collection_id)
    collection_item = CollectionItem.query.filter_by(
        collection_id=collection.id, item_id=item_id
    ).first_or_404()
    db.session.delete(collection_item)  # unlinks only — the Item itself is untouched
    db.session.commit()
    return redirect(url_for("collections.collection_detail", collection_id=collection.id))


@collections_bp.route("/c/<share_token>")
def public_collection(share_token):
    """Public, unauthenticated view — reachable only while the collection's
    owner has it toggled on. Looked up by the random share_token, never by
    the sequential id (guessable), and is_public is checked explicitly too
    even though toggling off already clears the token — belt and suspenders
    against any future path that might leave a stale token in place."""
    collection = Collection.query.filter_by(share_token=share_token, is_public=True).first_or_404()
    items = [ci for ci in collection.collection_items]
    categories = sorted({ci.item.category for ci in items})
    return render_template(
        "collections/public.html",
        collection=collection,
        collection_items=items,
        categories=categories,
    )


@collections_bp.route("/c/<share_token>/item/<int:item_id>")
def public_item_detail(share_token, item_id):
    """Also public/unauthenticated, and also scoped by share_token rather
    than trusting item_id alone — otherwise this route would let anyone
    view any item in the app just by guessing ids, whether or not its
    owner ever shared the collection it's in."""
    collection = Collection.query.filter_by(share_token=share_token, is_public=True).first_or_404()
    collection_item = CollectionItem.query.filter_by(
        collection_id=collection.id, item_id=item_id
    ).first_or_404()
    return render_template(
        "collections/public_item.html",
        collection=collection,
        ci=collection_item,
    )
