import enum

from flask_wtf import FlaskForm
import wtforms

from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import models as users_models
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import search
from pcapi.routes.backoffice.forms import utils


class AccountSearchFilter(enum.Enum):
    UNDERAGE = "Pass 15-17"
    BENEFICIARY = "Pass 18"
    PUBLIC = "Non bénéficiaire"
    SUSPENDED = "Suspendu"


class AccountSearchForm(search.SearchForm):
    filter = fields.PCSelectMultipleField("Filtres", choices=utils.choices_from_enum(AccountSearchFilter))

    def validate_q(self, q: fields.PCSearchField) -> fields.PCSearchField:
        q = super().validate_q(q)
        if len(q.data) < 3 and not str(q.data).isnumeric():
            raise wtforms.validators.ValidationError("Attention, la recherche doit contenir au moins 3 lettres.")
        return q


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
        ban_id="ban_id",
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
    reason = fields.PCOptCommentField("Raison du changement")


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour le compte jeune")
