import os, uuid, base64
from io import BytesIO

def upload_image(file):
    """上传图片，返回 (filename, url_or_dataurl)"""
    try:
        from PIL import Image as PILImage
    except ImportError:
        return None, None
    from flask import current_app

    ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "jpg"
    name = f"{uuid.uuid4().hex}.{ext}"

    file.seek(0)
    img = PILImage.open(file)
    img.thumbnail((1200, 1200))

    # 尝试本地存储
    d = current_app.config["UPLOAD_FOLDER"]
    try:
        os.makedirs(d, exist_ok=True)
        img.save(os.path.join(d, name))
        return name, None
    except Exception:
        pass

    # Vercel /tmp 不可用：转为 base64 data URL
    buf = BytesIO()
    fmt = "JPEG" if ext in ("jpg", "jpeg") else ext.upper()
    if fmt == "WEBP":
        fmt = "WEBP"
    img.save(buf, format=fmt if fmt in ("JPEG", "PNG", "GIF", "WEBP") else "JPEG")
    dataurl = "data:image/" + ("jpeg" if ext in ("jpg","jpeg") else ext) + ";base64," + base64.b64encode(buf.getvalue()).decode()
    return name, dataurl

def delete_image(filename):
    from flask import current_app
    p = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(p):
        try:
            os.remove(p)
        except Exception:
            pass
