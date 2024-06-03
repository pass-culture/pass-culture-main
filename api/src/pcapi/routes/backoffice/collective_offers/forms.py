import decimal
import enum
import json
import re
import typing
from urllib.parse import urlencode

from flask import flash
from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.models.offer_mixin import OfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.backoffice import autocomplete
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import constants
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils as forms_utils
from pcapi.routes.backoffice.offers import forms


class CollectiveOffersSearchAttributes(enum.Enum):
    FORMATS = "Formats"
    INSTITUTION = "Établissement"
    CREATION_DATE = "Date de création"
    EVENT_DATE = "Date de l'évènement"
    BOOKING_LIMIT_DATE = "Date limite de réservation"
    DEPARTMENT = "Département"
    REGION = "Région"
    VALIDATION = "État"
    ID = "ID de l'offre"
    VENUE = "Lieu"
    NAME = "Nom de l'offre"
    STATUS = "Statut"
    OFFERER = "Structure"
    PRICE = "Prix"


operator_no_require_value = ["NOT_EXIST"]

form_field_configuration = {
    "CREATION_DATE": {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    "DEPARTMENT": {"field": "department", "operator": ["IN", "NOT_IN"]},
    "FORMATS": {"field": "formats", "operator": ["INTERSECTS", "NOT_INTERSECTS"]},
    "REGION": {"field": "region", "operator": ["IN", "NOT_IN"]},
    "EVENT_DATE": {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    "BOOKING_LIMIT_DATE": {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    "ID": {"field": "string", "operator": ["IN", "NOT_IN"]},
    "INSTITUTION": {"field": "institution", "operator": ["IN", "NOT_IN"]},
    "NAME": {"field": "string", "operator": ["CONTAINS", "NO_CONTAINS", "NAME_EQUALS", "NAME_NOT_EQUALS"]},
    "OFFERER": {"field": "offerer", "operator": ["IN", "NOT_IN"]},
    "STATUS": {"field": "status", "operator": ["IN", "NOT_IN"]},
    "VENUE": {"field": "venue", "operator": ["IN", "NOT_IN"]},
    "VALIDATION": {"field": "validation", "operator": ["IN", "NOT_IN"]},
    "PRICE": {"field": "price", "operator": ["EQUALS", "LESS_THAN", "GREATER_THAN_OR_EQUAL_TO"]},
}


class CollectiveOfferAdvancedSearchSubForm(forms_utils.PCForm):
    class Meta:
        csrf = False

    json_data = json.dumps(
        {
            "display_configuration": form_field_configuration,
            "all_available_fields": [
                "date",
                "department",
                "formats",
                "region",
                "institution",
                "integer",
                "offerer",
                "string",
                "status",
                "venue",
                "validation",
                "price",
            ],
            "sub_rule_type_field_name": "search_field",
            "operator_field_name": "operator",
        }
    )

    def __init__(self, *args: list, **kwargs: dict):
        super().__init__(*args, **kwargs)
        autocomplete.prefill_institutions_choices(self.institution)
        autocomplete.prefill_offerers_choices(self.offerer)
        autocomplete.prefill_venues_choices(self.venue)

    search_field = fields.PCSelectWithPlaceholderValueField(
        "Champ de recherche",
        choices=forms_utils.choices_from_enum(CollectiveOffersSearchAttributes),
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
    formats = fields.PCSelectMultipleField(
        "Formats", choices=forms_utils.choices_from_enum(subcategories.EacFormat), field_list_compatibility=True
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
    institution = fields.PCTomSelectField(
        "Établissements",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_institutions",
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

    def validate_string(self, string: fields.PCStringField) -> fields.PCStringField:
        if string.data:
            search_field = self._fields["search_field"].data

            if search_field == "ID" and not re.match(r"^[\d\s,;]+$", string.data):
                raise wtforms.validators.ValidationError("La liste d'ID n'est pas valide")

        return string


class GetCollectiveOfferAdvancedSearchForm(forms.GetOffersBaseFields):
    class Meta:
        csrf = False

    method = "GET"
    only_validated_offerers = fields.PCSwitchBooleanField(
        "Uniquement les offres des structures validées", full_row=True
    )
    search = fields.PCFieldListField(
        fields.PCFormField(CollectiveOfferAdvancedSearchSubForm),
        label="recherches",
        min_entries=1,
    )

    def is_empty(self) -> bool:
        empty = GetCollectiveOfferAdvancedSearchForm.is_search_empty(self.search.data)
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
            if not GetCollectiveOfferAdvancedSearchForm.is_sub_search_empty(sub_search):
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
                if GetCollectiveOfferAdvancedSearchForm.is_sub_search_empty(sub_search):
                    try:
                        errors.append(f"Le filtre « {CollectiveOffersSearchAttributes[search_field].value} » est vide.")
                    except KeyError:
                        errors.append(f"Le filtre {search_field} est invalide.")

        if errors:
            flash("\n".join(errors), "warning")
            return False

        return super().validate(extra_validators)


class GetCollectiveOfferTemplatesListForm(forms.GetOffersBaseFields):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID, nom de l'offre")
    from_date = fields.PCDateField("Créées à partir du", validators=(wtforms.validators.Optional(),))
    to_date = fields.PCDateField("Jusqu'au", validators=(wtforms.validators.Optional(),))
    only_validated_offerers = fields.PCSwitchBooleanField("Uniquement les offres des structures validées")
    formats = fields.PCSelectMultipleField("Formats", choices=forms_utils.choices_from_enum(subcategories.EacFormat))
    offerer = fields.PCTomSelectField(
        "Structures",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
    )
    venue = fields.PCTomSelectField(
        "Lieux", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_web.autocomplete_venues"
    )
    status = fields.PCSelectMultipleField(
        "États",
        choices=forms_utils.choices_from_enum(OfferValidationStatus, formatter=filters.format_offer_validation_status),
    )

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._fields.move_to_end("limit")

    def is_empty(self) -> bool:
        # 'only_validated_offerers', 'sort' must be combined with other filters
        empty = not any(
            (
                self.formats.data,
                self.venue.data,
                self.offerer.data,
                self.status.data,
                self.from_date.data,
                self.to_date.data,
                self.q.data,
            )
        )
        return empty and super().is_empty()


class EditCollectiveOfferPrice(FlaskForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    price = fields.PCDecimalField(
        "Prix",
        use_locale=True,
        validators=[
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.NumberRange(min=0, message="Doit contenir un nombre positif"),
        ],
    )

    numberOfTickets = fields.PCIntegerField(
        "Places",
        validators=[
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.NumberRange(min=0, message="Doit contenir un nombre positif"),
        ],
    )

    def validate_price(self, price: fields.PCOptSearchField) -> fields.PCOptSearchField:
        price.data = price.data.quantize(decimal.Decimal("1.00"))
        return price
