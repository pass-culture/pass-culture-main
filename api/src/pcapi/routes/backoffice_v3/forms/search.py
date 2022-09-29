from flask_wtf import FlaskForm
import wtforms
from wtforms import validators

from pcapi.routes.backoffice_v3.serialization.search import TypeOptions

from . import fields
from . import utils


class SearchForm(FlaskForm):
    class Meta:
        csrf = False

    terms = fields.PCSearchField()
    order_by = wtforms.HiddenField("order_by", validators=[validators.Optional(strip_whitespace=True)])
    page = wtforms.HiddenField("page", validators=[validators.Optional()])
    per_page = wtforms.HiddenField("per_page", validators=[validators.Optional()])

    def add_error_to(self, field_name: str) -> None:
        msg = self.error_msg_builder(field_name)

        field = getattr(self, field_name)
        field.errors.append(msg)

    def error_msg_builder(self, field_name: str) -> str:
        match field_name:
            case "terms":
                return "Recherche invalide"
            case "order_by":
                return "Valeur de tri invalide"
            case "page":
                return "Numéro de page invalide"
            case "per_page":
                return "Nombre de résultats par page invalide"
            case _:
                return "Champ inconnu"


class ProSearchForm(SearchForm):
    pro_type = fields.PCSelectField("type", choices=utils.choices_from_enum(TypeOptions))
