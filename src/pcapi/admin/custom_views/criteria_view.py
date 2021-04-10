from typing import List

from wtforms.fields.core import StringField
from wtforms.form import Form
from wtforms.validators import DataRequired

from pcapi.admin.base_configuration import BaseAdminView


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
    column_filters: List[str] = []
    form_columns = ["description", "startDateTime", "endDateTime"]
    form_create_rules = ("name", "description", "startDateTime", "endDateTime")

    def get_create_form(self) -> Form:
        form = self.scaffold_form()
        form.name = StringField("Nom", [DataRequired()])
        return form
