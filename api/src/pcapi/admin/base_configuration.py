import logging
import secrets

from flask import session
from flask import url_for
from flask_admin import expose
from flask_admin.base import AdminIndexView as AdminIndexBaseView
from flask_admin.base import BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_admin.helpers import get_form_data
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from werkzeug.exceptions import Forbidden
from werkzeug.utils import redirect

from pcapi import settings
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.flask_app import oauth
from pcapi.models import db


logger = logging.getLogger(__name__)


class BaseAdminMixin:
    # We need to override `create_form()` and `edit_form()`, otherwise
    # Flask-Admin loads the form classes from its cache, which is
    # populated when the admin view is registered. It does not work
    # for us because we want the form to be different depending on the
    # logged-in user's privileges (see `form_columns()`). Thus, we
    # don't use the cache.
    @property
    def column_formatters(self):
        return {}

    def create_form(self, obj=None):
        form_class = self.get_create_form()
        return form_class(get_form_data(), obj=obj)

    def edit_form(self, obj=None):
        form_class = self.get_edit_form()
        return form_class(get_form_data(), obj=obj)

    def is_accessible(self) -> bool:
        authorized = current_user.is_authenticated and current_user.has_admin_role
        if not authorized:
            logger.warning("[ADMIN] Tentative d'accès non autorisé à l'interface d'administration par %s", current_user)

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


class AdminIndexView(AdminIndexBaseView):
    @expose("/")
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        return super().index()

    @expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        redirect_uri = url_for(".authorize", _external=True)
        return oauth.google.authorize_redirect(redirect_uri)

    @expose("/logout/")
    def logout_view(self):
        from pcapi.utils import login_manager

        logout_user()
        login_manager.discard_session()
        return redirect(url_for(".index"))

    @expose("/authorize/")
    def authorize(self):
        from pcapi.utils import login_manager

        token = oauth.google.authorize_access_token()
        google_user = oauth.google.parse_id_token(token)
        google_email = google_user["email"]
        db_user = users_repository.find_user_by_email(google_email)
        if db_user and not db_user.isActive:
            return Forbidden()

        if not db_user:
            if settings.IS_TESTING or settings.IS_DEV:
                db_user = users_models.User(
                    firstName=google_user["given_name"],
                    lastName=google_user["family_name"],
                    email=google_user["email"],
                    publicName=google_user["name"],
                    isEmailValidated=True,
                    isActive=True,
                    roles=[users_models.UserRole.ADMIN],
                )
                # generate a random password as the user won't login to anything else.
                db_user.setPassword(secrets.token_urlsafe(20))
                db.session.add(db_user)
                db.session.commit()
            else:
                session["google_email"] = google_email
                return redirect(url_for(".no_user_found_view"))

        login_user(db_user, remember=True)
        login_manager.stamp_session(db_user)
        return redirect(url_for(".index"))

    @expose("/no-user-found/")
    def no_user_found_view(self):
        from pcapi.utils import login_manager

        if current_user.is_authenticated:
            return redirect(url_for(".index"))

        if session.get("google_email") is None:
            return redirect(url_for(".index"))

        rendered_view = self.render("admin/no_user_found.html", email=session["google_email"])
        login_manager.discard_session()
        return rendered_view
