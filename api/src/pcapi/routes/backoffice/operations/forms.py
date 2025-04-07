import datetime
import re
from urllib.parse import urlparse

from flask_wtf import FlaskForm
import wtforms

from pcapi.core.operations import models
from pcapi.routes.backoffice.filters import format_special_event_response_status_str
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import search
from pcapi.routes.backoffice.forms import utils


RE_TYPEFORM_ID = r"^[a-zA-Z0-9]{4,}$"


class SearchSpecialEventForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Recherche dans le titre ou par identifiant Typeform")

    page = wtforms.HiddenField("page", default="1", validators=(wtforms.validators.Optional(),))
    per_page = fields.PCSelectField(
        "Par page",
        choices=(("10", "10"), ("25", "25"), ("50", "50"), ("100", "100")),
        default="100",
        validators=(wtforms.validators.Optional(),),
    )

    def is_empty(self) -> bool:
        return not any((self.q.data,))


class CreateSpecialEventForm(FlaskForm):
    typeform_id = fields.PCStringField(
        "Identifiant ou adresse de l'opération sur Typeform",
        validators=(wtforms.validators.DataRequired("La référence Typeform est obligatoire"),),
    )

    event_date = fields.PCDateField(
        "Date de l'opération",
        validators=(wtforms.validators.DataRequired("La date de l'opération est obligatoire"),),
    )

    def filter_typeform_id(self, data: str | None) -> str | None:
        if data:
            try:
                parsed = urlparse(data)
                if parsed.path.startswith("/form/"):
                    data = parsed.path.split("/")[2]
            except ValueError:
                pass
        return data

    def validate_typeform_id(self, typeform_id: fields.PCStringField) -> fields.PCStringField:
        if typeform_id.data:
            if not re.match(RE_TYPEFORM_ID, typeform_id.data):
                raise wtforms.validators.ValidationError("Le format n'est pas reconnu")
        return typeform_id

    def validate_event_date(self, event_date: fields.PCStringField) -> fields.PCStringField:
        if event_date.data < datetime.date.today():
            raise wtforms.validators.ValidationError(
                "La date de l'évènement ne peut pas être dans le passé",
            )
        return event_date


class OperationResponseForm(utils.PCForm):
    class Meta:
        csrf = False

    response_status = fields.PCSelectMultipleField(
        "État de la candidature",
        choices=utils.choices_from_enum(
            enum_cls=models.SpecialEventResponseStatus,
            formatter=format_special_event_response_status_str,
        ),
        coerce=models.SpecialEventResponseStatus,
    )
    eligibility = fields.PCSelectMultipleField(
        "Éligibilité", choices=utils.choices_from_enum(search.AccountSearchFilter)
    )
