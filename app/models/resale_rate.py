from app import db


class ResaleRate(db.Model):
    """Admin-managed via Flask-Admin, not user-facing. The 'default' category
    row is the fallback multiplier for any item category without its own rate."""

    __tablename__ = "resale_rates"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), unique=True, nullable=False)
    multiplier = db.Column(db.Float, nullable=False, default=0.60)

    def __repr__(self):
        return f"<ResaleRate {self.category} x{self.multiplier}>"
