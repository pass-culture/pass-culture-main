from flask_wtf import FlaskForm

import pcapi.core.fraud.models as fraud_models
import pcapi.core.users.models as users_models
from pcapi.routes.backoffice_v3 import filters
from pcapi.routes.backoffice_v3.forms import fields
from pcapi.routes.backoffice_v3.forms import utils


class EditAccountForm(utils.PCForm):
    first_name = fields.PCOptStringField("Prénom")
    last_name = fields.PCOptStringField("Nom")
    email = fields.PCEmailField("Email")
    birth_date = fields.PCDateField("Date de naissance")
    phone_number = fields.PCOptStringField("Numéro de téléphone")
    id_piece_number = fields.PCOptStringField("N° pièce d'identité")
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
    address = fields.PCOptHiddenField("Adresse")
    postal_code = fields.PCOptPostalCodeHiddenField("Code postal")
    city = fields.PCOptHiddenField("Ville")


class ManualReviewForm(FlaskForm):
    status = fields.PCSelectWithPlaceholderValueField(
        "Statut",
        choices=utils.choices_from_enum(fraud_models.FraudReviewStatus, formatter=filters.format_fraud_review_status),
    )
    eligibility = fields.PCSelectWithPlaceholderValueField(
        "Éligibilité",
        choices=utils.choices_from_enum(users_models.EligibilityType, formatter=filters.format_eligibility_type),
    )
    reason = fields.PCOptStringField("Raison du changement")


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour le compte jeune")
