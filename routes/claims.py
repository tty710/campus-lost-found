from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Item, Claim

claims_bp = Blueprint("claims", __name__)

# --- 提交认领申请 ---
@claims_bp.route("/item/<int:item_id>/claim", methods=["POST"])
@login_required
def submit_claim(item_id):
    item = db.session.get(Item, item_id)
    if item is None:
        flash("物品不存在", "danger")
        return redirect(url_for("items.index"))

    if item.user_id == current_user.id:
        flash("不能认领自己发布的物品", "danger")
        return redirect(url_for("items.item_detail", item_id=item.id))

    if item.status == "cancelled":
        flash("该物品已取消发布", "danger")
        return redirect(url_for("items.item_detail", item_id=item.id))

    existing = Claim.query.filter_by(
        item_id=item.id, claimant_id=current_user.id
    ).first()
    if existing:
        flash("您已提交过认领申请", "warning")
        return redirect(url_for("items.item_detail", item_id=item.id))

    message = request.form.get("message", "").strip()
    proof   = request.form.get("proof", "").strip()

    claim = Claim(
        item_id=item.id, claimant_id=current_user.id,
        message=message, proof=proof
    )
    db.session.add(claim)
    db.session.commit()
    flash("认领申请已提交，请等待发布者审核", "success")
    return redirect(url_for("items.item_detail", item_id=item.id))

# --- 我的认领 ---
@claims_bp.route("/my-claims")
@login_required
def my_claims():
    claims = Claim.query.filter_by(claimant_id=current_user.id)\
                        .order_by(Claim.created_at.desc()).all()
    return render_template("my_claims.html", claims=claims)

# --- 发布者审批认领 ---
@claims_bp.route("/claim/<int:claim_id>/approve", methods=["POST"])
@login_required
def approve_claim(claim_id):
    claim = db.session.get(Claim, claim_id)
    if claim is None:
        flash("认领记录不存在", "danger")
        return redirect(url_for("items.index"))

    if claim.item.user_id != current_user.id:
        flash("无权操作", "danger")
        return redirect(url_for("items.index"))

    if claim.status != "pending":
        flash("该申请已处理", "warning")
        return redirect(url_for("items.item_detail", item_id=claim.item.id))

    claim.status = "approved"
    claim.item.status = "claimed"
    db.session.commit()
    flash("已通过认领申请", "success")
    return redirect(url_for("items.item_detail", item_id=claim.item.id))

# --- 发布者拒绝认领 ---
@claims_bp.route("/claim/<int:claim_id>/reject", methods=["POST"])
@login_required
def reject_claim(claim_id):
    claim = db.session.get(Claim, claim_id)
    if claim is None:
        flash("认领记录不存在", "danger")
        return redirect(url_for("items.index"))

    if claim.item.user_id != current_user.id:
        flash("无权操作", "danger")
        return redirect(url_for("items.index"))

    if claim.status != "pending":
        flash("该申请已处理", "warning")
        return redirect(url_for("items.item_detail", item_id=claim.item.id))

    claim.status = "rejected"
    db.session.commit()
    flash("已拒绝认领申请", "info")
    return redirect(url_for("items.item_detail", item_id=claim.item.id))

# --- 发布者标记已归还 ---
@claims_bp.route("/claim/<int:claim_id>/return", methods=["POST"])
@login_required
def mark_returned(claim_id):
    claim = db.session.get(Claim, claim_id)
    if claim is None:
        flash("认领记录不存在", "danger")
        return redirect(url_for("items.index"))

    if claim.item.user_id != current_user.id:
        flash("无权操作", "danger")
        return redirect(url_for("items.index"))

    if claim.status != "approved":
        flash("请先通过认领申请", "warning")
        return redirect(url_for("items.item_detail", item_id=claim.item.id))

    claim.status = "returned"
    claim.item.status = "returned"
    db.session.commit()
    flash("已标记为已归还", "success")
    return redirect(url_for("items.item_detail", item_id=claim.item.id))
