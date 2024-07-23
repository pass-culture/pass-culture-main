from pcapi.routes.auth.forms import fields
from pcapi.routes.auth.utils import PCForm


class SigninForm(PCForm):
    email = fields.PCEmailField("Adresse email")
    password = fields.PCPasswordField("Mot de passe")
    discord_id = fields.PCHiddenField("discord_id")
    redirect_url = fields.PCHiddenField("redirect_url")
    error_message: str = ""
