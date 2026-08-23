"""Flask-Admin ModelViews (Build Spec Section 10). Flask-Admin has no
built-in access control, and the data model has no is_admin flag, so every
view here is gated behind HTTP Basic Auth (ADMIN_USERNAME/ADMIN_PASSWORD)
rather than left open or expanding the schema for a single-admin project."""
from flask import Response, current_app, request
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme

from app.models import Collection, Item, ResaleRate, User


def _check_admin_auth(auth):
    password = current_app.config.get("ADMIN_PASSWORD")
    if not password or not auth:
        return False
    return auth.username == current_app.config.get("ADMIN_USERNAME") and auth.password == password


class SecureAdminMixin:
    def is_accessible(self):
        return _check_admin_auth(request.authorization)

    def inaccessible_callback(self, name, **kwargs):
        return Response(
            "Admin access required.",
            401,
            {"WWW-Authenticate": 'Basic realm="cache admin"'},
        )


class SecureModelView(SecureAdminMixin, ModelView):
    pass


class SecureAdminIndexView(SecureAdminMixin, AdminIndexView):
    """Flask-Admin's root /admin/ page is a separate view class from
    ModelView — easy to protect every data view and still leave this shell
    page open by mistake, so it gets the exact same auth check."""


class UserAdmin(SecureModelView):
    column_exclude_list = ["password_hash"]
    form_excluded_columns = ["password_hash", "items", "collections"]
    column_searchable_list = ["phone_number", "name"]


class ItemAdmin(SecureModelView):
    column_searchable_list = ["name", "brand", "category"]
    column_filters = ["category", "status", "source"]


class ResaleRateAdmin(SecureModelView):
    column_searchable_list = ["category"]


class CollectionAdmin(SecureModelView):
    column_searchable_list = ["name"]


def init_admin(app, db):
    admin = Admin(
        app,
        name="cache admin",
        theme=Bootstrap4Theme(),
        index_view=SecureAdminIndexView(),
    )
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(ItemAdmin(Item, db.session))
    admin.add_view(ResaleRateAdmin(ResaleRate, db.session))
    admin.add_view(CollectionAdmin(Collection, db.session))
    return admin
