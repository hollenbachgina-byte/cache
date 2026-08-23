import secrets
from datetime import datetime
from decimal import Decimal

from app import db


def _generate_share_token():
    return secrets.token_urlsafe(16)


class Collection(db.Model):
    __tablename__ = "collections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # Public share links use this, not the sequential id — ids are guessable
    # (1, 2, 3...), which would let anyone enumerate every user's collections
    # once any single one is made public.
    share_token = db.Column(
        db.String(64), unique=True, nullable=False, index=True, default=_generate_share_token
    )
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
    # Owner-editable override for the shared/public page — defaults to the
    # item's own computed resale_value (Section 4) until explicitly set.
    # Lets the same item carry a different asking price in different
    # collections without touching the item's canonical resale math.
    asking_price = db.Column(db.Numeric(10, 2), nullable=True)

    @property
    def effective_price(self):
        if self.asking_price is not None:
            return self.asking_price
        return self.item.resale_value

    @effective_price.setter
    def effective_price(self, value):
        self.asking_price = Decimal(value) if value not in (None, "") else None
