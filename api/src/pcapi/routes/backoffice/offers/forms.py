import enum
from functools import partial
import json
import typing
from urllib.parse import urlencode

from flask import flash
from flask import url_for
from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import models as offerers_models
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import constants
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


class SearchOperators(enum.Enum):
    NOT_EQUALS = "est différent de"
    EQUALS = "est égal à"
    NAME_NOT_EQUALS = "est différent de\0\0"
    NAME_EQUALS = "est égal à\0\0"
    STR_NOT_EQUALS = "est différent de\0"  # the \0 is here to force wtforms to display NOT_EQUALS and STR_NOT_EQUALS
    STR_EQUALS = "est égal à\0"  # the \0 is here to force wtforms to display EQUALS and STR_EQUALS
    GREATER_THAN = "supérieur strict"
    GREATER_THAN_OR_EQUAL_TO = "supérieur ou égal"
    LESS_THAN = "inférieur strict"
    LESS_THAN_OR_EQUAL_TO = "inférieur ou égal"
    IN = "est parmi"
    NOT_IN = "n'est pas parmi"
    CONTAINS = "contient"
    NO_CONTAINS = "ne contient pas"
    NOT_EXIST = "n'a aucun"


class SearchAttributes(enum.Enum):
    CATEGORY = "Catégorie"
    SUBCATEGORY = "Sous-catégorie"
    CREATION_DATE = "Date de création"
    EVENT_DATE = "Date de l'évènement"
    BOOKING_LIMIT_DATE = "Date limite de réservation"
    DEPARTMENT = "Département"
    EAN = "EAN-13"
    VALIDATION = "État"
    ID = "ID de l'offre"
    VENUE = "Lieu"
    NAME = "Nom de l'offre"
    STATUS = "Statut"
    OFFERER = "Structure"
    TAG = "Tag"
    VISA = "Visa d'exploitation"


operator_no_require_value = ["NOT_EXIST"]

form_field_configuration = {
    "CATEGORY": {"field": "category", "operator": ["IN", "NOT_IN"]},
    "CREATION_DATE": {
        "field": "date",
        "operator": [
            "GREATER_THAN_OR_EQUAL_TO",
            "LESS_THAN",
        ],
    },
    "DEPARTMENT": {"field": "department", "operator": ["IN", "NOT_IN"]},
    "EAN": {"field": "string", "operator": ["CONTAINS", "NO_CONTAINS", "STR_EQUALS", "STR_NOT_EQUALS"]},
    "EVENT_DATE": {
        "field": "date",
        "operator": [
            "GREATER_THAN_OR_EQUAL_TO",
            "LESS_THAN",
        ],
    },
    "BOOKING_LIMIT_DATE": {
        "field": "date",
        "operator": [
            "GREATER_THAN_OR_EQUAL_TO",
            "LESS_THAN",
        ],
    },
    "ID": {"field": "integer", "operator": ["EQUALS", "NOT_EQUALS"]},
    "NAME": {"field": "string", "operator": ["CONTAINS", "NO_CONTAINS", "NAME_EQUALS", "NAME_NOT_EQUALS"]},
    "OFFERER": {"field": "offerer", "operator": ["IN", "NOT_IN"]},
    "STATUS": {"field": "status", "operator": ["IN", "NOT_IN"]},
    "SUBCATEGORY": {"field": "subcategory", "operator": ["IN", "NOT_IN"]},
    "TAG": {"field": "criteria", "operator": ["IN", "NOT_IN", "NOT_EXIST"]},
    "VENUE": {"field": "venue", "operator": ["IN", "NOT_IN"]},
    "VALIDATION": {"field": "validation", "operator": ["IN", "NOT_IN"]},
    "VISA": {"field": "string", "operator": ["CONTAINS", "NO_CONTAINS", "STR_EQUALS", "STR_NOT_EQUALS"]},
}


class GetOffersBaseFields(utils.PCForm):
    sort = wtforms.HiddenField(
        "sort", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("id", "dateCreated")))
    )
    order = wtforms.HiddenField(
        "order", default="asc", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("asc", "desc")))
    )
    limit = fields.PCSelectField(
        "Nombre maximum de résultats",
        choices=((100, "100"), (500, "500"), (1000, "1000"), (3000, "3000")),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )

    def get_sort_link(self, endpoint: str) -> str:
        form_url = partial(url_for, endpoint, **self.raw_data)
        return form_url(
            sort="dateCreated", order="asc" if self.sort.data == "dateCreated" and self.order.data == "desc" else "desc"
        )

    def is_empty(self) -> bool:
        # needed to clean multiple inheritances
        return True


