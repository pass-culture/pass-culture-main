from wtforms import validators

from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


class EditProUserForm(utils.PCForm):
    first_name = fields.PCOptStringField("Prénom")
    last_name = fields.PCOptStringField("Nom")
    email = fields.PCEmailField("Email")
    phone_number = fields.PCPhoneNumberField(
        "Téléphone",
    )
    postal_code = fields.PCOptPostalCodeField("Code postal")
    marketing_email_subscription = fields.PCSwitchBooleanField("Abonné aux emails marketing", full_row=True)


class DeleteProUser(utils.PCForm):
    email = fields.PCEmailField("Email")


class CommentForm(utils.PCForm):
    comment = fields.PCCommentField("Commentaire interne pour le compte pro")


class DisconnectProUserForm(utils.PCForm):
    comment = fields.PCCommentField(
        "Commentaire facultatif à propos de la déconnexion",
        validators=[
            validators.Optional(""),
            validators.Length(min=1, max=1024, message="doit contenir entre %(min)d et %(max)d caractères"),
        ],
    )
