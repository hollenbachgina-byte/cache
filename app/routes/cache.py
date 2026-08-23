"""Temporary placeholder for the See Cache dashboard (Build Spec Section 10,
Step 5). Exists now only so /register and /login have a real redirect target,
and so the bottom nav (Step 4) can be verified before the real dashboard
content is built."""
from flask import Blueprint, render_template
from flask_login import login_required

cache_bp = Blueprint("cache", __name__)


@cache_bp.route("/")
@login_required
def dashboard():
    return render_template("cache/dashboard_stub.html")
