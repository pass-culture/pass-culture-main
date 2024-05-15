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
    marketing_email_subscription = fields.PCSwitchBooleanField("Abonné aux emails marketing", full_row=True)


class EditProUserFormWithNewProNav(EditProUserForm):
    eligibility_date = fields.PCOptDateTimeField(
        "Date d'éligibilité au bêta-test (heure de Paris)", format="%Y-%m-%dT%H:%M"
    )
    new_nav_date = fields.PCOptDateTimeField("Date d'activation du NPP (heure de Paris)", format="%Y-%m-%dT%H:%M")


class DeleteProUser(utils.PCForm):
    email = fields.PCEmailField("Email")


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour le compte pro")
