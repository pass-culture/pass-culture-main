import enum
from functools import partial
import json
import re
import typing
from urllib.parse import urlencode

from flask import flash
from flask import url_for
from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import models as offerers_models
from pcapi.domain import show_types
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import constants
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils as forms_utils
from pcapi.utils import string as string_utils


class IndividualOffersSearchAttributes(enum.Enum):
    CATEGORY = "Catégorie"
    SUBCATEGORY = "Sous-catégorie"
    CREATION_DATE = "Date de création"
    EVENT_DATE = "Date de l'évènement"
    BOOKING_LIMIT_DATE = "Date limite de réservation"
    DEPARTMENT = "Département"
    REGION = "Région"
    EAN = "EAN-13"
    VALIDATION = "État"
    ID = "ID de l'offre"
    VENUE = "Lieu"
    ADDRESS = "Adresse de l'offre"
    NAME = "Nom de l'offre"
    SYNCHRONIZED = "Offre synchronisée"
    PRICE = "Prix"
    PROVIDER = "Fournisseur"
    STATUS = "Statut"
    OFFERER = "Structure"
    TAG = "Tag"
    MUSIC_TYPE_GTL = "Type de musique"
    SHOW_TYPE = "Type de spectacle"
    SHOW_SUB_TYPE = "Sous-type de spectacle"
    VISA = "Visa d'exploitation"


operator_no_require_value = ["NOT_EXIST"]

