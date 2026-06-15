from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Item, Claim, Image

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            flash("需要管理员权限", "danger")
            return redirect(url_for("items.index"))
        return f(*args, **kwargs)
    return decorated

# --- 管理后台首页 ---
@admin_bp.route("/")
@admin_required
def dashboard():
    total_users  = User.query.count()
    total_items  = Item.query.count()
    total_claims = Claim.query.count()
    pending_claims = Claim.query.filter_by(status="pending").count()
    lost_count   = Item.query.filter_by(item_type="lost").count()
    found_count  = Item.query.filter_by(item_type="found").count()
    return render_template("admin/dashboard.html",
                           total_users=total_users, total_items=total_items,
                           total_claims=total_claims, pending_claims=pending_claims,
                           lost_count=lost_count, found_count=found_count)

# --- 物品管理 ---
@admin_bp.route("/items")
@admin_required
def manage_items():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    q = Item.query.order_by(Item.created_at.desc())
    if status:
        q = q.filter_by(status=status)
    items = q.paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/items.html", items=items, current_status=status)

# --- 审核物品（管理员可修改、删除） ---
@admin_bp.route("/item/<int:item_id>/review", methods=["POST"])
@admin_required
def review_item(item_id):
    item = db.session.get(Item, item_id)
    if item is None:
        flash("物品不存在", "danger")
        return redirect(url_for("admin.manage_items"))
    action = request.form.get("action", "")
    if action == "delete":
        db.session.delete(item)
        db.session.commit()
        flash("已删除该物品", "info")
    elif action == "status":
        new_status = request.form.get("status", "")
        if new_status in ("published", "cancelled", "claimed", "returned"):
            item.status = new_status
            db.session.commit()
            flash("状态已更新", "success")
    return redirect(url_for("admin.manage_items"))

# --- 认领管理 ---
@admin_bp.route("/claims")
@admin_required
def manage_claims():
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "")
    q = Claim.query.order_by(Claim.created_at.desc())
    if status:
        q = q.filter_by(status=status)
    claims = q.paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/claims.html", claims=claims, current_status=status)

# --- 管理员审批认领 ---
@admin_bp.route("/claim/<int:claim_id>/approve", methods=["POST"])
@admin_required
def approve_claim(claim_id):
    claim = db.session.get(Claim, claim_id)
    if claim and claim.status == "pending":
        claim.status = "approved"
        claim.item.status = "claimed"
        db.session.commit()
        flash("已通过认领", "success")
    return redirect(url_for("admin.manage_claims"))

@admin_bp.route("/claim/<int:claim_id>/reject", methods=["POST"])
@admin_required
def reject_claim(claim_id):
    claim = db.session.get(Claim, claim_id)
    if claim and claim.status == "pending":
        claim.status = "rejected"
        db.session.commit()
        flash("已拒绝认领", "info")
    return redirect(url_for("admin.manage_claims"))

# --- 用户管理 ---
@admin_bp.route("/users")
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/user/<int:user_id>/role", methods=["POST"])
@admin_required
def toggle_role(user_id):
    user = db.session.get(User, user_id)
    if user and user.id != current_user.id:
        user.role = "admin" if user.role == "user" else "user"
        db.session.commit()
        flash(f"用户 {user.username} 角色已更新", "success")
    return redirect(url_for("admin.manage_users"))
