import logging

from flask import url_for
from flask_admin.base import BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_admin.helpers import get_form_data
from flask_login import current_user
from werkzeug.utils import redirect


logger = logging.getLogger(__name__)


class BaseAdminMixin:
    # We need to override `create_form()` and `edit_form()`, otherwise
    # Flask-Admin loads the form classes from its cache, which is
    # populated when the admin view is registered. It does not work
    # for us because we want the form to be different depending on the
    # logged-in user's privileges (see `form_columns()`). Thus, we
    # don't use the cache.
    def create_form(self, obj=None):
        form_class = self.get_create_form()
        return form_class(get_form_data(), obj=obj)

    def edit_form(self, obj=None):
        form_class = self.get_edit_form()
        return form_class(get_form_data(), obj=obj)

    def is_accessible(self) -> bool:
        authorized = current_user.is_authenticated and current_user.isAdmin
        if not authorized:
            logger.warning("[ADMIN] Tentative d'accès non autorisé à l'interface d'administation par %s", current_user)

        return authorized


class BaseAdminView(BaseAdminMixin, ModelView):
    page_size = 25
    can_set_page_size = True
    can_create = False
    can_edit = False
    can_delete = False
    form_base_class = SecureForm

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.index"))

    def after_model_change(self, form, model, is_created):
        action = "Création" if is_created else "Modification"
        model_name = str(model)
        logger.info("[ADMIN] %s du modèle %s par l'utilisateur %s", action, model_name, current_user)

    def check_super_admins(self) -> bool:
        # `current_user` may be None, here, because this function
        # is (also) called when admin views are registered and
        # Flask-Admin populates its form cache.
        if not current_user or not current_user.is_authenticated:
            return False
        return current_user.is_super_admin()


class BaseCustomAdminView(BaseAdminMixin, BaseView):
    def check_super_admins(self) -> bool:
        # `current_user` may be None, here, because this function
        # is (also) called when admin views are registered and
        # Flask-Admin populates its form cache.
        if not current_user or not current_user.is_authenticated:
            return False
        return current_user.is_super_admin()
