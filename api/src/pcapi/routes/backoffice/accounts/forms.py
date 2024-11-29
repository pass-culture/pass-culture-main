import datetime
import enum

from flask_wtf import FlaskForm
import wtforms

from pcapi.connectors.dms import models as dms_models
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
        data = q.data.strip(" \t,;")
        if len(data) < 3 and not str(data).isnumeric():
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
        street="street",
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
    street = fields.PCOptHiddenField("Adresse")
    postal_code = fields.PCOptPostalCodeHiddenField("Code postal")
    city = fields.PCOptHiddenField("Ville")
    marketing_email_subscription = fields.PCSwitchBooleanField("Abonné aux emails marketing", full_row=True)


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


class AccountUpdateRequestSearchForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Numéro de dossier")
    from_to_date = fields.PCDateRangeField(
        "Modifiés entre",
        validators=(wtforms.validators.Optional(),),
        max_date=datetime.date.today(),
        reset_to_blank=True,
    )
    page = wtforms.HiddenField("page", default="1", validators=(wtforms.validators.Optional(),))
    per_page = fields.PCSelectField(
        "Par page",
        choices=(("10", "10"), ("25", "25"), ("50", "50"), ("100", "100")),
        default="100",
        validators=(wtforms.validators.Optional(),),
    )
    has_found_user = fields.PCSelectMultipleField(
        "Compte jeune",
        choices=(("true", "Avec compte jeune"), ("false", "Sans compte jeune")),
    )
    status = fields.PCSelectMultipleField(
        "État",
        choices=utils.choices_from_enum(
            dms_models.GraphQLApplicationStates, formatter=filters.format_dms_application_status
        ),
    )
    update_type = fields.PCSelectMultipleField(
        "Type de demande",
        choices=utils.choices_from_enum(
            users_models.UserAccountUpdateType, formatter=filters.format_user_account_update_type
        ),
    )
    last_instructor = fields.PCTomSelectField(
        "Dernier instructeur",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_bo_users",
    )
