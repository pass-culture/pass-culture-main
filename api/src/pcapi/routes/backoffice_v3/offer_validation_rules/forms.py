import enum
import json
import re

from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
import pcapi.core.offers.models as offers_models
from pcapi.domain.show_types import SHOW_SUB_TYPES_LABEL_BY_CODE

from .. import filters
from ..forms import fields
from ..forms import utils


class SearchRuleForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("Nom de la règle")

    def is_empty(self) -> bool:
        return not any((self.q.data,))


class OfferType(enum.Enum):
    OFFER = "Offre"
    COLLECTIVE_OFFER = "Offre collective"
    COLLECTIVE_OFFER_TEMPLATE = "Offre collective vitrine"


class OfferValidationSubRuleForm(FlaskForm):
    class Meta:
        csrf = False

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
    offer_type = fields.PCSelectMultipleField("Type de l'offre", choices=utils.choices_from_enum(OfferType))
    offerer = fields.PCTomSelectField(
        "Structure",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_v3_web.autocomplete_offerers",
    )
    subcategories = fields.PCSelectMultipleField(
        "Sous-catégories", choices=[(s.id, s.pro_label) for s in subcategories_v2.ALL_SUBCATEGORIES]
    )
    categories = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(categories.CategoryIdLabelEnum)
    )
    show_sub_type = fields.PCSelectMultipleField(
        "Sous-type de spectacle",
        choices=[(str(s), SHOW_SUB_TYPES_LABEL_BY_CODE[s]) for s in SHOW_SUB_TYPES_LABEL_BY_CODE],
    )

    form_field_configuration = {
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
        "DESCRIPTION_OFFER": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
        "DESCRIPTION_COLLECTIVE_OFFER": {"field": "list_field", "operator": ["CONTAINS", "CONTAINS_EXACTLY"]},
        "DESCRIPTION_COLLECTIVE_OFFER_TEMPLATE": {
            "field": "list_field",
            "operator": ["CONTAINS", "CONTAINS_EXACTLY"],
        },
        "SUBCATEGORY_OFFER": {"field": "subcategories", "operator": ["IN", "NOT_IN"]},
        "CATEGORY_OFFER": {"field": "categories", "operator": ["IN", "NOT_IN"]},
        "SHOW_SUB_TYPE_OFFER": {"field": "show_sub_type", "operator": ["IN", "NOT_IN"]},
        "ID_OFFERER": {"field": "offerer", "operator": ["IN", "NOT_IN"]},
    }
    json_data = json.dumps(
        {
            "display_configuration": form_field_configuration,
            "all_available_fields": [
                "decimal_field",
                "list_field",
                "offer_type",
                "offerer",
                "categories",
                "subcategories",
                "show_sub_type",
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
            list_field.data = [keyword.strip() for keyword in re.split(r",+", list_field.data) if keyword.strip()]
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

    def validate_offerer(self, offerer: fields.PCTomSelectField) -> fields.PCSelectMultipleField:
        offerer.data = (
            offerer.data
            if self.form_field_configuration.get(self.sub_rule_type.data, {}).get("field") == "offerer"
            else []
        )
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


class CreateOfferValidationRuleForm(FlaskForm):
    name = fields.PCStringField("Nom de la règle")
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
