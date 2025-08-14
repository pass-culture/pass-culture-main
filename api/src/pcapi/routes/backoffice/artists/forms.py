import enum
import typing

import wtforms
from flask_wtf import FlaskForm

from pcapi.core.artist import models as artist_models
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils


class ArtistEditForm(FlaskForm):
    name = fields.PCStringField("Nom de l'artiste")
    description = fields.PCTextareaField("Description")


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
        choices=utils.choices_from_enum(ProductIdentifierTypeEnum, format_product_identifier_type),
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
        choices=utils.choices_from_enum(artist_models.ArtistType, format_artist_type),
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
