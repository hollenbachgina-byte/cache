"""Temporary placeholder for the See Cache dashboard (Build Spec Section 10,
Step 5). Exists now only so /register and /login have a real redirect target
to verify the auth flow end-to-end; gets replaced with the real dashboard."""
from flask import Blueprint
from flask_login import current_user, login_required

cache_bp = Blueprint("cache", __name__)


@cache_bp.route("/")
@login_required
def dashboard():
    return f"""
    <p style="font-family:sans-serif;padding:24px;">
      Logged in as {current_user.phone_number}.
      <br>Dashboard is built in Step 5.
      <br><a href="/logout">Log out</a>
    </p>
    """
