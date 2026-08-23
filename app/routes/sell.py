from flask import Blueprint, render_template
from flask_login import login_required

sell_bp = Blueprint("sell", __name__)


@sell_bp.route("/sell")
@login_required
def sell():
    return render_template("sell/sell.html")
