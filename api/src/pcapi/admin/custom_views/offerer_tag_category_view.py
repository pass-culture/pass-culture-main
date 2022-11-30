from wtforms.fields import StringField
from wtforms.form import Form
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Regexp

from pcapi.admin.base_configuration import BaseAdminView


TAG_NAME_REGEX = r"^[^\s]+$"


class OffererTagCategoryView(BaseAdminView):
    can_create = True
    can_edit = True
    can_delete = True
    column_list = ["id", "name", "label"]
    column_labels = {"name": "Nom", "label": "Libellé"}
    column_searchable_list = ["name"]
    column_filters: list[str] = []

    def get_create_form(self) -> Form:
        form = self.scaffold_form()
        form.name = StringField(
            "Nom",
            [
                DataRequired(),
                Regexp(TAG_NAME_REGEX, message="Le nom ne doit contenir aucun caractère d'espacement"),
                Length(max=140, message="Le nom ne peut excéder 140 caractères"),
            ],
        )
        form.label = StringField(
            "Libellé",
            [
                Length(max=140, message="Le libellé ne peut excéder 140 caractères"),
            ],
        )
        return form
