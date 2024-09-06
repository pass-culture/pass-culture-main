from flask import redirect
from flask import render_template
from flask import request
from flask_wtf.csrf import CSRFProtect
from werkzeug.wrappers.response import Response

from pcapi import repository
from pcapi.connectors import discord as discord_connector
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as user_models
from pcapi.core.users import repository as users_repo
from pcapi.models import db
import pcapi.routes.auth.exceptions as auth_exceptions
from pcapi.routes.auth.forms.forms import SigninForm
from pcapi.utils import requests

from . import blueprint
from . import utils


ERROR_STRING_PREFIX = "Erreur d'authentification Discord: "


@blueprint.auth_blueprint.route("/discord/signin", methods=["GET"])
def discord_signin() -> str:
    form = SigninForm()
    if error_message := request.args.get("error"):
        form.error_message = error_message

    return render_template("discord_signin.html", form=form)


@blueprint.auth_blueprint.route("/discord/success", methods=["GET"])
@repository.atomic()
def discord_success() -> Response | str:
    access_token = request.args.get("access_token")
    user_id = request.args.get("user_id")

    if not access_token:
        return redirect_with_error(f"{ERROR_STRING_PREFIX}access token non récupéré")
    if not user_id:
        return redirect_with_error(f"{ERROR_STRING_PREFIX}user_id pass Culture non récupéré")

    try:
        user_discord_id = discord_connector.get_user_id(access_token)
    except requests.exceptions.HTTPError:
        return render_retry_template(
            access_token=access_token,
            user_id=user_id,
            error_message="Erreur lors de la récupération de l'identifiant Discord",
        )

    if not user_discord_id:
        return render_retry_template(
            access_token=access_token,
            user_id=user_id,
            error_message="Erreur lors de la récupération de l'identifiant Discord",
        )
    try:
        update_discord_user(user_id, user_discord_id)
    except auth_exceptions.DiscordUserAlreadyLinked:
        return redirect_with_error("Ce compte Discord est déjà lié à un autre compte pass Culture.")
    except auth_exceptions.UserNotAllowed:
        return redirect_with_error("Accès refusé au serveur Discord. Contacte le support pour plus d'informations")

    try:
        discord_connector.add_to_server(access_token, user_discord_id)
    except requests.exceptions.HTTPError:
        return render_retry_template(
            access_token=access_token,
            user_id=user_id,
            error_message="Erreur lors de l'ajout au serveur Discord",
        )
    return redirect(discord_connector.DISCORD_HOME_URI, code=303)


@blueprint.auth_blueprint.route("/discord/callback", methods=["GET"])
def discord_call_back() -> str | Response | None:
    code = request.args.get("code")
    user_id = request.args.get("state")

    if not code:
        return redirect_with_error(f"{ERROR_STRING_PREFIX}code non récupéré")
    if not user_id:
        return redirect_with_error(f"{ERROR_STRING_PREFIX}user_id pass Culture non récupéré")

    try:
        access_token = discord_connector.retrieve_access_token(code)
    except requests.exceptions.HTTPError as error:
        error_message = ""
        if error.response:
            error_message = error.response.json().get("error_description")
            if not error_message:
                error_message = error.response.text
        error_message += "Tu peux réessayer ou contacter le support."
        return redirect_with_error(ERROR_STRING_PREFIX + error_message)

    return redirect(f"/auth/discord/success?access_token={access_token}&user_id={user_id}", code=303)


def update_discord_user(user_id: str, discord_id: str) -> None:
    already_linked_user = user_models.DiscordUser.query.filter_by(discordId=discord_id).first()
    if already_linked_user:
        raise auth_exceptions.DiscordUserAlreadyLinked()

    user = user_models.User.query.get(user_id)
    discord_user = user.discordUser

    if discord_user is None:
        # We still add the user to the database even if he doesn't have access to the discord server
        discord_user = user_models.DiscordUser(userId=user.id, discordId=discord_id, hasAccess=False)
        db.session.add(discord_user)
        raise auth_exceptions.UserNotAllowed()

    if not discord_user.hasAccess:
        raise auth_exceptions.UserNotAllowed()

    discord_user.discordId = discord_id


@blueprint.auth_blueprint.route("/discord/signin", methods=["POST"])
def discord_signin_post() -> str | Response | None:
    csrf = CSRFProtect()
    csrf.protect()
    form = SigninForm()
    if not form.validate():
        form.error_message = utils.build_form_error_msg(form)
        return render_template("discord_signin.html", form=form)

    email = form.email.data
    password = form.password.data

    try:
        user = users_repo.get_user_with_credentials(email, password, allow_inactive=True)
    except users_exceptions.UnvalidatedAccount:
        form.error_message = "L'email n'a pas été validé. Valide ton compte sur le pass Culture pour continuer"
        return render_template("discord_signin.html", form=form)

    except users_exceptions.CredentialsException:
        form.error_message = "Identifiant ou Mot de passe incorrect"
        return render_template("discord_signin.html", form=form)

    if user.account_state.is_deleted:
        form.error_message = "Le compte a été supprimé"
        return render_template("discord_signin.html", form=form)

    if user.account_state == user_models.AccountState.ANONYMIZED:
        form.error_message = "Le compte a été anonymisé"
        return render_template("discord_signin.html", form=form)

    url_redirection = discord_connector.build_discord_redirection_uri(user.id)
    return redirect(url_redirection)


def redirect_with_error(error_message: str) -> Response:
    repository.mark_transaction_as_invalid()
    return redirect(f"/auth/discord/signin?error={error_message}", code=303)


def handle_http_error(error: requests.exceptions.HTTPError) -> Response:
    error_message = ""
    if error.response:
        error_message = error.response.json().get("error_description")
        if not error_message:
            error_message = error.response.text
    error_message += "Tu peux réessayer ou contacter le support."
    return redirect_with_error(ERROR_STRING_PREFIX + error_message)


def render_retry_template(access_token: str, user_id: str, error_message: str) -> str:
    return render_template(
        "discord_retry.html",
        error=error_message,
        url=f"/auth/discord/success?access_token={access_token}&user_id={user_id}",
    )
