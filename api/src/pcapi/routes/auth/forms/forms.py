from pcapi.routes.auth.forms import fields
from pcapi.routes.auth.utils import PCForm


class SigninForm(PCForm):
    email = fields.PCEmailField("Adresse email")
    password = fields.PCPasswordField("Mot de passe")
    error_message: str = ""
