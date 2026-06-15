import os, uuid
from PIL import Image as PILImage

def upload_image(file):
    from flask import current_app
    ext = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else "jpg"
    name = f"{uuid.uuid4().hex}.{ext}"
    file.seek(0)
    d = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(d, exist_ok=True)
    img = PILImage.open(file)
    img.thumbnail((1200, 1200))
    img.save(os.path.join(d, name))
    return name, None

def delete_image(filename):
    from flask import current_app
    p = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(p): os.remove(p)
