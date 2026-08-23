from datetime import datetime

from app import db


class Collection(db.Model):
    __tablename__ = "collections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
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
