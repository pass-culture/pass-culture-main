from flask_wtf import FlaskForm
import wtforms

from pcapi.routes.backoffice_v3 import utils as bo_utils

from ..forms import fields


class SearchEanForm(FlaskForm):
    class Meta:
        csrf = False

    ean = fields.PCSearchField("EAN")

    def validate_ean(self, ean: fields.PCSearchField) -> fields.PCSearchField:
        if ean.data and not bo_utils.is_ean_valid(ean.data):
            raise wtforms.validators.ValidationError("La recherche ne correspond pas au format d'un EAN")
        ean.data = bo_utils.format_ean_or_visa(ean.data)
        return ean


class HiddenEanForm(FlaskForm):
    ean = fields.PCHiddenField("EAN")


class OfferCriteriaForm(HiddenEanForm):
    criteria = fields.PCTomSelectField(
        "Tags",
        multiple=True,
        choices=[],
        validate_choice=False,
        coerce=int,
        endpoint="backoffice_v3_web.autocomplete_criteria",
        validators=[
            wtforms.validators.DataRequired(),
        ],
    )