class OfferAdvancedSearchSubForm(utils.PCForm):
    class Meta:
        csrf = False

    json_data = json.dumps(
        {
            "display_configuration": form_field_configuration,
            "all_available_fields": [
                "category",
                "criteria",
                "date",
                "department",
                "integer",
                "offerer",
                "string",
                "status",
                "subcategory",
                "venue",
                "validation",
            ],
            "sub_rule_type_field_name": "search_field",
            "operator_field_name": "operator",
        }
    )

    def __init__(self, *args: list, **kwargs: dict):
        super().__init__(*args, **kwargs)
        autocomplete.prefill_criteria_choices(self.criteria)
        autocomplete.prefill_offerers_choices(self.offerer)
        autocomplete.prefill_venues_choices(self.venue)

    search_field = fields.PCSelectWithPlaceholderValueField(
        "Champ de recherche",
        choices=utils.choices_from_enum(SearchAttributes),
        validators=[
            wtforms.validators.Optional(""),
        ],
    )
    operator = fields.PCSelectWithPlaceholderValueField(
        "Opérateur",
        choices=utils.choices_from_enum(SearchOperators),
        validators=[
            wtforms.validators.Optional(""),
        ],
    )
    category = fields.PCSelectMultipleField(
        "Catégories",
        choices=utils.choices_from_enum(categories.CategoryIdLabelEnum),
        search_inline=True,
        field_list_compatibility=True,
    )
    subcategory = fields.PCSelectMultipleField(
        "Sous-catégories",
        choices=utils.choices_from_enum(subcategories.SubcategoryProLabelEnumv2),
        search_inline=True,
        field_list_compatibility=True,
    )
    criteria = fields.PCTomSelectField(
        "Tags",
        multiple=True,
        choices=[],
        coerce=int,
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_criteria",
        search_inline=True,
        field_list_compatibility=True,
    )
    department = fields.PCSelectMultipleField(
        "Départements",
        choices=constants.area_choices,
        search_inline=True,
        field_list_compatibility=True,
    )
    integer = fields.PCOptIntegerField(
        "Valeur numérique",
        validators=[
            wtforms.validators.Optional(""),
            wtforms.validators.NumberRange(min=0, max=(2**63) - 1, message="Doit être inférieur à %(max)d"),
        ],
    )
    offerer = fields.PCTomSelectField(
        "Structures",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
        search_inline=True,
        field_list_compatibility=True,
    )
    string = fields.PCOptStringField(
        "Text",
        validators=[
            wtforms.validators.Length(max=256, message="Doit contenir moins de %(max)d caractères"),
        ],
    )
    venue = fields.PCTomSelectField(
        "Lieux",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_venues",
        search_inline=True,
        field_list_compatibility=True,
    )
    date = fields.PCDateField(
        validators=[
            wtforms.validators.Optional(""),
        ]
    )
    validation = fields.PCSelectMultipleField(
        "États",
        choices=utils.choices_from_enum(
            OfferValidationStatus,
            formatter=filters.format_offer_validation_status,
        ),
        search_inline=True,
        field_list_compatibility=True,
    )
    status = fields.PCSelectMultipleField(
        "Statut",
        choices=utils.choices_from_enum(
            OfferStatus,
            formatter=filters.format_offer_status,
        ),
        search_inline=True,
        field_list_compatibility=True,
    )


