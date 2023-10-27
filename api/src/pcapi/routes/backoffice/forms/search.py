import enum
import re

import wtforms

from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.forms.constants import area_choices


DIGITS_AND_WHITESPACES_REGEX = re.compile(r"^[\d\s]+$")


class TypeOptions(enum.Enum):
    OFFERER = "offerer"
    VENUE = "venue"
    USER = "user"
    BANK_ACCOUNT = "bank-account"


def format_search_type_options(type_option: TypeOptions) -> str:
    match type_option:
        case TypeOptions.OFFERER:
            return "Structure"
        case TypeOptions.VENUE:
            return "Lieu"
        case TypeOptions.USER:
            return "Compte pro"
        case TypeOptions.BANK_ACCOUNT:
            return "Compte bancaire"
        case _:
            return type_option.value


class SearchForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCSearchField(label="")
    page = fields.PCOptHiddenIntegerField("page", default=1, validators=[wtforms.validators.Optional()])
    per_page = fields.PCOptHiddenIntegerField("per_page", default=20, validators=[wtforms.validators.Optional()])

    def validate_q(self, q: fields.PCOptSearchField) -> fields.PCOptSearchField:
        if q.data and "%" in q.data:
            raise wtforms.validators.ValidationError("Le caractère % n'est pas autorisé")
        return q


class ProSearchForm(SearchForm):
    pro_type = fields.PCSelectField(
        "Type",
        choices=utils.choices_from_enum(TypeOptions, format_search_type_options),
        default=TypeOptions.OFFERER,
    )
    departments = fields.PCSelectMultipleField("Départements", choices=area_choices, full_row=True)

    def filter_q(self, q: str | None) -> str | None:
        # Remove spaces from SIREN, SIRET and IDs
        if q and DIGITS_AND_WHITESPACES_REGEX.match(q):
            return re.sub(r"\s+", "", q)
        return q

    def validate_pro_type(self, pro_type: fields.PCSelectField) -> fields.PCSelectField:
        try:
            pro_type.data = TypeOptions[pro_type.data]
        except KeyError:
            raise wtforms.validators.ValidationError("Le type sélectionné est invalide")
        return pro_type


class CompactProSearchForm(ProSearchForm):
    # Compact form on top of search results and details pages
    departments = fields.PCSelectMultipleField("Départements", choices=area_choices, search_inline=True)
