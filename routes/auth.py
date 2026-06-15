from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("items.index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email    = request.form.get("email", "").strip()
        phone    = request.form.get("phone", "").strip()

        if not username or not password or not email:
            flash("用户名、密码和邮箱不能为空", "danger")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("用户名已存在", "danger")
            return render_template("register.html")
        if User.query.filter_by(email=email).first():
            flash("邮箱已被注册", "danger")
            return render_template("register.html")

        user = User(username=username, email=email, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("注册成功，请登录", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("items.index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash("用户名或密码错误", "danger")
            return render_template("login.html")
        login_user(user)
        flash("登录成功", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("items.index"))
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("items.index"))
