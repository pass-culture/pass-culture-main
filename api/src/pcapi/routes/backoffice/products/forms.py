import enum
import re

import wtforms
from flask_wtf import FlaskForm

from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


class BatchLinkOfferToProductForm(empty_forms.BatchForm):
    pass


class ProductFilterTypeEnum(enum.Enum):
    EAN = "ean"
    VISA = "visa"
    ALLOCINE_ID = "allocine-id"


def format_search_product_filter(type_option: ProductFilterTypeEnum) -> str:
    match type_option:
        case ProductFilterTypeEnum.EAN:
            return "EAN"
        case ProductFilterTypeEnum.VISA:
            return "Visa"
        case ProductFilterTypeEnum.ALLOCINE_ID:
            return "Allocine ID"
        case _:
            return type_option.value


DIGITS_AND_WHITESPACES_REGEX = re.compile(r"^[\d\s]+$")


class ProductSearchForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCSearchField(label="")
    product_filter_type = fields.PCSelectField(
        "Type",
        choices=utils.choices_from_enum(ProductFilterTypeEnum, format_search_product_filter),
        default=ProductFilterTypeEnum.EAN,
    )

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data and "%" in q.data:
            raise wtforms.validators.ValidationError("Le caractère % n'est pas autorisé")
        return q

    def filter_q(self, q: str | None) -> str | None:
        # Remove spaces from EAN, VISA, Allocine ID
        if q and DIGITS_AND_WHITESPACES_REGEX.match(q):
            return re.sub(r"\s+", "", q)
        return q

    def validate_product_type(self, product_filter_type: fields.PCSelectField) -> fields.PCSelectField:
        try:
            product_filter_type.data = ProductFilterTypeEnum[product_filter_type.data]
        except KeyError:
            raise wtforms.validators.ValidationError("Le type sélectionné est invalide")
        return product_filter_type


class OptionalCommentForm(FlaskForm):
    comment = fields.PCOptCommentField("Commentaire interne")
