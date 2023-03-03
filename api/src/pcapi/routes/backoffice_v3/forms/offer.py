from flask_wtf import FlaskForm

from pcapi.core.categories import categories

from . import constants
from . import fields
from . import utils


class GetOffersListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Id de l'offre, nom")
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

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data:
            q.data = q.data.strip()
        return q

    def is_empty(self) -> bool:
        return not any((self.q.data, self.criteria.data, self.category.data, self.department.data, self.venue.data))


class EditOfferForm(FlaskForm):
    criteria = fields.PCAutocompleteSelectMultipleField(
        "Tags", choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_criteria"
    )
    rankingWeight = fields.PCIntegerField("Pondération")
