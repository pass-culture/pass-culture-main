import enum
import json
import re

import wtforms
from flask_wtf import FlaskForm

from pcapi.core.categories import pro_categories
from pcapi.core.categories.genres.show import SHOW_SUB_TYPES_LABEL_BY_CODE
from pcapi.core.categories.models import EacFormat
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES
from pcapi.core.categories.subcategories import SubcategoryIdEnum
from pcapi.core.offers import models as offers_models
from pcapi.routes.backoffice import autocomplete
from pcapi.utils.clean_accents import clean_accents

from .. import filters
from ..forms import fields
from ..forms import utils


OFFER_VALIDATION_SUB_RULE_FORM_FIELD_CONFIGURATION = {
    "OFFER_TYPE": {"field": "offer_type", "operator": ["IN", "NOT_IN"]},
    "MAX_PRICE_OFFER": {
        "field": "decimal_field",
        "operator": [
            "EQUALS",
            "NOT_EQUALS",
            "GREATER_THAN",
            "GREATER_THAN_OR_EQUAL_TO",
            "LESS_THAN",
            "LESS_THAN_OR_EQUAL_TO",
        ],
    },
    "PRICE_COLLECTIVE_STOCK": {
        "field": "decimal_field",
        "operator": [
            "EQUALS",
            "NOT_EQUALS",
            "GREATER_THAN",
            "GREATER_THAN_OR_EQUAL_TO",
            "LESS_THAN",
            "LESS_THAN_OR_EQUAL_TO",
        ],
    },
    "PRICE_DETAIL_COLLECTIVE_STOCK": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
    "PRICE_DETAIL_COLLECTIVE_OFFER_TEMPLATE": {
        "field": "list_field",
        "operator": ["CONTAINS", "CONTAINS_EXACTLY"],
    },
    "WITHDRAWAL_DETAILS_OFFER": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
    "NAME_OFFER": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
    "NAME_COLLECTIVE_OFFER": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
    "NAME_COLLECTIVE_OFFER_TEMPLATE": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
    "TEXT_OFFER": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
    "TEXT_COLLECTIVE_OFFER": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
    "TEXT_COLLECTIVE_OFFER_TEMPLATE": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
    "DESCRIPTION_OFFER": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
    "DESCRIPTION_COLLECTIVE_OFFER": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
    "DESCRIPTION_COLLECTIVE_OFFER_TEMPLATE": {
        "field": "list_field",
        "operator": ["CONTAINS", "CONTAINS_EXACTLY"],
    },
    "SUBCATEGORY_OFFER": {"field": "subcategories", "operator": ["IN", "NOT_IN"]},
    "CATEGORY_OFFER": {"field": "categories", "operator": ["IN", "NOT_IN"]},
    "FORMATS_COLLECTIVE_OFFER": {"field": "formats", "operator": ["INTERSECTS", "NOT_INTERSECTS"]},
    "FORMATS_COLLECTIVE_OFFER_TEMPLATE": {"field": "formats", "operator": ["INTERSECTS", "NOT_INTERSECTS"]},
    "SHOW_SUB_TYPE_OFFER": {"field": "show_sub_type", "operator": ["IN", "NOT_IN"]},
    "ID_VENUE": {"field": "venue", "operator": ["IN", "NOT_IN"]},
    "ID_OFFERER": {"field": "offerer", "operator": ["IN", "NOT_IN"]},
}


class SearchRuleForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Nom de la règle, mots clés")
    offerer = fields.PCTomSelectField(
        "Entités juridiques",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
    )
    venue = fields.PCTomSelectField(
        "Partenaires culturels",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_venues",
    )
    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(pro_categories.CategoryIdLabelEnum)
    )
    subcategory = fields.PCSelectMultipleField("Sous-catégories", choices=utils.choices_from_enum(SubcategoryIdEnum))

    def is_empty(self) -> bool:
        return not any((self.q.data, self.offerer.data, self.venue.data, self.category.data, self.subcategory.data))

    def __init__(self, *args: list, **kwargs: dict):
        super().__init__(*args, **kwargs)
        autocomplete.prefill_offerers_choices(self.offerer)
        autocomplete.prefill_venues_choices(self.venue)


