import wtforms
from flask_wtf import FlaskForm

from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


class EditCriterionForm(FlaskForm):
    name = fields.PCStringField(
        "Nom",
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.Length(min=1, max=140, message="Doit contenir moins de %(max)d caractères"),
        ),
    )
    description = fields.PCStringField(
        "Description",
        validators=(
            wtforms.validators.Optional(""),
            wtforms.validators.Length(max=1024, message="Doit contenir moins de %(max)d caractères"),
        ),
    )

    start_date = fields.PCDateField("Date de début", validators=(wtforms.validators.Optional(),))
    end_date = fields.PCDateField("Date de fin", validators=(wtforms.validators.Optional(),))
    categories = fields.PCSelectMultipleField("Catégories", coerce=int)

    def validate_start_date(self, start_date: fields.PCDateField) -> fields.PCDateField:
        end_date = self._fields["end_date"]

        if (start_date.data and end_date.data) and (start_date.data > end_date.data):
            raise wtforms.ValidationError("ne peut pas être postérieure à celle de fin")

        return start_date


class CreateCriterionCategoryForm(FlaskForm):
    label = fields.PCOptStringField(
        "Libellé", validators=(wtforms.validators.Length(max=140, message="Doit contenir moins de %(max)d caractères"),)
    )


class SearchTagForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Tags offres et partenaires culturels")

    page = wtforms.HiddenField("page", default="1", validators=(wtforms.validators.Optional(),))
    per_page = fields.PCSelectField(
        "Par page",
        choices=(("10", "10"), ("25", "25"), ("50", "50"), ("100", "100")),
        default="100",
        validators=(wtforms.validators.Optional(),),
    )

    def is_empty(self) -> bool:
        return not any((self.q.data,))
