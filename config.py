# -*- coding: utf-8 -*-
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "campus-lost-found-2024")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        ""
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    @staticmethod
    def init_app(app):
        uri = app.config["SQLALCHEMY_DATABASE_URI"]
        if not uri:
            raise RuntimeError("DATABASE_URL 环境变量未设置，请在 Vercel Dashboard 中添加")
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        if "sslmode" not in uri.lower() and "postgresql://" in uri:
            uri = uri + ("&" if "?" in uri else "?") + "sslmode=require"
        app.config["SQLALCHEMY_DATABASE_URI"] = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "/tmp/uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
