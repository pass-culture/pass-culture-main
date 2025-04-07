import enum

import wtforms

from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


class AccountSearchFilter(enum.Enum):
    PASS_15_17 = "Ancien Pass 15-17"
    PASS_18 = "Ancien Pass 18"
    PASS_17_V3 = "Pass 17"
    PASS_18_V3 = "Pass 18"
    PUBLIC = "Non bénéficiaire"
    SUSPENDED = "Suspendu"


class SearchForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCSearchField(label="")
    page = fields.PCOptHiddenIntegerField("page", default=1, validators=[wtforms.validators.Optional()])
    per_page = fields.PCOptHiddenIntegerField("per_page", default=21, validators=[wtforms.validators.Optional()])

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data and "%" in q.data:
            raise wtforms.validators.ValidationError("Le caractère % n'est pas autorisé")
        return q
