from flask_wtf import FlaskForm
from wtforms.validators import Optional

from pcapi.core.finance import models as finance_models
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.forms import fields


not_implemented_incident_types = [
    finance_models.IncidentType.COMMERCIAL_GESTURE,
    finance_models.IncidentType.FRAUD,
    finance_models.IncidentType.OFFER_PRICE_REGULATION,
]


class IncidentCreationForm(FlaskForm):
    kind = fields.PCSelectField(
        "Type d'incident",
        choices=[
            (opt.name, filters.format_finance_incident_type_str(opt))
            for opt in finance_models.IncidentType
            if opt not in not_implemented_incident_types
        ],
    )

    origin = fields.PCStringField("Origine de la demande")

    total_amount = fields.PCDecimalField(
        "Montant total de l'incident (à récupérer à la structure)", validators=[Optional()]
    )


class BookingIncidentForm(empty_forms.BatchForm, IncidentCreationForm):
    pass
