from decimal import Decimal

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from app import db
from app.models import Item

cache_bp = Blueprint("cache", __name__)


@cache_bp.route("/")
@login_required
def dashboard():
    show_archived = request.args.get("show_archived") == "1"

    base_query = Item.query.filter_by(user_id=current_user.id)
    if not show_archived:
        base_query = base_query.filter_by(is_archived=False)
    all_items = base_query.order_by(Item.created_at.desc()).all()

    all_categories = sorted({item.category for item in all_items})

    selected_categories = request.args.getlist("category")
    if selected_categories:
        items = [item for item in all_items if item.category in selected_categories]
    else:
        items = all_items

    # Total always reflects active (non-archived) items only, regardless of
    # the show_archived toggle — archiving is meant to take something out
    # of your active cache value, not just hide it from the grid.
    active_items = Item.query.filter_by(user_id=current_user.id, is_archived=False).all()
    total_value = sum((item.displayed_resale_value for item in active_items), Decimal("0.00"))

    return render_template(
        "cache/dashboard.html",
        items=items,
        has_any_items=bool(all_items),
        total_value=total_value,
        all_categories=all_categories,
        selected_categories=selected_categories,
        show_archived=show_archived,
    )
