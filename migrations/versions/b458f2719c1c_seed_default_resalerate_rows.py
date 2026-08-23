"""Seed default ResaleRate rows

Revision ID: b458f2719c1c
Revises: 743209d7372d
Create Date: 2026-08-23 17:22:32.693398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b458f2719c1c'
down_revision = '743209d7372d'
branch_labels = None
depends_on = None


resale_rates_table = sa.table(
    "resale_rates",
    sa.column("category", sa.String),
    sa.column("multiplier", sa.Float),
)

# Matches app/routes/items.py's PRESET_CATEGORIES, plus the required
# "default" fallback row. All seeded at the column's own spec'd default
# (0.60) — real per-category tuning happens later via /admin, which is the
# whole point of Section 10 registering ResaleRate as a ModelView.
SEEDED_CATEGORIES = [
    "default",
    "Accessories",
    "Bags",
    "Clothing",
    "Electronics",
    "Home",
    "Jewelry",
    "Other",
    "Shoes",
    "Watches",
]


def upgrade():
    op.bulk_insert(
        resale_rates_table,
        [{"category": category, "multiplier": 0.60} for category in SEEDED_CATEGORIES],
    )


def downgrade():
    op.execute(
        resale_rates_table.delete().where(
            resale_rates_table.c.category.in_(SEEDED_CATEGORIES)
        )
    )
