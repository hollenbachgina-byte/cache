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

    # Hardcoded safety net matching this column's own spec'd default — only
    # matters before Step 10 seeds a real "default" row via Flask-Admin.
    FALLBACK_MULTIPLIER = 0.60

    @staticmethod
    def multiplier_for(category):
        rate = ResaleRate.query.filter_by(category=category).first()
        if rate:
            return rate.multiplier
        default_rate = ResaleRate.query.filter_by(category="default").first()
        if default_rate:
            return default_rate.multiplier
        return ResaleRate.FALLBACK_MULTIPLIER
