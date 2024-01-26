from datetime import date
from datetime import timedelta

from flask import flash
from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


class GetCustomReimbursementRulesListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Nom d'offre, ID offre")
    offerer = fields.PCTomSelectField(
        "Structures",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
    )
    venue = fields.PCTomSelectField(
        "Points de valorisation",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_venues",
    )
    limit = fields.PCSelectField(
        "Nombre maximum",
        choices=((25, "25"), (50, "50"), (100, "100")),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )
    categories = fields.PCSelectMultipleField(
        "Catégories",
        choices=utils.choices_from_enum(categories.CategoryIdLabelEnum),
        field_list_compatibility=True,
    )
    subcategories = fields.PCSelectMultipleField(
        "Sous-catégories", choices=[(s.id, s.pro_label) for s in subcategories_v2.ALL_SUBCATEGORIES]
    )

    def is_empty(self) -> bool:
        return not any(
            (
                self.q.data,
                self.offerer.data,
                self.venue.data,
                self.categories.data,
                self.subcategories.data,
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
        endpoint="backoffice_web.autocomplete_offerers",
    )
    venue = fields.PCTomSelectField(
        "Point de valorisation",
        multiple=False,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_pricing_points",
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

    def validate(self, extra_validators: dict | None = None) -> bool:
        offerer_id = self._fields["offerer"].data[0]
        venue_id = self._fields["venue"].data[0]
        print(offerer_id)
        print(venue_id)

        if not offerer_id and not venue_id:
            flash("Il faut obligatoirement renseigner une structure ou un lieu", "warning")
            return False

        if offerer_id and venue_id:
            flash("Un tarif dérogatoire ne peut pas concerner un lieu et une structure en même temps", "warning")
            return False
        return super().validate(extra_validators)


class EditCustomReimbursementRuleForm(FlaskForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    end_date = fields.PCDateField(
        "Date de fin d'application", validators=(wtforms.validators.InputRequired("obligatoire"),)
    )
