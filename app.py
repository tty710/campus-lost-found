# -*- coding: utf-8 -*-
from flask import Flask
from config import Config
from models import db
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    import os
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs("/tmp/instance", exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "\u8bf7\u5148\u767b\u5f55"
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes.auth import auth_bp
    from routes.items import items_bp
    from routes.claims import claims_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(claims_bp)
    app.register_blueprint(admin_bp)

    _init_flag = {"done": False}

    @app.before_request
    def _init_tables():
        if not _init_flag["done"]:
            _init_flag["done"] = True
            try:
                db.create_all()
            except Exception as e:
                import sys
                print(f"DB init warning: {e}", file=sys.stderr)

    @app.route("/health")
    def health():
        return "OK"

    @app.route("/")
    def home():
        from flask import redirect
        return redirect("/items/")

    return app

if __name__ == "__main__":
    create_app().run(debug=True, port=5000)