import datetime
import logging
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
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.core.users import repository as users_repository
from pcapi.core.users.backoffice import api as backoffice_api
from pcapi.flask_app import backoffice_oauth
from pcapi.models import db
from pcapi.repository import atomic

from . import blueprint
from . import utils


logger = logging.getLogger(__name__)


@blueprint.backoffice_web.route("/login", methods=["GET"])
@atomic()
def login() -> utils.BackofficeResponse:
    use_google_without_credentials = settings.BACKOFFICE_LOGIN_WITHOUT_CREDENTIALS and (
        not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET
    )

    if use_google_without_credentials:
        from pcapi.utils import login_manager

        local_admin_email = "admin@passculture.local"
        local_admin = users_repository.find_user_by_email(local_admin_email)

        if not local_admin:
            local_admin = create_local_admin_user(local_admin_email, "Local", "Admin")

        local_admin.lastConnectionDate = datetime.datetime.utcnow()
        local_admin.add_admin_role()
        backoffice_api.upsert_roles(local_admin, list(perm_models.Roles))
        db.session.flush()

        login_user(local_admin, remember=True)
        login_manager.stamp_session(local_admin)
        return werkzeug.utils.redirect(url_for(".home"))

    redirect_uri = url_for(".authorize", _external=True)
    return backoffice_oauth.google.authorize_redirect(redirect_uri)


@blueprint.backoffice_web.route("/authorize", methods=["GET"])
@atomic()
def authorize() -> utils.BackofficeResponse:
    from pcapi.utils import login_manager

    token = backoffice_oauth.google.authorize_access_token()
    google_user = backoffice_oauth.google.parse_id_token(token, nonce=None)
    google_email = google_user["email"]
    user = users_repository.find_user_by_email(google_email)

    if user and not user.isActive:
        logger.info(
            "Failed authentication attempt",
            extra={"identifier": google_email, "user": user.id, "avoid_current_user": True, "success": False},
            technical_message_id="backoffice.authorize",
        )
        return werkzeug.exceptions.Forbidden()

    if settings.IS_TESTING or settings.IS_DEV or settings.IS_INTEGRATION or settings.IS_OPS:
        roles = list(perm_models.Roles)
    else:
        roles = fetch_user_roles_from_google_workspace(google_email)
        if not user and len(roles) == 0:
            logger.info(
                "Failed authentication attempt",
                extra={"identifier": google_email, "user": "not found", "avoid_current_user": True, "success": False},
                technical_message_id="backoffice.authorize",
            )
            session["google_email"] = google_email
            return redirect(url_for(".user_not_found"))

    if not user:
        user = create_local_admin_user(
            email=google_user["email"],
            first_name=google_user["given_name"],
            last_name=google_user["family_name"],
        )

    user.lastConnectionDate = datetime.datetime.utcnow()
    user.add_admin_role()
    backoffice_api.upsert_roles(user, roles)
    db.session.flush()

    logger.info(
        "Successful authentication attempt",
        extra={"identifier": google_email, "user": user.id, "avoid_current_user": True, "success": True},
        technical_message_id="backoffice.authorize",
    )

    login_user(user, remember=True)
    login_manager.stamp_session(user)
    return redirect(url_for(".home"))


@blueprint.backoffice_web.route("/logout", methods=["POST"])
@atomic()
@utils.custom_login_required(redirect_to=".home")
def logout() -> utils.BackofficeResponse:
    logout_user()
    return redirect(url_for(".home"), code=303)


@blueprint.backoffice_web.route("/user-not-found", methods=["GET"])
@atomic()
def user_not_found() -> utils.BackofficeResponse:
    return render_template("auth/user_not_found.html")


def fetch_user_roles_from_google_workspace(user_email: str) -> list[perm_models.Roles]:
    groups = auth_api.get_groups_from_google_workspace(user_email)
    role_names = auth_api.extract_roles_from_google_workspace_groups(groups)
    user_roles = []
    for name in role_names:
        try:
            role = perm_models.Roles(name)
            user_roles.append(role)
        except ValueError:
            continue
    return user_roles


def create_local_admin_user(email: str, first_name: str, last_name: str) -> users_models.User:
    local_admin = users_api.create_account(
        email=email,
        # generate a random password as the user won't login to anything else.
        password=secrets.token_urlsafe(20),
        birthdate=datetime.date(1990, 1, 1),
        is_email_validated=True,
        remote_updates=False,
    )

    local_admin.firstName = first_name
    local_admin.lastName = last_name
    local_admin.hasSeenProTutorials = True
    local_admin.hasSeenProRgs = True
    local_admin.needsToFillCulturalSurvey = False

    return local_admin
