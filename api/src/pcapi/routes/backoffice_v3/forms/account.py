from flask_wtf import FlaskForm

import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.models as users_models

from . import fields
from . import utils


class EditAccountForm(utils.PCForm):
    first_name = fields.PCOptStringField("Prénom")
    last_name = fields.PCOptStringField("Nom")
    email = fields.PCEmailField("Email")
    birth_date = fields.PCDateField("Date de naissance")
    id_piece_number = fields.PCOptStringField("N° pièce d'identité")
    address = fields.PCOptStringField("Adresse")
    postal_code = fields.PCOptPostalCodeField("Code postal")
    city = fields.PCOptStringField("Ville")


class ManualReviewForm(FlaskForm):
    status = fields.PCSelectWithPlaceholderValueField(
        "Statut", choices=utils.choices_from_enum(fraud_models.FraudReviewStatus)
    )
    eligibility = fields.PCSelectWithPlaceholderValueField(
        "Éligibilité", choices=utils.choices_from_enum(users_models.EligibilityType)
    )
    reason = fields.PCOptStringField("Raison du changement")
