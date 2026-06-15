import os
import uuid
from datetime import datetime

from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, current_app)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image as PILImage

from models import db, Item, Image, Claim
import storage

items_bp = Blueprint("items", __name__)

CATEGORIES = [
    "????", "????", "????",
    "????", "????", "????", "??"
]

def allowed_file(filename):
    return "." in filename and            filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

def save_upload(file):
    """???? - ?? Supabase Storage??????"""
    ext = file.filename.rsplit(".", 1)[1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    
    # Try Supabase Storage
    result = storage.upload_image(file)
    if result:
        path, url = result
        return name, url
    
    # Fallback: local filesystem
    file.seek(0)
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = PILImage.open(file)
    img.thumbnail((1200, 1200))
    img.save(path)
    return name, None

@items_bp.route("/")
def index():
    page     = request.args.get("page", 1, type=int)
    item_type = request.args.get("type", "")
    category  = request.args.get("category", "")

    q = Item.query.order_by(Item.created_at.desc())
    if item_type in ("lost", "found"):
        q = q.filter_by(item_type=item_type)
    if category:
        q = q.filter_by(category=category)

    items = q.paginate(page=page, per_page=12, error_out=False)
    return render_template("index.html", items=items, categories=CATEGORIES,
                           current_type=item_type, current_category=category)

@items_bp.route("/search")
def search():
    keyword = request.args.get("q", "").strip()
    item_type = request.args.get("type", "")
    category  = request.args.get("category", "")
    page      = request.args.get("page", 1, type=int)

    q = Item.query
    if keyword:
        q = q.filter(
            db.or_(Item.title.contains(keyword),
                   Item.description.contains(keyword),
                   Item.location.contains(keyword))
        )
    if item_type in ("lost", "found"):
        q = q.filter_by(item_type=item_type)
    if category:
        q = q.filter_by(category=category)

    items = q.order_by(Item.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)

    return render_template("search.html", items=items, keyword=keyword,
                           categories=CATEGORIES,
                           current_type=item_type, current_category=category)

@items_bp.route("/publish", methods=["GET", "POST"])
@login_required
def publish():
    if request.method == "POST":
        title       = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category    = request.form.get("category", "").strip()
        location    = request.form.get("location", "").strip()
        item_type   = request.form.get("item_type", "").strip()
        found_date  = request.form.get("found_date", "").strip()

        if not title or not category or not item_type or not found_date:
            flash("????????", "danger")
            return render_template("publish.html", categories=CATEGORIES)

        try:
            found_date = datetime.strptime(found_date, "%Y-%m-%d").date()
        except ValueError:
            flash("??????", "danger")
            return render_template("publish.html", categories=CATEGORIES)

        item = Item(
            title=title, description=description, category=category,
            location=location, item_type=item_type,
            found_date=found_date, user_id=current_user.id
        )
        db.session.add(item)
        db.session.flush()

        files = request.files.getlist("images")
        for f in files:
            if f and f.filename and allowed_file(f.filename):
                filename, supabase_url = save_upload(f)
                img = Image(item_id=item.id, filename=filename, url=supabase_url or "")
                db.session.add(img)

        db.session.commit()
        flash("?????", "success")
        return redirect(url_for("items.item_detail", item_id=item.id))

    return render_template("publish.html", categories=CATEGORIES)

@items_bp.route("/item/<int:item_id>")
def item_detail(item_id):
    item = db.session.get(Item, item_id)
    if item is None:
        flash("?????", "danger")
        return redirect(url_for("items.index"))
    images = Image.query.filter_by(item_id=item.id).all()
    user_claim = None
    if current_user.is_authenticated:
        user_claim = Claim.query.filter_by(
            item_id=item.id, claimant_id=current_user.id
        ).first()
    return render_template("item_detail.html", item=item,
                           images=images, user_claim=user_claim)

@items_bp.route("/my-items")
@login_required
def my_items():
    items = Item.query.filter_by(user_id=current_user.id)                     .order_by(Item.created_at.desc()).all()
    return render_template("my_items.html", items=items)

@items_bp.route("/item/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    item = db.session.get(Item, item_id)
    if item is None or item.user_id != current_user.id:
        flash("????", "danger")
        return redirect(url_for("items.index"))
    for img in item.images:
        # Try Supabase delete first
        storage.delete_image(img.filename)
        # Also try local delete
        img_path = os.path.join(current_app.config["UPLOAD_FOLDER"], img.filename)
        if os.path.exists(img_path):
            os.remove(img_path)
    db.session.delete(item)
    db.session.commit()
    flash("???", "info")
    return redirect(url_for("items.my_items"))

@items_bp.route("/item/<int:item_id>/status", methods=["POST"])
@login_required
def update_status(item_id):
    item = db.session.get(Item, item_id)
    if item is None or item.user_id != current_user.id:
        flash("????", "danger")
        return redirect(url_for("items.index"))
    new_status = request.form.get("status", "").strip()
    if new_status in ("published", "cancelled"):
        item.status = new_status
        db.session.commit()
        flash("?????", "success")
    return redirect(url_for("items.item_detail", item_id=item.id))
