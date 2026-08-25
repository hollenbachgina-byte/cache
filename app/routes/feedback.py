from flask import Blueprint, redirect, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Feedback

# Named "feedback_widget", not "feedback" — Flask-Admin auto-derives a
# blueprint name from the Feedback model ("feedback") for its ModelView,
# and Flask blueprint names must be unique.
feedback_bp = Blueprint("feedback_widget", __name__)


@feedback_bp.route("/feedback", methods=["POST"])
@login_required
def submit_feedback():
    message = request.form.get("message", "").strip()
    page_context = request.form.get("page_context", "").strip() or None
    if message:
        db.session.add(Feedback(user_id=current_user.id, message=message, page_context=page_context))
        db.session.commit()
    return redirect(request.referrer or url_for("cache.dashboard"))
