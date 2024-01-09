import enum

from flask_wtf import FlaskForm
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

    kind = fields.PCSelectField(
        "Type d'incident",
        choices=[
            (opt.name, filters.format_finance_incident_type_str(opt))
            for opt in finance_models.IncidentType
            if opt not in not_implemented_incident_types
        ],
    )

    origin = fields.PCStringField("Origine de la demande")


class CollectiveIncidentCreationForm(BaseIncidentCreationForm):
    pass


class BookingIncidentForm(empty_forms.BatchForm, BaseIncidentCreationForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    total_amount = fields.PCDecimalField(
        "Montant de l'incident à récupérer (sans le calcul de barème)", use_locale=True, validators=[Optional()]
    )


class IncidentValidationForm(FlaskForm):
    compensation_mode = fields.PCSelectField(
        "Mode de compensation", choices=forms_utils.choices_from_enum(IncidentCompensationModes)
    )
