from decimal import Decimal

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Item
from app.services.storage import PhotoUploadError, upload_photo

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile():
    items = Item.query.filter_by(user_id=current_user.id).all()
    cache_value = sum((item.resale_value for item in items), Decimal("0.00"))
    return render_template("profile/profile.html", cache_value=cache_value)


@profile_bp.route("/profile/name", methods=["POST"])
@login_required
def update_name():
    name = request.form.get("name", "").strip()
    current_user.name = name or None
    db.session.commit()
    return redirect(url_for("profile.profile"))


@profile_bp.route("/profile/photo", methods=["POST"])
@login_required
def update_photo():
    photo = request.files.get("photo")
    if photo and photo.filename != "":
        try:
            current_user.profile_photo_url = upload_photo(photo, current_user.id)
            db.session.commit()
        except PhotoUploadError:
            pass  # Profile photo is decorative; a bad upload just leaves the old one in place.
    return redirect(url_for("profile.profile"))
