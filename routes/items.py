import os
import uuid
from datetime import datetime

from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, current_app)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image as PILImage

from models import db, Item, Image, Claim

items_bp = Blueprint("items", __name__)

CATEGORIES = [
    "证件卡类", "电子设备", "书籍文具",
    "衣物饰品", "钥匙钱包", "生活用品", "其他"
]

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

def save_upload(file):
    """保存上传图片，返回文件名"""
    ext = file.filename.rsplit(".", 1)[1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
    img = PILImage.open(file)
    img.thumbnail((1200, 1200))
    img.save(path)
    return name

# --- 首页：物品列表 ---
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

# --- 搜索 ---
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

# --- 发布物品 ---
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
            flash("请填写所有必填项", "danger")
            return render_template("publish.html", categories=CATEGORIES)

        try:
            found_date = datetime.strptime(found_date, "%Y-%m-%d").date()
        except ValueError:
            flash("日期格式错误", "danger")
            return render_template("publish.html", categories=CATEGORIES)

        item = Item(
            title=title, description=description, category=category,
            location=location, item_type=item_type,
            found_date=found_date, user_id=current_user.id
        )
        db.session.add(item)
        db.session.flush()  # 获取 item.id

        # 图片上传
        files = request.files.getlist("images")
        for f in files:
            if f and f.filename and allowed_file(f.filename):
                filename = save_upload(f)
                img = Image(item_id=item.id, filename=filename)
                db.session.add(img)

        db.session.commit()
        flash("发布成功！", "success")
        return redirect(url_for("items.item_detail", item_id=item.id))

    return render_template("publish.html", categories=CATEGORIES)

# --- 物品详情 ---
@items_bp.route("/item/<int:item_id>")
def item_detail(item_id):
    item = db.session.get(Item, item_id)
    if item is None:
        flash("物品不存在", "danger")
        return redirect(url_for("items.index"))
    images = Image.query.filter_by(item_id=item.id).all()
    # 当前用户的认领记录
    user_claim = None
    if current_user.is_authenticated:
        user_claim = Claim.query.filter_by(
            item_id=item.id, claimant_id=current_user.id
        ).first()
    return render_template("item_detail.html", item=item,
                           images=images, user_claim=user_claim)

# --- 我的发布 ---
@items_bp.route("/my-items")
@login_required
def my_items():
    items = Item.query.filter_by(user_id=current_user.id)\
                     .order_by(Item.created_at.desc()).all()
    return render_template("my_items.html", items=items)

# --- 删除物品 ---
@items_bp.route("/item/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):
    item = db.session.get(Item, item_id)
    if item is None or item.user_id != current_user.id:
        flash("无权操作", "danger")
        return redirect(url_for("items.index"))
    # 删除图片文件
    for img in item.images:
        img_path = os.path.join(current_app.config["UPLOAD_FOLDER"], img.filename)
        if os.path.exists(img_path):
            os.remove(img_path)
    db.session.delete(item)
    db.session.commit()
    flash("已删除", "info")
    return redirect(url_for("items.my_items"))

# --- 更新物品状态（发布者操作） ---
@items_bp.route("/item/<int:item_id>/status", methods=["POST"])
@login_required
def update_status(item_id):
    item = db.session.get(Item, item_id)
    if item is None or item.user_id != current_user.id:
        flash("无权操作", "danger")
        return redirect(url_for("items.index"))
    new_status = request.form.get("status", "").strip()
    if new_status in ("published", "cancelled"):
        item.status = new_status
        db.session.commit()
        flash("状态已更新", "success")
    return redirect(url_for("items.item_detail", item_id=item.id))
