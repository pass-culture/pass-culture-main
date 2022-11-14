from flask_wtf import FlaskForm
from wtforms import validators

import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.models as users_models
import pcapi.utils.email as email_utils

from . import fields
from . import utils


class EditAccountForm(FlaskForm):
    first_name = fields.PCOptStringField("Prénom")
    last_name = fields.PCOptStringField("Nom")
    email = fields.PCEmailField("Email")
    birth_date = fields.PCDateField("Date de naissance")
    id_piece_number = fields.PCOptStringField("N° pièce d'identité")
    address = fields.PCOptStringField("Adresse")
    postal_code = fields.PCPostalCodeField("Code postal")
    city = fields.PCOptStringField("Ville")

    def validate_postal_code(self, postal_code: fields.PCPostalCodeField) -> fields.PCPostalCodeField:
        if not postal_code.data.isnumeric():
            raise validators.ValidationError("Un code postal doit être composé de chiffres")
        return postal_code

    def filter_email(self, raw_email: str | None) -> str:
        if not raw_email:
            return ""
        return email_utils.sanitize_email(raw_email)


class ManualReviewForm(FlaskForm):
    status = fields.PCSelectWithPlaceholderValueField(
        "Statut", choices=utils.choices_from_enum(fraud_models.FraudReviewStatus)
    )
    eligibility = fields.PCSelectWithPlaceholderValueField(
        "Eligibilité", choices=utils.choices_from_enum(users_models.EligibilityType)
    )
    reason = fields.PCOptStringField("Raison du changement")
