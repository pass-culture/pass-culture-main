from pcapi.routes.auth.forms import fields
from pcapi.routes.auth.utils import PCForm


class SigninForm(PCForm):
    discord_id = fields.PCStringField(
        "Identifiant Discord",
    )
    email = fields.PCEmailField(
        "Adresse email",
    )
    password = fields.PCPasswordField(
        "Mot de passe",
    )
    redirect_url = fields.PCHiddenField(
        "redirect_url",
    )
    error_message: str = ""
