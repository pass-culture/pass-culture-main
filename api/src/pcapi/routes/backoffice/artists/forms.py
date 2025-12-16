import enum
import json
import typing
from functools import partial
from urllib.parse import urlencode

import wtforms
from flask import flash
from flask import url_for
from flask_wtf import FlaskForm

from pcapi.core.artist import models as artist_models
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils as forms_utils


class ArtistAdvancedSearchAttributes(enum.Enum):
    ID = "ID"
    NAME_OR_ALIAS = "Nom ou alias"
    IS_VISIBLE = "Visible"
    CREATION_DATE = "Date de création"
    PRODUCT_NAME = "Nom du produit associé"


operator_no_require_value = ["NOT_EXIST"]

artist_form_field_configuration = {
    "ID": {"field": "string", "operator": ["EQUALS", "NOT_EQUALS"]},
    "NAME_OR_ALIAS": {"field": "string", "operator": ["CONTAINS", "NO_CONTAINS", "EQUALS", "NOT_EQUALS"]},
    "IS_VISIBLE": {"field": "boolean", "operator": ["EQUALS"]},
    "CREATION_DATE": {"field": "date", "operator": ["DATE_FROM", "DATE_TO", "DATE_EQUALS"]},
    "PRODUCT_NAME": {"field": "string", "operator": ["CONTAINS", "EQUALS"]},
}


class GetArtistsBaseFields(forms_utils.PCForm):
    sort = wtforms.HiddenField(
        "sort", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("date_created")))
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
        ),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )

    def get_sort_link(self, endpoint: str) -> str:
        form_url = partial(url_for, endpoint, **self.raw_data)
        return form_url(
            sort="date_created",
            order="asc" if self.sort.data == "date_created" and self.order.data == "desc" else "desc",
        )

    def is_empty(self) -> bool:
        return True


