import enum
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from app import db


class ItemStatus(enum.Enum):
    captured = "Captured"
    surfaced = "Surfaced"
    listed = "Listed"
    sold = "Sold"


class ItemSource(enum.Enum):
    manual = "manual"
    auto = "auto"


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=True)
    date_purchased = db.Column(db.Date, nullable=False)
    price_purchased = db.Column(db.Numeric(10, 2), nullable=False)
    photo_url = db.Column(db.String(512), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.Enum(ItemStatus), nullable=False, default=ItemStatus.captured)
    source = db.Column(db.Enum(ItemSource), nullable=False, default=ItemSource.manual)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    collection_items = db.relationship("CollectionItem", backref="item", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Item {self.id} {self.name}>"

    @property
    def resale_value(self):
        """Computed live, never persisted — a category's multiplier is looked
        up (falling back to 'default') at every render, so admin changes to
        ResaleRate apply retroactively with no recompute job."""
        from app.models.resale_rate import ResaleRate

        multiplier = Decimal(str(ResaleRate.multiplier_for(self.category)))
        return (self.price_purchased * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
