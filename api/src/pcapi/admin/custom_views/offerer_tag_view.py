import typing

from jinja2.runtime import Context
from wtforms.fields import StringField
from wtforms.form import Form
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Regexp

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import tag_categories


TAG_NAME_REGEX = r"^[^\s]+$"


def category_formatter(view: BaseAdminView, context: Context, model: offerers_models.OffererTag, name: str) -> str:
    if model.categoryId is None:
        return ""
    return tag_categories.ALL_OFFERER_TAG_CATEGORIES_DICT[model.categoryId].label


class OffererTagView(BaseAdminView):
    can_create = True
    can_edit = True
    can_delete = True
    column_list = ["id", "name", "label", "description", "categoryId"]
    column_labels = {"name": "Nom", "label": "Libellé", "description": "Description", "categoryId": "Catégorie"}
    column_searchable_list = ["name"]
    column_filters: list[str] = []

    form_choices = {
        "categoryId": [(category.id, category.label) for category in tag_categories.ALL_OFFERER_TAG_CATEGORIES]
    }

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
        form.description = StringField("Description")
        return form

    @property
    def column_formatters(self) -> dict[str, typing.Callable]:
        formatters = super().column_formatters
        formatters["categoryId"] = category_formatter
        return formatters
