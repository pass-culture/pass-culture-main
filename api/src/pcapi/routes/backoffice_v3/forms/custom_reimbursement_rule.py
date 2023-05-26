from datetime import date
from datetime import timedelta

from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import subcategories_v2

from . import fields


class GetCustomReimbursementRulesListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Nom d'offre, ID offre")
    offerer = fields.PCTomSelectField(
        "Structures",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_v3_web.autocomplete_offerers",
    )
    limit = fields.PCSelectField(
        "Nombre maximum",
        choices=((25, "25"), (50, "50"), (100, "100")),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )

    def is_empty(self) -> bool:
        return not any(
            (
                self.q.data,
                self.offerer.data,
            )
        )


class CreateCustomReimbursementRuleForm(FlaskForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    offerer = fields.PCTomSelectField(
        "Structure",
        multiple=False,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_v3_web.autocomplete_offerers",
        validators=[wtforms.validators.InputRequired("Information obligatoire")],
    )
    subcategories = fields.PCSelectMultipleField(
        "Sous-catégories", choices=[(s.id, s.pro_label) for s in subcategories_v2.ALL_SUBCATEGORIES]
    )

    rate = fields.PCDecimalField(
        "Taux de remboursement %",
        use_locale=True,
        validators=[
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.NumberRange(min=0, message="Doit contenir un nombre positif"),
            wtforms.validators.NumberRange(max=100, message="Doit contenir un nombre inférieur ou égal à 100"),
        ],
    )
    start_date = fields.PCDateField(
        "Date de début d'application",
        validators=[wtforms.validators.InputRequired("Information obligatoire")],
    )
    end_date = fields.PCDateField(
        "Date de fin d'application (optionnelle)", validators=(wtforms.validators.Optional(),)
    )

    def validate_start_date(self, start_date: fields.PCDateField) -> fields.PCDateField:
        start_date = start_date.data
        end_date = self._fields["end_date"].data

        if end_date and (start_date > end_date):
            raise wtforms.ValidationError("Ne peut pas être postérieure à la date de fin")

        if start_date < date.today() + timedelta(days=1):
            raise wtforms.ValidationError("Ne peut pas commencer avant demain")

        return start_date


class EditCustomReimbursementRuleForm(FlaskForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    end_date = fields.PCDateField(
        "Date de fin d'application", validators=(wtforms.validators.InputRequired("obligatoire"),)
    )
