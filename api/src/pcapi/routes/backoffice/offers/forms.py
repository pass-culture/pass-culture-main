import decimal
import enum
import json
import re
import typing
from functools import partial
from urllib.parse import urlencode

import wtforms
from flask import flash
from flask import url_for
from flask_wtf import FlaskForm

from pcapi.core.categories import pro_categories
from pcapi.core.categories import subcategories
from pcapi.core.categories.genres import show
from pcapi.core.offerers import models as offerers_models
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
    DEPARTMENT = "Département de l'offre"
    REGION = "Région de l'offre"
    EAN = "EAN-13"
    VALIDATION = "État"
    ID = "ID de l'offre"
    PRODUCT = "ID d'une offre sur le même produit"
    MEDIATION = "Image"
    VENUE = "Partenaire culturel"
    VENUE_TYPE = "Activité principale du partenaire"
    ADDRESS = "Adresse de l'offre"
    NAME = "Nom de l'offre"
    SYNCHRONIZED = "Offre synchronisée"
    PRICE = "Prix"
    PROVIDER = "Fournisseur"
    STATUS = "Statut"
    OFFERER = "Entité juridique"
    TAG = "Tag"
    VENUE_TAG = "Tag sur le partenaire culturel"
    OFFERER_TAG = "Tag sur l'entité juridique"
    HEADLINE = "Offres à la une"
    HIGHLIGHT_REQUEST = "Valorisation thématique (demande de participation)"
    VALIDATED_OFFERER = "Entité juridique validée"
    ALLOCINE_ID = "Identifiant Allociné"


class IndividualOffersAlgoliaSearchAttributes(enum.Enum):
    CATEGORY = "Catégorie"
    DATE = "Date"
    DEPARTMENT = "Département du partenaire culturel"
    EAN = "EAN-13"
    VENUE = "Partenaire culturel"
    REGION = "Région du partenaire culturel"
    SUBCATEGORY = "Sous-catégorie"
    OFFERER = "Entité juridique"
    PRICE = "Prix"
    SHOW_TYPE = "Type de spectacle"


class IndividualOffersLlmSearchAttributes(enum.Enum):
    CATEGORY = "Catégorie"
    CREATION_DATE = "Date de création"
    EVENT_DATE = "Date de l'évènement"
    DEPARTMENT = "Département du partenaire culturel"
    PRICE = "Prix"
    SUBCATEGORY = "Sous-catégorie"


operator_no_require_value = ["NOT_EXIST"]

