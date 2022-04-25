from wtforms.fields import StringField
from wtforms.form import Form
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Regexp

from pcapi.admin.base_configuration import BaseAdminView
import pcapi.admin.rules as pcapi_rules


CRITERION_NAME_REGEX = r"^[^\s]+$"


class CriteriaView(BaseAdminView):
    can_create = True
    can_edit = True
    can_delete = True
    column_list = ["id", "name", "description", "startDateTime", "endDateTime"]
    column_labels = dict(
        name="Nom",
        description="Description",
        startDateTime="Date de début",
        endDateTime="Date de fin",
    )
    column_searchable_list = ["name", "description", "startDateTime", "endDateTime"]
    column_filters: list[str] = []
    form_columns = ["description", "startDateTime", "endDateTime"]
    form_create_rules = (
        "name",
        "description",
        "startDateTime",
        "endDateTime",
        pcapi_rules.HiddenField("csrf_token"),
    )

    def get_create_form(self) -> Form:
        form = self.scaffold_form()
        form.name = StringField(
            "Nom",
            [
                DataRequired(),
                Regexp(CRITERION_NAME_REGEX, message="Le nom ne doit contenir aucun caractère d'espacement"),
                Length(max=140, message="Le nom d'un tag ne peut excéder 140 caractères"),
            ],
        )
        return form