class GetOfferAdvancedSearchForm(GetOffersBaseFields):
    class Meta:
        csrf = False

    method = "GET"
    only_validated_offerers = fields.PCSwitchBooleanField(
        "Uniquement les offres des structures validées", full_row=True
    )
    search = fields.PCFieldListField(
        fields.PCFormField(OfferAdvancedSearchSubForm),
        label="recherches",
        min_entries=1,
    )

    def is_empty(self) -> bool:
        empty = not self.only_validated_offerers.data
        empty = empty and GetOfferAdvancedSearchForm.is_search_empty(self.search.data)
        return empty and super().is_empty()

    @staticmethod
    def is_sub_search_empty(sub_search: dict[str, typing.Any]) -> bool:
        field_name = sub_search.get("search_field")
        operator = sub_search.get("operator")
        if field_name:
            field_attribute_name = form_field_configuration.get(field_name, {}).get("field", "")
            field_data = sub_search.get(field_attribute_name)  # type: ignore [call-overload]
            if field_data:
                return False
            if operator in operator_no_require_value:
                return False
        return True

    @staticmethod
    def is_search_empty(search_data: list[dict[str, typing.Any]]) -> bool:
        for sub_search in search_data:
            if not GetOfferAdvancedSearchForm.is_sub_search_empty(sub_search):
                return False
        return True

    def get_sort_link_with_search_data(self, endpoint: str) -> str:
        search_data = {}
        for i, sub_form in enumerate(self.search):
            prefix = f"search-{i}-"
            for field_name, field_value in sub_form.data.items():
                if field_value:
                    search_data[f"{prefix}{field_name}"] = field_value

        encoded_search_data = urlencode(search_data, doseq=True)

        base_url = self.get_sort_link(endpoint)

        return f"{base_url}&{encoded_search_data}" if encoded_search_data else f"{base_url}"

    def validate(self, extra_validators: dict | None = None) -> bool:
        errors = []

        for sub_search in self.search.data:
            if search_field := sub_search.get("search_field"):
                if GetOfferAdvancedSearchForm.is_sub_search_empty(sub_search):
                    try:
                        errors.append(f"Le filtre « {SearchAttributes[search_field].value} » est vide.")
                    except KeyError:
                        errors.append(f"Le filtre {search_field} est invalide.")

        if errors:
            flash("\n".join(errors), "warning")
            return False

        return super().validate(extra_validators)


class GetOffersSearchForm(GetOffersBaseFields):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID de l'offre ou liste d'ID, nom, EAN-13, visa d'exploitation")
    category = fields.PCSelectMultipleField(
        "Catégories",
        choices=utils.choices_from_enum(categories.CategoryIdLabelEnum),
        search_inline=True,
    )
    offerer = fields.PCTomSelectField(
        "Structures",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
        search_inline=True,
    )
    status = fields.PCSelectMultipleField(
        "États",
        choices=utils.choices_from_enum(OfferValidationStatus, formatter=filters.format_offer_validation_status),
        search_inline=True,
    )

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._fields.move_to_end("q", last=False)
        self._fields.move_to_end("category")
        self._fields.move_to_end("offerer")
        self._fields.move_to_end("status")
        self._fields.move_to_end("limit")
        autocomplete.prefill_offerers_choices(self.offerer)

    def is_empty(self) -> bool:
        empty = not any(
            (
                self.q.data,
                self.category.data,
                self.offerer.data,
                self.status.data,
            )
        )
        return empty and super().is_empty()


class InternalSearchForm(GetOffersSearchForm, GetOfferAdvancedSearchForm):
    """concat of GetOffersSearchForm and GetOfferAdvancedSearchForm. this form is never displayed bit it is the one
    used to display the list of individual offers"""

    class Meta:
        csrf = False


class EditOfferForm(FlaskForm):
    criteria = fields.PCTomSelectField(
        "Tags", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_web.autocomplete_criteria"
    )
    rankingWeight = fields.PCOptIntegerField("Pondération")


class BatchEditOfferForm(empty_forms.BatchForm, EditOfferForm):
    pass


class EditOfferVenueForm(FlaskForm):
    venue = fields.PCSelectWithPlaceholderValueField("Nouveau lieu", choices=[], validate_choice=False)
    notify_beneficiary = fields.PCSwitchBooleanField("Notifier les jeunes", full_row=True)

    def set_venue_choices(self, venues: list[offerers_models.Venue]) -> None:
        self.venue.choices = [(venue.id, venue.name) for venue in venues]


class EditStockForm(FlaskForm):
    price = fields.PCDecimalField(
        "Prix",
        validators=[
            wtforms.validators.NumberRange(min=0, max=300, message="Le prix doit être positif et inférieur à 300 €.")
        ],
    )
