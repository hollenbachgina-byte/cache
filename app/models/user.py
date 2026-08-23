from datetime import datetime

from flask_login import UserMixin

from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    phone_number = db.Column(db.String(32), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cache_email = db.Column(db.String(255), nullable=True)
    profile_photo_url = db.Column(db.String(512), nullable=True)

    items = db.relationship("Item", backref="user", lazy=True, cascade="all, delete-orphan")
    collections = db.relationship("Collection", backref="user", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.id} {self.phone_number}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
