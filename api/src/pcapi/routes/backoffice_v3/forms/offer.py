import enum
import re

from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import categories
from pcapi.routes.backoffice_v3 import utils as bo_utils

from . import constants
from . import fields
from . import utils


class OfferSearchColumn(enum.Enum):
    ALL = "Tout"
    ID = "ID de l'offre"
    NAME = "Nom de l'offre"
    ISBN = "ISBN"
    VISA = "Visa d'exploitation"


class GetOffersListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID de l'offre ou liste d'ID, nom, ISBN, visa d'exploitation")
    where = fields.PCSelectField(
        "Chercher dans",
        choices=utils.choices_from_enum(OfferSearchColumn),
        default=OfferSearchColumn.ALL.name,
        validators=(wtforms.validators.Optional(),),
    )
    criteria = fields.PCAutocompleteSelectMultipleField(
        "Tags", choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_criteria"
    )
    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(categories.CategoryIdLabelEnum)
    )
    department = fields.PCSelectMultipleField("Départements", choices=constants.area_choices)
    venue = fields.PCAutocompleteSelectMultipleField(
        "Lieux", choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_venues"
    )
    limit = fields.PCSelectField(
        "Nombre maximum",
        choices=((100, "100"), (500, "500"), (1000, "1000"), (3000, "3000")),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data:
            q.data = q.data.strip()
        if self.where.data == OfferSearchColumn.ID.name and not re.match(r"^[\d\s,;]+$", q.data):
            raise wtforms.validators.ValidationError("La recherche ne correspond pas à un ID ou une liste d'ID")
        if self.where.data == OfferSearchColumn.ISBN.name and not bo_utils.is_isbn_valid(q.data):
            raise wtforms.validators.ValidationError("La recherche ne correspond pas au format d'un ISBN")
        if self.where.data == OfferSearchColumn.VISA.name and not bo_utils.is_visa_valid(q.data):
            raise wtforms.validators.ValidationError("La recherche ne correspond pas au format d'un visa")
        return q

    def is_empty(self) -> bool:
        return not any((self.q.data, self.criteria.data, self.category.data, self.department.data, self.venue.data))


class EditOfferForm(FlaskForm):
    criteria = fields.PCAutocompleteSelectMultipleField(
        "Tags", choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_criteria"
    )
    rankingWeight = fields.PCOptIntegerField("Pondération")


class BatchEditOfferForm(EditOfferForm):
    object_ids = wtforms.HiddenField("Identifiants à traiter")
