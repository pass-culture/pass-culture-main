from flask_wtf import FlaskForm
from wtforms import validators

import pcapi.utils.email as email_utils
import pcapi.utils.phone_number as phone_utils

from . import fields


class EditProUserForm(FlaskForm):
    first_name = fields.PCOptStringField("Prénom")
    last_name = fields.PCOptStringField("Nom")
    email = fields.PCEmailField("Email")
    phone_number = fields.PCPhoneNumberField(
        "Téléphone",
    )
    postal_code = fields.PCPostalCodeField("Code postal")

    def validate_postal_code(self, postal_code: fields.PCPostalCodeField) -> fields.PCPostalCodeField:
        if not postal_code.data.isnumeric() and len(postal_code.data) == 5:
            raise validators.ValidationError("Un code postal doit être composé de 5 chiffres")
        return postal_code

    def validate_phone_number(self, phone_number: fields.PCPhoneNumberField) -> fields.PCPhoneNumberField:
        if not phone_utils.ParsedPhoneNumber(phone_number.data):
            raise validators.ValidationError("Veuillez indiquer un numéro de téléphone valide.")
        return phone_number

    def filter_email(self, raw_email: str | None) -> str:
        if not raw_email:
            return ""
        return email_utils.sanitize_email(raw_email)


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour le compte pro")
