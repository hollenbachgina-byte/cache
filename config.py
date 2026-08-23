import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base config. Reads everything from environment variables (.env locally,
    real env vars on Render) — nothing secret is hardcoded here."""

    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
    SUPABASE_STORAGE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "item-photos")

    # Flask-Admin has no built-in access control and the data model has no
    # is_admin flag — gate /admin with HTTP Basic Auth instead of leaving it
    # open or expanding the schema for a single-admin CS50 project.
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

    # Client already compresses photos to ~1200px/JPEG q0.7 before upload; this
    # just caps how large an unexpected/uncompressed request body can be.
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