class OfferType(enum.Enum):
    Offer = "Offre individuelle"
    CollectiveOffer = "Offre collective"
    CollectiveOfferTemplate = "Offre collective vitrine"


class OfferValidationSubRuleForm(FlaskForm):
    class Meta:
        csrf = False

    id = fields.PCOptHiddenIntegerField("ID de sous-règle")
    sub_rule_type = fields.PCSelectWithPlaceholderValueField(
        "Type de sous-règle",
        choices=utils.choices_from_enum(
            offers_models.OfferValidationSubRuleField, formatter=filters.format_offer_validation_sub_rule_field
        ),
    )
    operator = fields.PCSelectWithPlaceholderValueField(
        "Opérateur",
        choices=utils.choices_from_enum(
            offers_models.OfferValidationRuleOperator, formatter=filters.format_offer_validation_operator
        ),
    )
    decimal_field = fields.PCDecimalField(
        "Valeur numérique",
        validators=(wtforms.validators.Optional(""),),
    )
    list_field = fields.PCTextareaField(
        "Liste de mots-clés",
        rows=10,
        validators=(wtforms.validators.Length(max=10000, message="ne doit pas dépasser %(max)d caractères"),),
    )
    offer_type = fields.PCSelectMultipleField(
        "Type de l'offre", choices=utils.choices_from_enum(OfferType), field_list_compatibility=True
    )
    venue = fields.PCTomSelectField(
        "Partenaire culturel",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_venues",
        field_list_compatibility=True,
    )
    offerer = fields.PCTomSelectField(
        "Entité juridique",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
        field_list_compatibility=True,
    )
    subcategories = fields.PCSelectMultipleField(
        "Sous-catégories",
        choices=[(s.id, s.pro_label) for s in ALL_SUBCATEGORIES],
        field_list_compatibility=True,
    )
    categories = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(pro_categories.CategoryIdLabelEnum), field_list_compatibility=True
    )
    show_sub_type = fields.PCSelectMultipleField(
        "Sous-type de spectacle",
        choices=[(str(s), SHOW_SUB_TYPES_LABEL_BY_CODE[s]) for s in SHOW_SUB_TYPES_LABEL_BY_CODE],
        field_list_compatibility=True,
    )
    formats = fields.PCSelectMultipleField(
        "Formats", choices=utils.choices_from_enum(EacFormat), field_list_compatibility=True
    )

    form_field_configuration = OFFER_VALIDATION_SUB_RULE_FORM_FIELD_CONFIGURATION

    json_data = json.dumps(
        {
            "display_configuration": form_field_configuration,
            "all_available_fields": [
                "decimal_field",
                "list_field",
                "offer_type",
                "venue",
                "offerer",
                "categories",
                "subcategories",
                "show_sub_type",
                "formats",
            ],
            "sub_rule_type_field_name": "sub_rule_type",
            "operator_field_name": "operator",
        }
    )

    def validate_decimal_field(self, decimal_field: fields.PCDecimalField) -> fields.PCDecimalField:
        decimal_field.data = (
            decimal_field.data
            if self.form_field_configuration.get(self.sub_rule_type.data, {}).get("field") == "decimal_field"
            else ""
        )
        return decimal_field

    def validate_list_field(self, list_field: fields.PCTextareaField) -> fields.PCTextareaField:
        if (
            list_field.data
            and self.form_field_configuration.get(self.sub_rule_type.data, {}).get("field") == "list_field"
        ):
            if not re.match(r"(.+?)(,|$)", list_field.data):
                raise wtforms.validators.ValidationError(
                    "Seuls des groupes de mots séparés par des virgules sont autorisés"
                )
            list_field.data = sorted(
                [keyword.strip() for keyword in re.split(r",+", list_field.data) if keyword.strip()],
                key=lambda keyword: clean_accents(keyword).lower(),
            )
        else:
            list_field.data = []
        return list_field

    def validate_offer_type(self, offer_type: fields.PCSelectMultipleField) -> fields.PCSelectMultipleField:
        offer_type.data = (
            offer_type.data
            if self.form_field_configuration.get(self.sub_rule_type.data, {}).get("field") == "offer_type"
            else []
        )
        return offer_type

    def validate_venue(self, venue: fields.PCTomSelectField) -> fields.PCSelectMultipleField:
        venue.data = (
            venue.data if self.form_field_configuration.get(self.sub_rule_type.data, {}).get("field") == "venue" else []
        )
        venue.data = [int(venue_id) for venue_id in venue.data]
        return venue

    def validate_offerer(self, offerer: fields.PCTomSelectField) -> fields.PCSelectMultipleField:
        offerer.data = (
            offerer.data
            if self.form_field_configuration.get(self.sub_rule_type.data, {}).get("field") == "offerer"
            else []
        )
        offerer.data = [int(offerer_id) for offerer_id in offerer.data]
        return offerer

    def validate_categories(self, categories_field: fields.PCSelectMultipleField) -> fields.PCSelectMultipleField:
        categories_field.data = (
            categories_field.data
            if self.form_field_configuration.get(self.sub_rule_type.data, {}).get("field") == "categories"
            else []
        )
        return categories_field

    def validate_subcategories(self, subcategories: fields.PCSelectMultipleField) -> fields.PCSelectMultipleField:
        subcategories.data = (
            subcategories.data
            if self.form_field_configuration.get(self.sub_rule_type.data, {}).get("field") == "subcategories"
            else []
        )
        return subcategories

    def validate_show_sub_type(self, show_sub_type: fields.PCSelectMultipleField) -> fields.PCSelectMultipleField:
        show_sub_type.data = (
            show_sub_type.data
            if self.form_field_configuration.get(self.sub_rule_type.data, {}).get("field") == "show_sub_type"
            else []
        )
        return show_sub_type

    def validate_operator(
        self, operator: fields.PCSelectWithPlaceholderValueField
    ) -> fields.PCSelectWithPlaceholderValueField:
        if operator.data not in self.form_field_configuration.get(self.sub_rule_type.data, {}).get("operator", []):
            raise wtforms.validators.ValidationError("L'opérateur doit être conforme au type de sous-règle choisi")
        return operator

    def validate_formats(self, formats_field: fields.PCSelectMultipleField) -> fields.PCSelectMultipleField:
        formats_field.data = (
            formats_field.data
            if self.form_field_configuration.get(self.sub_rule_type.data, {}).get("field") == "formats"
            else []
        )
        return formats_field


class CreateOfferValidationRuleForm(FlaskForm):
    name = fields.PCStringField(
        "Nom de la règle",
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.Length(max=256, message="ne doit pas dépasser %(max)d caractères"),
        ),
    )
    sub_rules = fields.PCFieldListField(
        fields.PCFormField(OfferValidationSubRuleForm), label="Sous-règles", min_entries=1
    )

    def validate_sub_rules(self, sub_rules: fields.PCFieldListField) -> fields.PCFieldListField:
        for sub_rule_data in sub_rules.data:
            # Check that the field corresponding to the selected sub_rule_type is filled
            corresponding_field = OfferValidationSubRuleForm.form_field_configuration.get(
                sub_rule_data["sub_rule_type"], {}
            )
            if not corresponding_field:
                raise wtforms.validators.ValidationError("Information obligatoire.")
            if not sub_rule_data[corresponding_field.get("field")]:
                raise wtforms.validators.ValidationError(
                    f"Tous les champs de {filters.format_offer_validation_sub_rule_field(offers_models.OfferValidationSubRuleField[sub_rule_data['sub_rule_type']])} doivent être remplis"
                )
        return sub_rules
