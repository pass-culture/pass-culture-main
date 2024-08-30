from flask import redirect
from flask import render_template
from flask import request
from flask_wtf.csrf import CSRFProtect
from werkzeug.wrappers.response import Response

from pcapi.connectors import discord as discord_connector
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as user_models
from pcapi.core.users import repository as users_repo
from pcapi.models import db
from pcapi.routes.auth.forms.forms import SigninForm
from pcapi.utils import requests

from . import blueprint
from . import utils


@blueprint.auth_blueprint.route("/discord/signin", methods=["GET"])
def discord_signin() -> str:
    form = SigninForm()
    form.discord_id.data = request.args.get("discord_id")
    form.redirect_url.data = discord_connector.DISCORD_FULL_REDIRECT_URI
    if error_message := request.args.get("error"):
        form.error_message = error_message

    return render_template("discord_signin.html", form=form)


@blueprint.auth_blueprint.route("/discord/callback", methods=["GET"])
def discord_call_back() -> str | Response | None:
    # Webhook called by the discord server once the discord authentication is successful
    code = request.args.get("code")
    ERROR_STRING_PREFIX = "Erreur d'authentification Discord: "
    if not code:
        return redirect(f"/auth/discord/signin?error={ERROR_STRING_PREFIX}code non récupéré", code=303)

    try:
        access_token = discord_connector.retrieve_access_token(code)
    except requests.exceptions.HTTPError as e:
        return redirect(f"/auth/discord/signin?error={ERROR_STRING_PREFIX}{e.response.json().get('error')}", code=303)

    if not access_token:
        return redirect(f"/auth/discord/signin?error={ERROR_STRING_PREFIX}access token non récupéré", code=303)

    try:
        discord_connector.add_to_server(access_token)
    except requests.exceptions.HTTPError as e:
        return redirect(
            f"/auth/discord/signin?error={ERROR_STRING_PREFIX}{e.response.json().get('message')}",
            code=303,
        )

    return redirect(discord_connector.DISCORD_HOME_URI, code=303)


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
    discord_id = form.discord_id.data
    url_redirection = form.redirect_url.data

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

    discord_user = user.discordUser
    if discord_user is None or not discord_user.hasAccess:
        if discord_user is None:
            discord_user = user_models.DiscordUser(userId=user.id, discordId=discord_id, hasAccess=False)
            db.session.add(discord_user)
            db.session.commit()
        form.error_message = "Accès refusé au serveur Discord. Contacte le support pour plus d'informations"
        return render_template("discord_signin.html", form=form)
    if discord_user.is_active:
        return redirect(url_redirection)

    discord_user.discordId = discord_id
    db.session.commit()
    return redirect(url_redirection)
