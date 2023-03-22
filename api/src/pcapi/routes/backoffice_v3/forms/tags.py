from flask_wtf import FlaskForm
import wtforms

from . import fields


TAG_NAME_REGEX = r"^[^\s]+$"


class EditTagForm(FlaskForm):
    name = fields.PCStringField(
        "Nom",
        validators=(
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.Length(min=1, max=140, message="Doit contenir moins de %(max)d caractères"),
            wtforms.validators.Regexp(TAG_NAME_REGEX, message="Le nom ne doit contenir aucun caractère d'espacement"),
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

    def validate_start_date(self, start_date: fields.PCDateField) -> fields.PCDateField:
        end_date = self._fields["end_date"]

        if (start_date.data and end_date.data) and (start_date.data > end_date.data):
            raise wtforms.ValidationError("ne peut pas être postérieure à celle de fin")

        return start_date
