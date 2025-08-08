import enum

from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms.validators import NumberRange
from wtforms.validators import Optional

from pcapi.core.finance import models as finance_models
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils as forms_utils


not_implemented_incident_types = [
    finance_models.IncidentType.FRAUD,
    finance_models.IncidentType.OFFER_PRICE_REGULATION,
]


class IncidentCompensationModes(enum.Enum):
    FORCE_DEBIT_NOTE = "Générer une note de débit à la prochaine échéance"
    COMPENSATE_ON_BOOKINGS = "Récupérer l'argent sur les prochaines réservations"


class BaseIncidentCreationForm(FlaskForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    origin = fields.PCSelectField(
        "Origine de la demande",
        choices=forms_utils.choices_from_enum(finance_models.FinanceIncidentRequestOrigin),
        validators=[DataRequired("Information obligatoire")],
    )

    zendesk_id = fields.PCOptIntegerField(
        "N° de ticket Zendesk",
        validators=[
            Optional(),
            NumberRange(min=0, message="Doit contenir un nombre positif"),
        ],
    )

    comment = fields.PCOptStringField("Commentaire (facultatif)")


class CommercialGestureCreationForm(empty_forms.BatchForm, BaseIncidentCreationForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    total_amount = fields.PCDecimalField(
        "Montant total dû à l'acteur culturel (en euros, sans le calcul de barème)",
        use_locale=True,
        validators=[Optional()],
    )


class CollectiveCommercialGestureCreationForm(BaseIncidentCreationForm):
    pass


class CollectiveOverPaymentIncidentCreationForm(BaseIncidentCreationForm):
    pass


class BookingOverPaymentIncidentForm(empty_forms.BatchForm, BaseIncidentCreationForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    total_amount = fields.PCDecimalField(
        "Montant de l'incident à récupérer (en euros, sans le calcul de barème)",
        use_locale=True,
        validators=[Optional()],
    )
    percent = fields.PCDecimalField(
        "Pourcentage du montant des réservations à récupérer",
        default=100,
        validators=[
            Optional(),
            NumberRange(min=0, max=100, message="Le pourcentage doit être compris entre 0 %% et 100 %%."),
        ],
        use_locale=True,
    )


class IncidentValidationForm(FlaskForm):
    compensation_mode = fields.PCSelectField(
        "Mode de compensation", choices=forms_utils.choices_from_enum(IncidentCompensationModes)
    )


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne")


class BatchIncidentValidationForm(empty_forms.BatchForm, IncidentValidationForm):
    pass


class BatchIncidentCancellationForm(empty_forms.BatchForm, CommentForm):
    pass


class GetIncidentsSearchForm(forms_utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID de l'incident, de l'offre ou de la réservation, contremarque, N° de ticket Zendesk")

    status = fields.PCSelectMultipleField(
        "États",
        choices=forms_utils.choices_from_enum(
            finance_models.IncidentStatus,
            formatter=filters.format_finance_incident_status,
        ),
    )

    incident_type = fields.PCSelectMultipleField(
        "Type d'incident",
        choices=(
            (finance_models.IncidentType.OVERPAYMENT.name, "Trop perçu"),
            (finance_models.IncidentType.COMMERCIAL_GESTURE.name, "Geste commercial"),
        ),
    )

    is_collective = fields.PCSelectMultipleField(
        "Type de réservation",
        choices=(("true", "Collective"), ("false", "Individuelle")),
    )

    offerer = fields.PCTomSelectField(
        "Entités juridiques",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
    )

    venue = fields.PCTomSelectField(
        "Partenaires culturels porteurs de l'offre",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_venues",
    )

    origin = fields.PCSelectMultipleField(
        "Origine de la demande",
        choices=forms_utils.choices_from_enum(finance_models.FinanceIncidentRequestOrigin),
    )

    limit = fields.PCLimitField(
        "Nombre maximum de résultats",
        choices=(
            (100, "Afficher 100 résultats maximum"),
            (500, "Afficher 500 résultats maximum"),
            (1000, "Afficher 1000 résultats maximum"),
            (3000, "Afficher 3000 résultats maximum"),
        ),
        default="100",
        coerce=int,
        validators=(Optional(),),
    )

    from_date = fields.PCDateField("Créées à partir du", validators=(Optional(),))
    to_date = fields.PCDateField("Jusqu'au", validators=(Optional(),))

    def is_empty(self) -> bool:
        return not any(
            (
                self.q.data,
                self.status.data,
                self.incident_type.data,
                self.is_collective.data,
                self.offerer.data,
                self.venue.data,
                self.origin.data,
                self.from_date.data,
                self.to_date.data,
            )
        )
