import enum
import re
import typing

import wtforms

from pcapi.models.feature import FeatureToggle
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import search as search_forms
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


class ProSearchForm(search_forms.SearchForm):
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

    # We can't use exclude_opts in pro_type definition because choices would not be updated when changing the value of
    # WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY. This init function can be removed at the same time as the feature flag.
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        if not FeatureToggle.WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY.is_active():
            self.pro_type.choices = [
                choice for choice in self.pro_type.choices if choice[0] != TypeOptions.BANK_ACCOUNT.name
            ]


class CompactProSearchForm(ProSearchForm):
    # Compact form on top of search results and details pages
    departments = fields.PCSelectMultipleField("Départements", choices=area_choices, search_inline=True)
