from wtforms.fields import StringField
from wtforms.form import Form
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Regexp

from pcapi.admin.base_configuration import BaseAdminView


TAG_NAME_REGEX = r"^[^\s]+$"


class OffererTagView(BaseAdminView):
    can_create = True
    can_edit = False  # Nothing to edit
    can_delete = True
    column_list = ["id", "name"]
    column_labels = {"name": "Nom"}
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
        return form
