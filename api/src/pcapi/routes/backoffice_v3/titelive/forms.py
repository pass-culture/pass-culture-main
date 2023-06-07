from flask_wtf import FlaskForm
import wtforms

from pcapi.routes.backoffice_v3 import utils as bo_utils

from ..forms import fields


class SearchEanForm(FlaskForm):
    class Meta:
        csrf = False

    ean = fields.PCSearchField("EAN-13")

    def validate_ean(self, ean: fields.PCSearchField) -> fields.PCSearchField:
        if ean.data:
            if not bo_utils.is_ean_valid(ean.data):
                raise wtforms.validators.ValidationError("La recherche ne correspond pas au format d'un EAN-13")
            ean.data = bo_utils.format_ean_or_visa(ean.data)
        return ean

    def is_empty(self) -> bool:
        return not any((self.ean.data,))


class OptionalCommentForm(FlaskForm):
    comment = fields.PCOptCommentField("Commentaire interne")
