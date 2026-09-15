from pcapi.routes.discord.forms import fields
from pcapi.routes.discord.utils import PCForm


class SigninForm(PCForm):
    email = fields.PCEmailField("Adresse email")
    password = fields.PCPasswordField("Mot de passe")
    recaptcha_token = fields.PCLongHiddenField("Recaptcha Token")
    error_message: str = ""

    class Meta:
        csrf = True
