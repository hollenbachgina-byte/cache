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


class ItemCondition(enum.Enum):
    new = "New"
    like_new = "Like New"
    good = "Good"
    fair = "Fair"


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=True)
    date_purchased = db.Column(db.Date, nullable=False)
    price_purchased = db.Column(db.Numeric(10, 2), nullable=False)
    retailer = db.Column(db.String(255), nullable=True)
    photo_url = db.Column(db.String(512), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    # Category-specific attributes (Feedback Round 2, Section 9) — plain
    # nullable strings, not a separate attributes table. Which ones are
    # relevant is a UI-level concern (which fields the Add/Edit form shows
    # per category), not a schema-level one.
    size = db.Column(db.String(50), nullable=True)
    material = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(100), nullable=True)
    dimensions = db.Column(db.String(100), nullable=True)
    storage_capacity = db.Column(db.String(50), nullable=True)
    condition = db.Column(db.Enum(ItemCondition), nullable=True)
    status = db.Column(db.Enum(ItemStatus), nullable=False, default=ItemStatus.captured)
    source = db.Column(db.Enum(ItemSource), nullable=False, default=ItemSource.manual)
    # Archived = hidden from the default dashboard view, reversible. A
    # separate axis from `status` (which is reserved for the Phase 2 sell
    # lifecycle and is always "Captured" in Phase 1) — archiving isn't a
    # sell-flow state, just a "don't show me this by default" flag.
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
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
