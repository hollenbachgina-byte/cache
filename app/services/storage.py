"""Server-side upload to Supabase Storage. The client already compresses
photos before submitting (static/js/image-compress.js); this re-validates
and re-encodes with Pillow as a safety net (Section 2/8 of the build spec)
before pushing bytes to Supabase using the service_role key — that key is
secret and must never reach the browser, so the upload has to happen here,
not client-side."""
import io
import uuid

import requests
from flask import current_app
from PIL import Image, UnidentifiedImageError

MAX_DIMENSION = 1600


class PhotoUploadError(Exception):
    pass


def upload_photo(file_storage, user_id):
    try:
        image = Image.open(file_storage.stream)
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise PhotoUploadError("That file isn't a valid image.")

    file_storage.stream.seek(0)
    image = Image.open(file_storage.stream).convert("RGB")

    if max(image.size) > MAX_DIMENSION:
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=80)
    data = buffer.getvalue()

    filename = f"{user_id}/{uuid.uuid4().hex}.jpg"
    bucket = current_app.config["SUPABASE_STORAGE_BUCKET"]
    base_url = current_app.config["SUPABASE_URL"]
    service_key = current_app.config["SUPABASE_SERVICE_KEY"]

    upload_url = f"{base_url}/storage/v1/object/{bucket}/{filename}"
    response = requests.post(
        upload_url,
        headers={
            "Authorization": f"Bearer {service_key}",
            "apikey": service_key,
            "Content-Type": "image/jpeg",
        },
        data=data,
        timeout=30,
    )
    if not response.ok:
        raise PhotoUploadError(f"Photo upload failed: {response.status_code} {response.text}")

    return f"{base_url}/storage/v1/object/public/{bucket}/{filename}"


def delete_item_photo(photo_url):
    """Best-effort cleanup when an item is deleted — not spec-required, but
    leaving orphaned files in the bucket forever is just storage litter.
    Failures here shouldn't block the actual item deletion."""
    bucket = current_app.config["SUPABASE_STORAGE_BUCKET"]
    base_url = current_app.config["SUPABASE_URL"]
    service_key = current_app.config["SUPABASE_SERVICE_KEY"]

    marker = f"/object/public/{bucket}/"
    if marker not in photo_url:
        return
    path = photo_url.split(marker, 1)[1]

    try:
        requests.delete(
            f"{base_url}/storage/v1/object/{bucket}/{path}",
            headers={
                "Authorization": f"Bearer {service_key}",
                "apikey": service_key,
            },
            timeout=10,
        )
    except requests.RequestException:
        pass
