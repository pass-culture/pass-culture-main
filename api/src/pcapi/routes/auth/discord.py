import datetime
import urllib

from flask import redirect
from flask import render_template
from flask import request
from flask_wtf.csrf import CSRFProtect
from werkzeug.wrappers.response import Response

from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as user_models
from pcapi.core.users import repository as users_repo
from pcapi.models import db
from pcapi.routes.auth.forms.forms import SigninForm

from . import blueprint


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
    form.discord_id.data = request.args.get("discord_id")
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
    discord_token = token_utils.AsymetricToken.create(
        token_utils.TokenType.DISCORD_OAUTH,
        settings.DISCORD_JWT_PRIVATE_KEY,
        settings.DISCORD_JWT_PUBLIC_KEY,
        ttl=datetime.timedelta(minutes=15),
        data={"discord_id": form.discord_id.data, "status": status},
    )
    url = process_redirect_url(url_redirection, discord_token.encoded_token)
    return redirect(url, code=303)
