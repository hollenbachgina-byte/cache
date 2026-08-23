from decimal import Decimal

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app import db
from app.models import Item

cache_bp = Blueprint("cache", __name__)


@cache_bp.route("/")
@login_required
def dashboard():
    all_items = Item.query.filter_by(user_id=current_user.id).order_by(Item.created_at.desc()).all()

    all_categories = sorted(
        row[0]
        for row in db.session.query(Item.category)
        .filter_by(user_id=current_user.id)
        .distinct()
        .all()
    )

    selected_categories = request.args.getlist("category")
    if selected_categories:
        items = [item for item in all_items if item.category in selected_categories]
    else:
        items = all_items

    total_value = sum((item.resale_value for item in all_items), Decimal("0.00"))

    return render_template(
        "cache/dashboard.html",
        items=items,
        has_any_items=bool(all_items),
        total_value=total_value,
        all_categories=all_categories,
        selected_categories=selected_categories,
    )
