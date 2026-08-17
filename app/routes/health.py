"""Temporary scaffold-verification route.

Confirms the app boots and can reach the Supabase Postgres database before
any models/migrations exist (Build Spec Section 10, Step 1). Doubles as a
Render health-check endpoint once deployed, so it's fine to keep long-term.
"""
from flask import Blueprint, jsonify
from sqlalchemy import text

from app import db

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
def health():
    status = {"app": "ok"}
    try:
        db.session.execute(text("SELECT 1"))
        status["database"] = "ok"
    except Exception as exc:
        status["database"] = f"error: {exc}"
    return jsonify(status)
