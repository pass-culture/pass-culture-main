import datetime
import urllib
from urllib.parse import urlencode

from flask import redirect
from flask import render_template
from flask import request
from flask_wtf.csrf import CSRFProtect
import requests
from werkzeug.wrappers.response import Response

from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as user_models
from pcapi.core.users import repository as users_repo
from pcapi.models import db
from pcapi.routes.auth.forms.forms import SigninForm

from . import blueprint


DISCORD_BOT_TOKEN = ""
DISCORD_GUILD_ID = "1202586082508808232"
DISCORD_CLIENT_ID = "1261948740915433574"
DISCORD_CLIENT_SECRET = ""
DISCORD_CALLBACK_URI = "http://localhost:5001/auth/discord/callback"
DISCORD_REDIRECT_SUCCESS = "http://localhost:5001/auth/discord/success"
DISCORD_FULL_REDIRECT_URI = (
    f"https://discord.com/api/oauth2/authorize"
    f"?client_id={DISCORD_CLIENT_ID}"
    f"&redirect_uri={DISCORD_CALLBACK_URI}"
    f"&response_type=code"
    f"&scope=identify%20guilds.join"
)


def process_redirect_url(redirect_url: str, authorization_code: str) -> str:
    # Prepare the redirect URL
    url_parts = list(urllib.parse.urlparse(redirect_url))
    queries = dict(urllib.parse.parse_qsl(url_parts[4]))
    queries["authorization_code"] = authorization_code
    url_parts[4] = urllib.parse.urlencode(queries)
    url = urllib.parse.urlunparse(url_parts)
    return url


@blueprint.auth_blueprint.route("/discord/signin", methods=["GET"])
def discord_signin() -> str:
    form = SigninForm()
    form.redirect_url.data = request.args.get("redirect_url")
    # form.discord_id.data = request.args.get("discord_id")
    url_redirection = DISCORD_FULL_REDIRECT_URI
    return render_template("discord_signin.html", form=form, url_redirection=url_redirection)


@blueprint.auth_blueprint.route("/discord/callback", methods=["GET"])
def discord_call_back() -> str | Response | None:
    code = request.args.get("code")
    form = SigninForm()
    form.redirect_url.data = DISCORD_FULL_REDIRECT_URI
    # form.discord_id.data = request.args.get("discord_id")
    if not code:
        return "Missing code", 400

    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_CALLBACK_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_response = requests.post("https://discord.com/api/oauth2/token", data=urlencode(data), headers=headers)
    token_response.raise_for_status()
    access_token = token_response.json().get("access_token")

    print(f"Access token received: {access_token}")

    if access_token:
        form.discord_id.data = access_token
    else:
        logging.error("Failed to retrieve access token")
        return "Failed to retrieve access token", 500

    return render_template("discord_signin.html", form=form)


@blueprint.auth_blueprint.route("/discord/signin", methods=["POST"])
def discord_signin_post() -> str | Response | None:
    csrf = CSRFProtect()
    csrf.protect()
    form = SigninForm()
    if not form.validate():
        form.error_message = "Identifiant ou Mot de passe incorrect"
        return render_template("discord_signin.html", form=form)
    email = form.email.data
    password = form.password.data
    url_redirection = form.redirect_url.data
    discord_id = form.discord_id.data
    try:
        user = users_repo.get_user_with_credentials(email, password, allow_inactive=True)
    except users_exceptions.UnvalidatedAccount:
        form.error_message = "L'email n'a pas été validé"
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
        status = "UNAUTHORIZED"
    elif discord_user.is_active:
        status = "ALREADY_ACTIVE"
    else:
        discord_user.discordId = discord_id
        db.session.commit()
        status = "AUTHORIZED"

        # Ajout de l'user au serveur
        userResponse = requests.get(
            "https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {discord_id}"}
        )
        userId = userResponse.json()["id"]
        data = {"access_token": discord_id}
        url = f"https://discord.com/api/guilds/{DISCORD_GUILD_ID}/members/{userId}"
        headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}", "Content-Type": "application/json"}
        response = requests.put(url, json=data, headers=headers)

    discord_token = token_utils.AsymetricToken.create(
        token_utils.TokenType.DISCORD_OAUTH,
        settings.DISCORD_JWT_PRIVATE_KEY,
        settings.DISCORD_JWT_PUBLIC_KEY,
        ttl=datetime.timedelta(minutes=15),
        data={"discord_id": form.discord_id.data, "status": status},
    )
    url = process_redirect_url(url_redirection, discord_token.encoded_token)
    return redirect(url, code=303)
