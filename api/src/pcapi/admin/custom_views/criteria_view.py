from wtforms.fields.core import StringField
from wtforms.form import Form
from wtforms.validators import DataRequired
from wtforms.validators import Regexp

from pcapi.admin.base_configuration import BaseAdminView


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
    form_create_rules = ("name", "description", "startDateTime", "endDateTime")

    def get_create_form(self) -> Form:
        form = self.scaffold_form()
        form.name = StringField(
            "Nom",
            [
                DataRequired(),
                Regexp(CRITERION_NAME_REGEX, message="Le nom ne doit contenir aucun caractère d'espacement"),
            ],
        )
        return form