form_field_configuration = {
    "ADDRESS": {"field": "address", "operator": ["IN", "NOT_IN"]},
    "CATEGORY": {"field": "category", "operator": ["IN", "NOT_IN"]},
    "CREATION_DATE": {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    "DEPARTMENT": {"field": "department", "operator": ["IN", "NOT_IN"]},
    "REGION": {"field": "region", "operator": ["IN", "NOT_IN"]},
    "EAN": {"field": "string", "operator": ["EQUALS", "NOT_EQUALS"]},
    "EVENT_DATE": {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    "BOOKING_LIMIT_DATE": {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    "ID": {"field": "string", "operator": ["IN", "NOT_IN"]},
    "NAME": {"field": "string", "operator": ["CONTAINS", "NO_CONTAINS", "NAME_EQUALS", "NAME_NOT_EQUALS"]},
    "OFFERER": {"field": "offerer", "operator": ["IN", "NOT_IN"]},
    "STATUS": {"field": "status", "operator": ["IN", "NOT_IN"]},
    "SUBCATEGORY": {"field": "subcategory", "operator": ["IN", "NOT_IN"]},
    "TAG": {"field": "criteria", "operator": ["IN", "NOT_IN", "NOT_EXIST"]},
    "VENUE": {"field": "venue", "operator": ["IN", "NOT_IN"]},
    "VALIDATION": {"field": "validation", "operator": ["IN", "NOT_IN"]},
    "VISA": {"field": "string", "operator": ["EQUALS", "NOT_EQUALS"]},
    "MUSIC_TYPE_GTL": {"field": "music_type_gtl", "operator": ["IN", "NOT_IN"]},
    "SHOW_TYPE": {"field": "show_type", "operator": ["IN", "NOT_IN"]},
    "SHOW_SUB_TYPE": {"field": "show_sub_type", "operator": ["IN", "NOT_IN"]},
    "PRICE": {
        "field": "price",
        "operator": [
            "EQUALS",
            "GREATER_THAN_OR_EQUAL_TO",
            "LESS_THAN",
        ],
    },
    "SYNCHRONIZED": {"field": "boolean", "operator": ["NULLABLE"]},
    "PROVIDER": {"field": "provider", "operator": ["IN", "NOT_IN"]},
}


class GetOffersBaseFields(forms_utils.PCForm):
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


class OfferAdvancedSearchSubForm(forms_utils.PCForm):
    class Meta:
        csrf = False
        locales = ["fr_FR", "fr"]

    json_data = json.dumps(
        {
            "display_configuration": form_field_configuration,
            "all_available_fields": [
                "address",
                "category",
                "criteria",
                "date",
                "department",
                "region",
                "integer",
                "offerer",
                "string",
                "status",
                "subcategory",
                "venue",
                "validation",
                "music_type_gtl",
                "show_type",
                "show_sub_type",
                "price",
                "boolean",
                "provider",
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
        autocomplete.prefill_addresses_choices(self.address)
        autocomplete.prefill_providers_choices(self.provider)

    search_field = fields.PCSelectWithPlaceholderValueField(
        "Champ de recherche",
        choices=forms_utils.choices_from_enum(IndividualOffersSearchAttributes),
        validators=[
            wtforms.validators.Optional(""),
        ],
    )
    operator = fields.PCSelectField(
        "Opérateur",
        choices=forms_utils.choices_from_enum(utils.AdvancedSearchOperators),
        default=utils.AdvancedSearchOperators.EQUALS,  # avoids empty option
        validators=[
            wtforms.validators.Optional(""),
        ],
    )
    boolean = fields.PCSelectField(
        choices=(("true", "Oui"), ("false", "Non")),
        default="true",
        validators=[
            wtforms.validators.Optional(""),
        ],
    )
    category = fields.PCSelectMultipleField(
        "Catégories",
        choices=forms_utils.choices_from_enum(categories.CategoryIdLabelEnum),
        search_inline=True,
        field_list_compatibility=True,
    )
    subcategory = fields.PCSelectMultipleField(
        "Sous-catégories",
        choices=forms_utils.choices_from_enum(subcategories.SubcategoryProLabelEnumv2),
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
    region = fields.PCSelectMultipleField(
        "Régions",
        choices=utils.get_regions_choices(),
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
    price = fields.PCDecimalField(
        "Prix",
        use_locale=True,
        validators=[
            wtforms.validators.Optional(""),
            wtforms.validators.NumberRange(min=0, message="Doit contenir un nombre positif"),
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
        "Texte",
        validators=[
            wtforms.validators.Length(max=4096, message="Doit contenir moins de %(max)d caractères"),
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
    address = fields.PCTomSelectField(
        "Adresses (autocomplétion expérimentale)",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_addresses",
        search_inline=True,
        field_list_compatibility=True,
    )
    provider = fields.PCTomSelectField(
        "Providers",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_providers",
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
        choices=forms_utils.choices_from_enum(
            OfferValidationStatus,
            formatter=filters.format_offer_validation_status,
        ),
        search_inline=True,
        field_list_compatibility=True,
    )
    status = fields.PCSelectMultipleField(
        "Statut",
        choices=forms_utils.choices_from_enum(
            OfferStatus,
            formatter=filters.format_offer_status,
        ),
        search_inline=True,
        field_list_compatibility=True,
    )
    music_type_gtl = fields.PCSelectMultipleField(
        "Type de musique",
        choices=[(s.gtl_id[:2], s.label) for s in categories.TITELIVE_MUSIC_TYPES],
        search_inline=True,
        field_list_compatibility=True,
    )
    show_type = fields.PCSelectMultipleField(
        "Type de spectacle",
        choices=[(str(s), show_types.SHOW_TYPES_LABEL_BY_CODE[s]) for s in show_types.SHOW_TYPES_LABEL_BY_CODE],
        search_inline=True,
        field_list_compatibility=True,
    )
    show_sub_type = fields.PCSelectMultipleField(
        "Sous-type de spectacle",
        choices=[(str(s), show_types.SHOW_SUB_TYPES_LABEL_BY_CODE[s]) for s in show_types.SHOW_SUB_TYPES_LABEL_BY_CODE],
        search_inline=True,
        field_list_compatibility=True,
    )

    def validate_string(self, string: fields.PCStringField) -> fields.PCStringField:
        if string.data:
            search_field = self._fields["search_field"].data

            if search_field == "ID" and not re.match(r"^[\d\s,;]+$", string.data):
                raise wtforms.validators.ValidationError("La liste d'ID n'est pas valide")
            if search_field == "EAN":
                if not string_utils.is_ean_valid(string.data):
                    raise wtforms.validators.ValidationError("La recherche ne correspond pas au format d'un EAN-13")
                string.data = string_utils.format_ean_or_visa(string.data)
            elif search_field == "VISA":
                if not string_utils.is_visa_valid(string.data):
                    raise wtforms.validators.ValidationError("La recherche ne correspond pas au format d'un VISA")
                string.data = string_utils.format_ean_or_visa(string.data)

        return string


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
            field_data = sub_search.get(field_attribute_name)  # type: ignore[call-overload]
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
                        errors.append(f"Le filtre « {IndividualOffersSearchAttributes[search_field].value} » est vide.")
                    except KeyError:
                        errors.append(f"Le filtre {search_field} est invalide.")

        if errors:
            flash("\n".join(errors), "warning")
            return False

        return super().validate(extra_validators)


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
        self.venue.choices = [
            (venue.id, f"{venue.common_name} ({venue.siret if venue.siret else 'Pas de SIRET'})") for venue in venues
        ]


class EditStockForm(FlaskForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    price = fields.PCDecimalField(
        "Prix",
        use_locale=True,
        validators=[
            wtforms.validators.NumberRange(min=0, max=300, message="Le prix doit être positif et inférieur à 300 €.")
        ],
    )
