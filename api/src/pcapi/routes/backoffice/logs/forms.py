import enum
import json
import typing

import wtforms
from flask import flash

from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils as forms_utils
from pcapi.routes.backoffice.utils import advanced_search


class LogsSearchAttribute(enum.Enum):
    LOG_DATE = "Date du log"
    BOOKING = "ID de la réservation"
    OFFER = "ID de l'offre"
    PRODUCT = "ID du produit"
    PROVIDER = "Partenaire technique"
    STOCK = "ID du stock"
    USER = "ID de l'utilisateur"
    VENUE = "Partenaire culturel"


class LogSearchType(enum.StrEnum):
    OFFER_CREATION = "Création d'offres"
    BOOKING = "Création de réservation"
    CANCEL_BOOKING = "Annulation de réservation"
    USER_LOGIN = "Connexion d'un utilisateur"


operator_no_require_value = ["NOT_EXIST"]
form_field_configuration = {
    "LOG_DATE": {"field": "datetime", "operator": ["GREATER_THAN_OR_EQUAL_TO", "LESS_THAN"]},
    "BOOKING": {"field": "integer", "operator": ["EQUALS"]},
    "OFFER": {"field": "integer", "operator": ["EQUALS"]},
    "PRODUCT": {"field": "integer", "operator": ["EQUALS"]},
    "PROVIDER": {"field": "providers", "operator": ["IN"]},
    "STOCK": {"field": "integer", "operator": ["EQUALS"]},
    "USER": {"field": "integer", "operator": ["EQUALS"]},
    "VENUE": {"field": "venues", "operator": ["IN"]},
}


class LogsAdvancedSearchSubForm(forms_utils.PCForm):
    class Meta:
        csrf = False

    json_data = json.dumps(
        {
            "display_configuration": form_field_configuration,
            "all_available_fields": [
                "datetime",
                "integer",
                "providers",
                "venues",
            ],
            "sub_rule_type_field_name": "search_field",
            "operator_field_name": "operator",
        }
    )

    def __init__(self, *args: list, **kwargs: dict):
        super().__init__(*args, **kwargs)
        autocomplete.prefill_providers_choices(self.providers)
        autocomplete.prefill_venues_choices(self.venues)

    search_field = fields.PCSelectWithPlaceholderValueField(
        "Champ de recherche",
        choices=forms_utils.choices_from_enum(LogsSearchAttribute, sort=True),
        validators=[
            wtforms.validators.Optional(""),
        ],
    )
    operator = fields.PCSelectField(
        "Opérateur",
        choices=forms_utils.choices_from_enum(advanced_search.AdvancedSearchOperators),
        default=advanced_search.AdvancedSearchOperators.EQUALS,  # avoids empty option
        validators=[
            wtforms.validators.Optional(""),
        ],
    )

    integer = fields.PCOptIntegerField(
        "Valeur numérique",
        validators=[
            wtforms.validators.Optional(""),
            wtforms.validators.NumberRange(min=0, max=(2**63) - 1, message="Doit être inférieur à %(max)d"),
        ],
    )

    datetime = fields.PCDateTimeField(
        "Date et heure",
        seconds=True,
        validators=[
            wtforms.validators.Optional(""),
        ],
    )

    providers = fields.PCTomSelectField(
        "Partenaires techniques",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice.autocomplete_providers",
        search_inline=True,
        field_list_compatibility=True,
    )

    venues = fields.PCTomSelectField(
        "Partenaires culturels",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice.autocomplete_venues",
        search_inline=True,
        field_list_compatibility=True,
    )


class SearchForm(forms_utils.PCForm):
    class Meta:
        csrf = False

    method = "GET"

    search_type = fields.PCSelectField(
        "Type de logs",
        choices=forms_utils.choices_from_enum(LogSearchType),
        default=LogSearchType.OFFER_CREATION.name,  # avoids empty option
        validators=[wtforms.validators.Optional("Information obligatoire")],
    )

    search = fields.PCFieldListField(
        fields.PCFormField(LogsAdvancedSearchSubForm),
        label="recherches",
        min_entries=1,
    )

    @staticmethod
    def is_sub_search_empty(sub_search: dict[str, typing.Any]) -> bool:
        field_name = sub_search.get("search_field")
        operator = sub_search.get("operator")
        if field_name:
            field_attribute_name = form_field_configuration.get(field_name, {}).get("field", "")
            field_data = sub_search.get(field_attribute_name)  # type: ignore[call-overload]
            if field_data not in (None, []):
                return False
            if operator in operator_no_require_value:
                return False
        return True

    @staticmethod
    def is_search_empty(search_data: list[dict[str, typing.Any]]) -> bool:
        for sub_search in search_data:
            if not SearchForm.is_sub_search_empty(sub_search):
                return False
        return True

    def validate(self, extra_validators: dict | None = None) -> bool:
        errors = []

        for sub_search in self.search.data:
            if search_field := sub_search.get("search_field"):
                if SearchForm.is_sub_search_empty(sub_search):
                    try:
                        errors.append(f"Le filtre « {LogsSearchAttribute[search_field].value} » est vide.")
                    except KeyError:
                        errors.append(f"Le filtre {search_field} est invalide.")
                else:
                    operator = sub_search.get("operator")
                    if operator not in form_field_configuration.get(search_field, {}).get("operator", []):
                        try:
                            errors.append(
                                f"L'opérateur « {advanced_search.AdvancedSearchOperators[operator].value} » n'est pas supporté par le filtre {LogsSearchAttribute[search_field].value}."
                            )
                        except KeyError:
                            errors.append(f"L'opérateur {operator} n'est pas supporté par le filtre {search_field}.")

        if errors:
            flash("\n".join(errors), "warning")
            return False

        return super().validate(extra_validators)
