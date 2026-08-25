import secrets
from datetime import datetime

from app import db


def generate_share_token():
    return secrets.token_urlsafe(16)


class Collection(db.Model):
    __tablename__ = "collections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    # Only set while is_public — cleared the moment visibility is turned
    # off, so an old link 404s immediately rather than staying valid.
    # Never guessable-sequential (ids are 1, 2, 3...); this is what a
    # public share link is actually looked up by.
    share_token = db.Column(db.String(64), unique=True, nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    collection_items = db.relationship(
        "CollectionItem", backref="collection", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Collection {self.id} {self.name}>"


class CollectionItem(db.Model):
    """Join table — an item can belong to multiple collections."""

    __tablename__ = "collection_items"

    collection_id = db.Column(db.Integer, db.ForeignKey("collections.id"), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), primary_key=True)