form_field_configuration = {
    "ADDRESS": {"field": "address", "operator": ["IN", "NOT_IN"]},
    "ALLOCINE_ID": {"field": "integer", "operator": ["EQUALS"]},
    "CATEGORY": {"field": "category", "operator": ["IN", "NOT_IN"]},
    "CREATION_DATE": {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    "DEPARTMENT": {"field": "department", "operator": ["IN", "NOT_IN"]},
    "REGION": {"field": "region", "operator": ["IN", "NOT_IN"]},
    "EAN": {"field": "string", "operator": ["EQUALS", "NOT_EQUALS"]},
    "EVENT_DATE": {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    "BOOKING_LIMIT_DATE": {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    "ID": {"field": "string", "operator": ["IN", "NOT_IN"]},
    "MEDIATION": {"field": "boolean", "operator": ["NULLABLE"]},
    "NAME": {"field": "string", "operator": ["CONTAINS", "NO_CONTAINS", "NAME_EQUALS", "NAME_NOT_EQUALS"]},
    "OFFERER": {"field": "offerer", "operator": ["IN", "NOT_IN"]},
    "OFFERER_TAG": {"field": "offerer_tags", "operator": ["IN", "NOT_IN", "NOT_EXIST"]},
    "PRODUCT": {"field": "integer", "operator": ["EQUALS", "NOT_EQUALS"]},
    "STATUS": {"field": "status", "operator": ["IN", "NOT_IN"]},
    "SUBCATEGORY": {"field": "subcategory", "operator": ["IN", "NOT_IN"]},
    "TAG": {"field": "criteria", "operator": ["IN", "NOT_IN", "NOT_EXIST"]},
    "VENUE": {"field": "venue", "operator": ["IN", "NOT_IN"]},
    "VENUE_TAG": {"field": "criteria", "operator": ["IN", "NOT_IN", "NOT_EXIST"]},
    "VENUE_TYPE": {"field": "venue_type", "operator": ["IN", "NOT_IN"]},
    "VALIDATION": {"field": "validation", "operator": ["IN", "NOT_IN"]},
    "VISA": {"field": "string", "operator": ["EQUALS", "NOT_EQUALS"]},
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
    "HEADLINE": {"field": "boolean", "operator": ["EQUALS"]},
    "HIGHLIGHT_REQUEST": {"field": "highlight", "operator": ["IN"]},
    "VALIDATED_OFFERER": {"field": "boolean", "operator": ["EQUALS"]},
}

algolia_form_field_configuration = {
    "CATEGORY": {"field": "category", "operator": ["IN", "NOT_IN"]},
    "DATE": {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    "DEPARTMENT": {"field": "department", "operator": ["IN", "NOT_IN"]},
    "REGION": {"field": "region", "operator": ["IN", "NOT_IN"]},
    "EAN": {"field": "string", "operator": ["EQUALS", "NOT_EQUALS"]},
    "OFFERER": {"field": "offerer", "operator": ["IN", "NOT_IN"]},
    "PRICE": {"field": "price", "operator": ["NUMBER_EQUALS", "GREATER_THAN_OR_EQUAL_TO", "LESS_THAN"]},
    "SUBCATEGORY": {"field": "subcategory", "operator": ["IN", "NOT_IN"]},
    "VENUE": {"field": "venue", "operator": ["IN", "NOT_IN"]},
    "SHOW_TYPE": {"field": "show_type", "operator": ["IN", "NOT_IN"]},
}

llm_form_field_configuration = {
    "CATEGORY": {"field": "category", "operator": ["IN", "NOT_IN"]},
    "SUBCATEGORY": {"field": "subcategory", "operator": ["IN", "NOT_IN"]},
    "DEPARTMENT": {"field": "department", "operator": ["IN", "NOT_IN"]},
    "PRICE": {"field": "price", "operator": ["EQUALS", "GREATER_THAN_OR_EQUAL_TO", "LESS_THAN"]},
    "CREATION_DATE": {"field": "date", "operator": ["EQUALS", "GREATER_THAN_OR_EQUAL_TO", "LESS_THAN"]},
    "EVENT_DATE": {"field": "date", "operator": ["EQUALS", "GREATER_THAN_OR_EQUAL_TO", "LESS_THAN"]},
}


class GetOffersBaseFields(forms_utils.PCForm):
    sort = wtforms.HiddenField(
        "sort", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("id", "dateCreated")))
    )
    order = wtforms.HiddenField(
        "order", default="asc", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("asc", "desc")))
    )
    limit = fields.PCLimitField(
        "Nombre maximum de résultats",
        choices=(
            (100, "Afficher 100 résultats maximum"),
            (500, "Afficher 500 résultats maximum"),
            (1000, "Afficher 1000 résultats maximum"),
            (3000, "Afficher 3000 résultats maximum"),
        ),
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
                "highlight",
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
                "venue_type",
                "validation",
                "show_type",
                "price",
                "boolean",
                "provider",
                "offerer_tags",
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
        autocomplete.prefill_highlights_choices(self.highlight)
        autocomplete.prefill_offerer_tag_choices(self.offerer_tags)

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
        "Booléen",
        choices=(("true", "Oui"), ("false", "Non")),
        default="true",
        validators=[
            wtforms.validators.Optional(""),
        ],
    )
    category = fields.PCSelectMultipleField(
        "Catégories",
        choices=forms_utils.choices_from_enum(pro_categories.CategoryIdLabelEnum),
        search_inline=True,
        field_list_compatibility=True,
    )
    highlight = fields.PCTomSelectField(
        "Valorisation thématique",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_highlights",
        search_inline=True,
        field_list_compatibility=True,
    )
    subcategory = fields.PCSelectMultipleField(
        "Sous-catégories",
        choices=forms_utils.choices_from_enum(subcategories.SubcategoryProLabelEnum),
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
    offerer_tags = fields.PCTomSelectField(
        "Tag de l'entité juridique",
        multiple=True,
        choices=[],
        coerce=int,
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerer_tags",
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
        "Prix en euros",
        use_locale=True,
        validators=[
            wtforms.validators.Optional(""),
            wtforms.validators.NumberRange(min=0, message="Doit contenir un nombre positif"),
        ],
    )
    offerer = fields.PCTomSelectField(
        "Entités juridiques",
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
        "Partenaires culturels",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_venues",
        search_inline=True,
        field_list_compatibility=True,
    )
    venue_type = fields.PCSelectMultipleField(
        "Activité principale du partenaire",
        choices=forms_utils.choices_from_enum(offerers_models.VenueTypeCode),
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
    show_type = fields.PCSelectMultipleField(
        "Type de spectacle",
        choices=[(str(s), show.SHOW_TYPES_LABEL_BY_CODE[s]) for s in show.SHOW_TYPES_LABEL_BY_CODE],
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

        return string


class OfferAlgoliaSearchSubForm(forms_utils.PCForm):
    class Meta:
        csrf = False
        locales = ["fr_FR", "fr"]

    json_data = json.dumps(
        {
            "display_configuration": algolia_form_field_configuration,
            "all_available_fields": [
                "category",
                "date",
                "department",
                "offerer",
                "price",
                "region",
                "show_type",
                "string",
                "subcategory",
                "venue",
            ],
            "sub_rule_type_field_name": "search_field",
            "operator_field_name": "operator",
        }
    )

    def __init__(self, *args: list, **kwargs: dict):
        super().__init__(*args, **kwargs)
        autocomplete.prefill_offerers_choices(self.offerer)
        autocomplete.prefill_venues_choices(self.venue)

    search_field = fields.PCSelectWithPlaceholderValueField(
        "Champ de recherche",
        choices=forms_utils.choices_from_enum(IndividualOffersAlgoliaSearchAttributes),
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
    category = fields.PCSelectMultipleField(
        "Catégories",
        choices=forms_utils.choices_from_enum(pro_categories.CategoryIdLabelEnum),
        search_inline=True,
        field_list_compatibility=True,
    )
    subcategory = fields.PCSelectMultipleField(
        "Sous-catégories",
        choices=forms_utils.choices_from_enum(subcategories.SubcategoryProLabelEnum),
        search_inline=True,
        field_list_compatibility=True,
    )
    date = fields.PCDateField(
        validators=[
            wtforms.validators.Optional(""),
        ]
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
    offerer = fields.PCTomSelectField(
        "Entités juridiques",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
        search_inline=True,
        field_list_compatibility=True,
    )
    price = fields.PCDecimalField(
        "Prix",
        use_locale=True,
        validators=[
            wtforms.validators.Optional(""),
            wtforms.validators.NumberRange(min=0, message="Doit contenir un nombre positif"),
        ],
    )
    string = fields.PCOptStringField(
        "Texte",
        validators=[
            wtforms.validators.Length(max=4096, message="Doit contenir moins de %(max)d caractères"),
        ],
    )
    venue = fields.PCTomSelectField(
        "Partenaires culturels",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_venues",
        search_inline=True,
        field_list_compatibility=True,
    )
    show_type = fields.PCSelectMultipleField(
        "Type de spectacle",
        choices=[(label, label) for label in show.SHOW_TYPES_LABEL_BY_CODE.values()],
        search_inline=True,
        field_list_compatibility=True,
    )

    def validate_string(self, string: fields.PCStringField) -> fields.PCStringField:
        if string.data:
            search_field = self._fields["search_field"].data
            if search_field == "EAN":
                if not string_utils.is_ean_valid(string.data):
                    raise wtforms.validators.ValidationError("La recherche ne correspond pas au format d'un EAN-13")
                string.data = string_utils.format_ean_or_visa(string.data)
        return string


class OfferLlmSearchSubForm(forms_utils.PCForm):
    class Meta:
        csrf = False
        locales = ["fr_FR", "fr"]

    json_data = json.dumps(
        {
            "display_configuration": llm_form_field_configuration,
            "all_available_fields": [
                "category",
                "date",
                "department",
                "price",
                "subcategory",
            ],
            "sub_rule_type_field_name": "search_field",
            "operator_field_name": "operator",
        }
    )

    def __init__(self, *args: list, **kwargs: dict):
        super().__init__(*args, **kwargs)

    search_field = fields.PCSelectWithPlaceholderValueField(
        "Champ de recherche",
        choices=forms_utils.choices_from_enum(IndividualOffersLlmSearchAttributes),
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
    category = fields.PCSelectMultipleField(
        "Catégories",
        choices=forms_utils.choices_from_enum(pro_categories.CategoryIdLabelEnum),
        search_inline=True,
        field_list_compatibility=True,
    )
    subcategory = fields.PCSelectMultipleField(
        "Sous-catégories",
        choices=forms_utils.choices_from_enum(subcategories.SubcategoryProLabelEnum),
        search_inline=True,
        field_list_compatibility=True,
    )
    date = fields.PCDateField(
        validators=[
            wtforms.validators.Optional(""),
        ]
    )
    department = fields.PCSelectMultipleField(
        "Départements",
        choices=constants.area_choices,
        search_inline=True,
        field_list_compatibility=True,
    )
    price = fields.PCDecimalField(
        "Prix",
        use_locale=True,
        validators=[
            wtforms.validators.Optional(""),
            wtforms.validators.NumberRange(min=0, message="Doit contenir un nombre positif"),
        ],
    )


class BaseOfferAdvancedSearchForm(GetOffersBaseFields):
    class Meta:
        csrf = False

    method = "GET"

    search = fields.PCFieldListField(
        fields.PCFormField(OfferAdvancedSearchSubForm),
        label="recherches",
        min_entries=1,
    )

    @classmethod
    def is_sub_search_empty(cls, sub_search: dict[str, typing.Any]) -> bool:
        field_name = sub_search.get("search_field")
        operator = sub_search.get("operator")
        if field_name:
            field_attribute_name = cls.form_field_configuration.get(field_name, {}).get("field", "")
            field_data = sub_search.get(field_attribute_name)
            if field_data not in (None, []):
                return False
            if operator in operator_no_require_value:
                return False
        return True

    @classmethod
    def is_search_empty(cls, search_data: list[dict[str, typing.Any]]) -> bool:
        for sub_search in search_data:
            if not cls.is_sub_search_empty(sub_search):
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
                if type(self).is_sub_search_empty(sub_search):
                    try:
                        errors.append(f"Le filtre « {self.search_attributes[search_field].value} » est vide.")
                    except KeyError:
                        errors.append(f"Le filtre {search_field} est invalide.")
                else:
                    operator = sub_search.get("operator")
                    if operator not in self.form_field_configuration.get(search_field, {}).get("operator", []):
                        try:
                            errors.append(
                                f"L'opérateur « {utils.AdvancedSearchOperators[operator].value} » n'est pas supporté par le filtre {IndividualOffersSearchAttributes[search_field].value}."
                            )
                        except KeyError:
                            errors.append(f"L'opérateur {operator} n'est pas supporté par le filtre {search_field}.")

        if errors:
            flash("\n".join(errors), "warning")
            return False

        return super().validate(extra_validators)


class GetOfferAdvancedSearchForm(BaseOfferAdvancedSearchForm):
    form_field_configuration = form_field_configuration
    search_attributes = IndividualOffersSearchAttributes

    def is_empty(self) -> bool:
        return GetOfferAdvancedSearchForm.is_search_empty(self.search.data) and super().is_empty()


class GetOfferAlgoliaSearchForm(BaseOfferAdvancedSearchForm):
    form_field_configuration = algolia_form_field_configuration
    search_attributes = IndividualOffersAlgoliaSearchAttributes

    algolia_search = fields.PCOptStringField("Recherche", full_width=True)
    search = fields.PCFieldListField(
        fields.PCFormField(OfferAlgoliaSearchSubForm),
        label="recherches",
        min_entries=1,
    )

    def is_empty(self) -> bool:
        empty = not self.algolia_search.data
        empty = empty and GetOfferAlgoliaSearchForm.is_search_empty(self.search.data)
        return empty and super().is_empty()


class GetOfferLlmSearchForm(BaseOfferAdvancedSearchForm):
    form_field_configuration = llm_form_field_configuration
    search_attributes = IndividualOffersLlmSearchAttributes

    llm_search = fields.PCTextareaField(
        "Recherche",
        rows=2,
        can_be_cleared=True,
        validators=[
            wtforms.validators.Optional(""),
            wtforms.validators.Length(min=3, max=512, message="doit contenir entre %(min)d et %(max)d caractères"),
        ],
    )
    search = fields.PCFieldListField(
        fields.PCFormField(OfferLlmSearchSubForm),
        label="recherches",
        min_entries=1,
    )

    def is_empty(self) -> bool:
        empty = not self.llm_search.data
        empty = empty and GetOfferLlmSearchForm.is_search_empty(self.search.data)
        return empty and super().is_empty()


class EditOfferForm(empty_forms.DynamicForm):
    criteria = fields.PCTomSelectField(
        "Tags", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_web.autocomplete_criteria"
    )
    rankingWeight = fields.PCOptIntegerField("Pondération")


class BatchEditOfferForm(empty_forms.BatchForm, EditOfferForm):
    pass


class EditOfferVenueForm(FlaskForm):
    venue = fields.PCSelectWithPlaceholderValueField("Nouveau partenaire culturel", choices=[], validate_choice=False)
    move_offer_address = fields.PCSwitchBooleanField(
        "Déplacer aussi la localisation à l'adresse du nouveau partenaire culturel", full_row=True
    )
    notify_beneficiary = fields.PCSwitchBooleanField("Notifier les jeunes", full_row=True)

    def set_venue_choices(self, venues: list[offerers_models.Venue]) -> None:
        self.venue.choices = [
            (venue.id, f"{venue.common_name} ({venue.siret if venue.siret else 'Pas de SIRET'})") for venue in venues
        ]


class EditStockForm(FlaskForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    def __init__(self, old_price: float | decimal.Decimal):
        super().__init__()
        self.price.validators = [
            wtforms.validators.Optional(),
            wtforms.validators.NumberRange(
                min=0, max=old_price, message=f"Le prix doit être positif et inférieur à {old_price} €."
            ),
        ]

    price = fields.PCDecimalField(
        "Nouveau prix",
        use_locale=True,
    )
    percent = fields.PCDecimalField(
        "Réduction en pourcentage (%)",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.NumberRange(
                min=0, max=100, message="La réduction du prix doit être entre 0 %% et 100 %%."
            ),
        ],
        use_locale=True,
    )

    def validate(
        self,
    ) -> bool:
        if self.price.data and self.percent.data:
            error = ("Un seul des deux champs est utilisable à la fois",)
            self.price.errors += error
            self.percent.errors += error
            return False
        if not (self.price.data or self.percent.data):
            error = ("Un des champs est obligatoire",)
            self.price.errors += error
            self.percent.errors += error
            return False
        return super().validate()


class ConnectAsForm(FlaskForm):
    object_id = wtforms.HiddenField()
    object_type = wtforms.HiddenField()
    redirect = wtforms.HiddenField()
