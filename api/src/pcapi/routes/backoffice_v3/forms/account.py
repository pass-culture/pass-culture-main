from flask_wtf import FlaskForm

import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.models as users_models
import pcapi.utils.email as email_utils

from . import fields
from . import utils


class EditAccountForm(FlaskForm):
    first_name = fields.PCOptStringField("Prénom")
    last_name = fields.PCOptStringField("Nom")
    email = fields.PCEmailField("Email")

    def filter_email(self, raw_email: str | None) -> str:
        if not raw_email:
            return ""
        return email_utils.sanitize_email(raw_email)


class ManualReviewForm(FlaskForm):
    status = fields.PCSelectField("Statut", choices=utils.choices_from_enum(fraud_models.FraudReviewStatus))
    eligibility = fields.PCSelectField("Eligibilité", choices=utils.choices_from_enum(users_models.EligibilityType))
    reason = fields.PCStringField("Raison du changement")
