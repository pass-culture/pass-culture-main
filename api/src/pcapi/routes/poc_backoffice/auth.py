import datetime
import secrets

from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask_login import login_user
from flask_login import logout_user
import werkzeug

from pcapi import settings
from pcapi.core.auth import api as auth_api
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
import pcapi.core.users.api as users_api
from pcapi.flask_app import app
from pcapi.flask_app import oauth
from pcapi.models import db
from pcapi.models.feature import FeatureToggle

from . import blueprint
from . import utils


@blueprint.poc_backoffice_web.route("/unauthorized", methods=["GET"])
def unauthorized():  # type: ignore
    return render_template("unauthorized.template.html")


@blueprint.poc_backoffice_web.route("/login", methods=["GET"])
@app.login_manager.unauthorized_handler  # type: ignore [attr-defined]
@utils.ff_enabled(FeatureToggle.ENABLE_NEW_BACKOFFICE_POC, redirect_to=".unauthorized")
def login():  # type: ignore
    is_testing_or_dev_without_google_credentials = (settings.IS_TESTING or settings.IS_DEV) and (
        not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET
    )

    if is_testing_or_dev_without_google_credentials:
        from pcapi.utils import login_manager

        local_admin_email = "admin@passculture.local"
        local_admin = users_repository.find_user_by_email(local_admin_email)

        if not local_admin:
            local_admin = create_local_admin_user(local_admin_email, "Local", "Admin")

        login_user(local_admin, remember=True)
        login_manager.stamp_session(local_admin)
        return werkzeug.utils.redirect(url_for(".home"))

    redirect_uri = url_for(".authorize", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@blueprint.poc_backoffice_web.route("/authorize", methods=["GET"])
@utils.ff_enabled(FeatureToggle.ENABLE_NEW_BACKOFFICE_POC, redirect_to=".unauthorized")
def authorize():  # type: ignore
    from pcapi.utils import login_manager

    token = oauth.google.authorize_access_token()
    google_user = oauth.google.parse_id_token(token)
    google_email = google_user["email"]
    user = users_repository.find_user_by_email(google_email)

    if user and not user.isActive:
        return werkzeug.exceptions.Forbidden()

    if settings.IS_TESTING or settings.IS_DEV:
        if not user:
            user = create_local_admin_user(
                email=google_user["email"],
                first_name=google_user["name"],
                last_name=google_user["family_name"],
                given_name=google_user["given_name"],
            )
    else:
        if not user:
            session["google_email"] = google_email
            return redirect(url_for(".user_not_found"))

        user.backoffice_permissions = fetch_user_permissions_from_google_workspace(user)
        db.session.commit()

    login_user(user, remember=True)
    login_manager.stamp_session(user)
    return redirect(url_for(".home"))


@blueprint.poc_backoffice_web.route("/logout", methods=["POST"])
#  @utils.custom_login_required(redirect_to=".home")
def logout():  # type: ignore
    logout_user()
    return redirect(url_for(".home"))


@blueprint.poc_backoffice_web.route("/user-not-found", methods=["GET"])
def user_not_found():  # type: ignore
    return render_template("user_not_found.template.html")


def fetch_user_permissions_from_google_workspace(user: users_models.User) -> list[perm_models.Permission]:
    groups = auth_api.get_groups_from_google_workspace(user.email)
    backoffice_roles = auth_api.extract_roles_from_google_workspace_groups(groups)
    return auth_api.get_permissions_from_roles(backoffice_roles)


def create_local_admin_user(
    email: str, first_name: str, last_name: str, given_name: str | None = None
) -> users_models.User:
    local_admin = users_api.create_account(
        email=email,
        password="not-so-secret-password",
        birthdate=datetime.date(1990, 1, 1),
        is_email_validated=True,
        remote_updates=False,
    )
    local_admin.roles = [users_models.UserRole.ADMIN]
    local_admin.firstName = first_name
    local_admin.lastName = last_name
    local_admin.publicName = given_name if given_name is not None else f"{first_name} {last_name}"
    # generate a random password as the user won't login to anything else.
    local_admin.setPassword(secrets.token_urlsafe(20))
    return local_admin
