# -*- coding: utf-8 -*-
import os
import re

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Supabase connection pooler (port 6543) - required for Vercel serverless
_POOLED_DB = "postgresql://postgres.edagdtolpmspurnohxkw:140d2f33b3e22f522128643dd977ba4d@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "campus-lost-found-2024")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", _POOLED_DB)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "connect_args": {
            "connect_timeout": 10,
        },
    }

    @staticmethod
    def init_app(app):
        uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if not uri:
            app.config["SQLALCHEMY_DATABASE_URI"] = _POOLED_DB
            uri = _POOLED_DB
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        if "sslmode" not in uri.lower() and "postgresql://" in uri:
            uri = uri + ("&" if "?" in uri else "?") + "sslmode=require"
        app.config["SQLALCHEMY_DATABASE_URI"] = uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "/tmp/uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
