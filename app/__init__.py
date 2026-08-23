from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app import models  # noqa: F401  registers model classes with SQLAlchemy metadata

    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.cache import cache_bp
    from app.routes.items import items_bp
    from app.routes.profile import profile_bp
    from app.routes.collections import collections_bp
    from app.routes.sell import sell_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cache_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(sell_bp)

    from app.admin import init_admin

    init_admin(app, db)

    return app
