from flask_wtf import FlaskForm
import wtforms

from pcapi.routes.backoffice_v3 import utils as bo_utils

from ..forms import fields


class SearchIsbnForm(FlaskForm):
    class Meta:
        csrf = False

    isbn = fields.PCSearchField("ISBN")

    def validate_isbn(self, isbn: fields.PCSearchField) -> fields.PCSearchField:
        if isbn.data and not bo_utils.is_isbn_valid(isbn.data):
            raise wtforms.validators.ValidationError("La recherche ne correspond pas au format d'un ISBN")
        isbn.data = bo_utils.format_isbn_or_visa(isbn.data)
        return isbn


class HiddenIsbnForm(FlaskForm):
    isbn = fields.PCHiddenField("ISBN")


class OfferCriteriaForm(HiddenIsbnForm):
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
