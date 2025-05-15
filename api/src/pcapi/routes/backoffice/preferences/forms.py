from pcapi.routes.backoffice.forms import fields, utils
from pcapi.routes.backoffice.forms.constants import area_choices


class EditPreferencesForm(utils.PCForm):
    departments = fields.PCSelectMultipleField("Départements", choices=area_choices)
