import wtforms
from flask_wtf import FlaskForm
from wtforms import validators

from pcapi.utils import string as string_utils

from ..forms import fields


class SearchEanForm(FlaskForm):
    class Meta:
        csrf = False

    ean = fields.PCSearchField(
        "EAN-13",
        validators=[
            validators.DataRequired("L'EAN est obligatoire"),
            validators.Length(min=13, max=13, message="L'EAN doit faire exactement 13 chiffres"),
        ],
    )

    def validate_ean(self, ean: fields.PCSearchField) -> fields.PCSearchField:
        if ean.data:
            if not string_utils.is_ean_valid(ean.data):
                raise wtforms.validators.ValidationError("La recherche ne correspond pas au format d'un EAN-13")
            ean.data = string_utils.format_ean_or_visa(ean.data)
        return ean

    def is_empty(self) -> bool:
        return not any((self.ean.data,))


class OptionalCommentForm(FlaskForm):
    comment = fields.PCOptCommentField("Commentaire interne")
