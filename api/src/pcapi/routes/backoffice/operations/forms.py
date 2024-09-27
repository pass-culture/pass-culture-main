import re
from urllib.parse import urlparse

from flask_wtf import FlaskForm
import wtforms

from pcapi.routes.backoffice.forms import fields
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

    # TODO: event date
    # TODO: offerer ID
    # TODO: venue ID
    # TODO: offer ID ?

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
