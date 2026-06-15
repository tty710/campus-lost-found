from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password   = db.Column(db.String(256), nullable=False)
    email      = db.Column(db.String(128), unique=True, nullable=False)
    phone      = db.Column(db.String(20), default="")
    role       = db.Column(db.String(16), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items  = db.relationship("Item",  backref="publisher", lazy="dynamic")
    claims = db.relationship("Claim", backref="claimant",  lazy="dynamic")

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)

    def is_admin(self):
        return self.role == "admin"

class Item(db.Model):
    __tablename__ = "items"
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, default="")
    category    = db.Column(db.String(32), nullable=False, index=True)
    location    = db.Column(db.String(128), default="")
    found_date  = db.Column(db.Date, nullable=False)
    item_type   = db.Column(db.String(8), nullable=False)  # lost | found
    status      = db.Column(db.String(16), default="published", index=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship("Image", backref="item", lazy="dynamic",
                             cascade="all, delete-orphan")
    claims = db.relationship("Claim", backref="item", lazy="dynamic",
                             cascade="all, delete-orphan")

class Image(db.Model):
    __tablename__ = "images"
    id         = db.Column(db.Integer, primary_key=True)
    item_id    = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    filename   = db.Column(db.String(256), nullable=False)
    url        = db.Column(db.String(512), default="")  # Supabase Storage public URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Claim(db.Model):
    __tablename__ = "claims"
    id          = db.Column(db.Integer, primary_key=True)
    item_id     = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message     = db.Column(db.Text, default="")
    proof       = db.Column(db.Text, default="")
    status      = db.Column(db.String(16), default="pending", index=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