class ArtistAdvancedSearchSubForm(forms_utils.PCForm):
    class Meta:
        csrf = False
        locales = ["fr_FR", "fr"]

    json_data = json.dumps(
        {
            "display_configuration": artist_form_field_configuration,
            "all_available_fields": [
                "string",
                "date",
                "boolean",
            ],
            "sub_rule_type_field_name": "search_field",
            "operator_field_name": "operator",
        }
    )

    search_field = fields.PCSelectWithPlaceholderValueField(
        "Champ de recherche",
        choices=forms_utils.choices_from_enum(ArtistAdvancedSearchAttributes),
        validators=[
            wtforms.validators.Optional(""),
        ],
    )
    operator = fields.PCSelectField(
        "Opérateur",
        choices=forms_utils.choices_from_enum(utils.AdvancedSearchOperators),
        default=utils.AdvancedSearchOperators.EQUALS,
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
    string = fields.PCOptStringField(
        "Texte",
        validators=[
            wtforms.validators.Length(max=4096, message="Doit contenir moins de %(max)d caractères"),
        ],
    )
    date = fields.PCDateField(
        validators=[
            wtforms.validators.Optional(""),
        ]
    )


class BaseArtistAdvancedSearchForm(GetArtistsBaseFields):
    class Meta:
        csrf = False

    method = "GET"

    search = fields.PCFieldListField(
        fields.PCFormField(ArtistAdvancedSearchSubForm),
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
                        errors.append(f"Le filtre « {ArtistAdvancedSearchAttributes[search_field].value} » est vide.")
                    except KeyError:
                        errors.append(f"Le filtre {search_field} est invalide.")
                else:
                    operator = sub_search.get("operator")
                    if operator not in self.form_field_configuration.get(search_field, {}).get("operator", []):
                        try:
                            errors.append(
                                f"L'opérateur « {utils.AdvancedSearchOperators[operator].value} » n'est pas supporté par le filtre {ArtistAdvancedSearchAttributes[search_field].value}."
                            )
                        except KeyError:
                            errors.append(f"L'opérateur {operator} n'est pas supporté par le filtre {search_field}.")

        if errors:
            flash("\n".join(errors), "warning")
            return False

        return super().validate(extra_validators)


class GetArtistAdvancedSearchForm(BaseArtistAdvancedSearchForm):
    form_field_configuration = artist_form_field_configuration

    def is_empty(self) -> bool:
        return GetArtistAdvancedSearchForm.is_search_empty(self.search.data) and super().is_empty()


class ArtistEditForm(FlaskForm):
    name = fields.PCStringField("Nom de l'artiste")
    description = fields.PCTextareaField("Description")
    biography = fields.PCTextareaField("Biographie")
    wikidata_id = fields.PCOptStringField("ID Wikidata")
    wikipedia_url = fields.PCURLField("URL Wikipédia")


class ProductIdentifierTypeEnum(enum.Enum):
    EAN = "ean"
    ALLOCINE_ID = "allocineId"
    VISA = "visa"


def format_product_identifier_type(type_option: ProductIdentifierTypeEnum) -> str:
    match type_option:
        case ProductIdentifierTypeEnum.EAN:
            return "EAN-13"
        case ProductIdentifierTypeEnum.ALLOCINE_ID:
            return "ID Allociné"
        case ProductIdentifierTypeEnum.VISA:
            return "Visa"
        case _:
            return type_option.value


class AssociateProductSearchForm(FlaskForm):
    identifier_type = fields.PCSelectField(
        "Type d'identifiant",
        choices=forms_utils.choices_from_enum(ProductIdentifierTypeEnum, format_product_identifier_type),
        default=ProductIdentifierTypeEnum.EAN,
    )
    identifier_value = fields.PCStringField(
        "Identifiant du produit", validators=[wtforms.validators.DataRequired("L'identifiant est obligatoire.")]
    )


def format_artist_type(artist_type: artist_models.ArtistType) -> str:
    match artist_type:
        case artist_models.ArtistType.AUTHOR:
            return "Auteur"
        case artist_models.ArtistType.PERFORMER:
            return "Interprète"
        case _:
            return artist_type.value


class ConfirmAssociationForm(FlaskForm):
    product_id = wtforms.HiddenField(validators=[wtforms.validators.DataRequired()])
    artist_type = fields.PCSelectField(
        "Rôle de l'artiste pour ce produit",
        choices=forms_utils.choices_from_enum(artist_models.ArtistType, format_artist_type),
        default=artist_models.ArtistType.AUTHOR,
    )


class MergeArtistForm(FlaskForm):
    target_artist_id = fields.PCArtistTomSelectField(
        "Artiste Cible",
        multiple=False,
        choices=[],
        validate_choice=False,
        coerce=str,
        endpoint="backoffice_web.autocomplete_artists",
        validators=[wtforms.validators.DataRequired("Vous devez sélectionner un artiste cible.")],
    )

    def __init__(self, source_artist_id: str | None = None, *args: typing.Any, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self.source_artist_id = source_artist_id

    def validate_target_artist_id(self, field: fields.PCArtistTomSelectField) -> None:
        if field.data == self.source_artist_id:
            raise wtforms.validators.ValidationError("Un artiste ne peut pas être fusionné avec lui-même.")


class SplitArtistForm(FlaskForm):
    new_artist_name = fields.PCStringField(
        "Nom du nouvel artiste", validators=[wtforms.validators.DataRequired("Le nom est obligatoire.")]
    )
    new_artist_description = fields.PCTextareaField(
        "Description du nouvel artiste", validators=[wtforms.validators.Optional()]
    )

    new_artist_aliases = fields.PCTextareaField(
        "Alias du nouvel artiste",
        description="Séparez les alias par des virgules (,)",
        validators=[wtforms.validators.Optional()],
    )

    products_to_move = fields.PCSelectMultipleField(
        "Produits à transférer au nouvel artiste",
        coerce=int,
        validators=[wtforms.validators.DataRequired("Vous devez sélectionner au moins un produit à transférer.")],
    )

    def __init__(self, product_choices: list | None = None, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        if product_choices:
            self.products_to_move.choices = product_choices
