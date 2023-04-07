from flask_wtf import FlaskForm
import wtforms

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
