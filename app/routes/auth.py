from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

import phonenumbers
from phonenumbers import NumberParseException

from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__)

MIN_PASSWORD_LENGTH = 8


def normalize_phone(raw):
    """Parses a phone number (assuming US if no country code) and returns its
    E.164 form for storage/lookup, or None if it isn't a valid number."""
    try:
        parsed = phonenumbers.parse(raw, "US")
    except NumberParseException:
        return None
    if not phonenumbers.is_valid_number(parsed):
        return None
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("cache.dashboard"))

    if request.method == "GET":
        if request.args.get("step") == "form":
            return render_template("auth/register_form.html")
        return render_template("auth/splash.html")

    raw_phone = request.form.get("phone_number", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    errors = {}

    normalized_phone = normalize_phone(raw_phone)
    if normalized_phone is None:
        errors["phone_number"] = "Enter a valid phone number."
    elif User.query.filter_by(phone_number=normalized_phone).first():
        errors["phone_number"] = "An account already exists for this number."

    if len(password) < MIN_PASSWORD_LENGTH:
        errors["password"] = f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords don't match."

    if errors:
        return render_template(
            "auth/register_form.html", errors=errors, phone_number=raw_phone
        ), 400

    user = User(
        phone_number=normalized_phone,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return render_template("auth/register_success.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("cache.dashboard"))

    if request.method == "GET":
        return render_template("auth/login.html")

    raw_phone = request.form.get("phone_number", "").strip()
    password = request.form.get("password", "")

    normalized_phone = normalize_phone(raw_phone)
    user = User.query.filter_by(phone_number=normalized_phone).first() if normalized_phone else None

    if user is None or not check_password_hash(user.password_hash, password):
        return render_template(
            "auth/login.html",
            error="That password doesn't match this account.",
            phone_number=raw_phone,
        ), 401

    login_user(user)
    return redirect(url_for("cache.dashboard"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
