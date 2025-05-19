import typing

import wtforms
from flask_wtf import FlaskForm

from pcapi.core.categories import pro_categories
from pcapi.core.categories import subcategories

from ..forms import fields
from ..forms import utils


class SearchRuleForm(FlaskForm):
    class Meta:
        csrf = False

    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(pro_categories.CategoryIdLabelEnum)
    )
    subcategory = fields.PCSelectMultipleField(
        "Sous-catégories",
        choices=sorted(
            [(s.id, s.pro_label) for s in subcategories.ALL_SUBCATEGORIES if not s.is_event], key=lambda x: x[1]
        ),
    )


class EditOfferPriceLimitationRuleForm(FlaskForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    rate = fields.PCDecimalField(
        "Limite de modification du prix %",
        use_locale=True,
        validators=[
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.NumberRange(
                min=0, max=999, message="La limite de modification de prix doit être un nombre entre 0 et 999 %%"
            ),
        ],
    )


class CreateOfferPriceLimitationRuleForm(EditOfferPriceLimitationRuleForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    subcategory = fields.PCSelectField(
        "Sous-catégorie",
        choices=sorted(
            [(s.id, s.pro_label) for s in subcategories.ALL_SUBCATEGORIES if not s.is_event], key=lambda x: x[1]
        ),
    )

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._fields.move_to_end("subcategory", last=False)
