import wtforms

from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


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
