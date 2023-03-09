from flask_wtf import FlaskForm

import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.models as users_models

from . import fields
from . import utils


def sanitize_pc_string(value: str | None) -> str | None:
    """
    Strips leading whitespaces and avoids empty strings in database.
    This filter may be set globally for any PCOptStringField but has not been tested on every form yet.
    """
    if value:
        value = value.strip()
    return value if value else None


class EditAccountForm(utils.PCForm):
    first_name = fields.PCOptStringField("Prénom", filters=(sanitize_pc_string,))
    last_name = fields.PCOptStringField("Nom", filters=(sanitize_pc_string,))
    email = fields.PCEmailField("Email")
    birth_date = fields.PCDateField("Date de naissance")
    phone_number = fields.PCOptStringField("Numéro de téléphone", filters=(sanitize_pc_string,))
    id_piece_number = fields.PCOptStringField("N° pièce d'identité", filters=(sanitize_pc_string,))
    postal_address_autocomplete = fields.PcPostalAddressAutocomplete(
        "Adresse",
        address="address",
        city="city",
        postal_code="postal_code",
        latitude=None,
        longitude=None,
        required=False,
        has_reset=True,
        has_manual_editing=True,
        limit=10,
    )
    address = fields.PCOptHiddenField("Adresse", filters=(sanitize_pc_string,))
    postal_code = fields.PCOptPostalCodeHiddenField("Code postal", filters=(sanitize_pc_string,))
    city = fields.PCOptHiddenField("Ville", filters=(sanitize_pc_string,))


class ManualReviewForm(FlaskForm):
    status = fields.PCSelectWithPlaceholderValueField(
        "Statut", choices=utils.choices_from_enum(fraud_models.FraudReviewStatus)
    )
    eligibility = fields.PCSelectWithPlaceholderValueField(
        "Éligibilité", choices=utils.choices_from_enum(users_models.EligibilityType)
    )
    reason = fields.PCOptStringField("Raison du changement")


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour le compte jeune")
