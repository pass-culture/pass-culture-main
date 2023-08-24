from flask_wtf import FlaskForm

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


class DeleteProUser(utils.PCForm):
    email = fields.PCEmailField("Email")


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour le compte pro")
