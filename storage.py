import os
import uuid
from supabase import create_client, Client

_supabase_client = None

def get_supabase() -> Client | None:
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    from flask import current_app
    url = current_app.config.get("SUPABASE_URL")
    key = current_app.config.get("SUPABASE_KEY")
    if url and key:
        _supabase_client = create_client(url, key)
        return _supabase_client
    return None

def upload_image(file, bucket="item-images"):
    supabase = get_supabase()
    if supabase is None:
        return None
    ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "jpg"
    path = f"{uuid.uuid4().hex}.{ext}"
    supabase.storage.from_(bucket).upload(
        path, file.read(),
        {"content-type": file.content_type or "image/jpeg"}
    )
    url = supabase.storage.from_(bucket).get_public_url(path)
    return path, url

def delete_image(path, bucket="item-images"):
    supabase = get_supabase()
    if supabase is None:
        return
    try:
        supabase.storage.from_(bucket).remove([path])
    except Exception:
        pass
