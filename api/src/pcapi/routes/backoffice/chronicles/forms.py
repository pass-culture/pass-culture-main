import enum
import typing

from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import Optional
from wtforms.validators import ValidationError

from pcapi.core.chronicles import models as chronicles_models
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils as forms_utils


class SearchType(enum.Enum):
    ALL = "Tout"
    CHRONICLE_CONTENT = "Uniquement le contenu des chroniques"
    PRODUCT_NAME = "Uniquement le titre des offres"


class ProductIdentifierType(enum.Enum):
    EAN = "EAN"
    ALLOCINE_ID = "ID Allociné"
    VISA = "Visa"


class GetChronicleSearchForm(forms_utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("EAN, nom de l'offre, contenu des chroniques")

    search_type = fields.PCSelectField(
        "Type de recherche",
        choices=forms_utils.choices_from_enum(SearchType),
        default=SearchType.ALL.name,
        validators=(Optional(),),
    )

    date_range = fields.PCDateRangeField("Dates", validators=(Optional(),))
    page = fields.PCHiddenField("page", default="1", validators=(Optional(),))
    limit = fields.PCLimitField(
        "Nombre maximum de résultats",
        choices=(
            (10, "Afficher 10 résultats maximum"),
            (25, "Afficher 25 résultats maximum"),
            (50, "Afficher 50 résultats maximum"),
            (100, "Afficher 100 résultats maximum"),
        ),
        default="100",
        coerce=int,
        validators=(Optional(),),
    )

    is_active = fields.PCSelectMultipleField(
        "Chronique publiée",
        choices=(("true", "Oui"), ("false", "Non")),
    )

    social_media_diffusible = fields.PCSelectMultipleField(
        "Diffusible réseaux sociaux",
        choices=[("true", "Oui"), ("false", "Non")],
    )

    category = fields.PCSelectMultipleField(
        "Club",
        choices=(
            forms_utils.choices_from_enum(
                chronicles_models.ChronicleClubType, formatter=filters.format_chronicle_club_type
            )
        ),
    )


class UpdateContentForm(forms_utils.PCForm):
    def __init__(self, *args: typing.Any, content: str | None = "", **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        if content:
            self.content.data = content

    content = fields.PCTextareaField(
        "",  # the field name hides the text when scrolling on long chronicles.
        rows=15,
        validators=(Length(min=1),),
    )


class AttachProductForm(forms_utils.PCForm):
    product_identifier_type = fields.PCSelectField(
        "Type d'identifiant",
        choices=forms_utils.choices_from_enum(
            enum_cls=chronicles_models.ChronicleProductIdentifierType,
            formatter=filters.format_chronicle_product_identifier_type,
            exclude_opts=[chronicles_models.ChronicleProductIdentifierType.OFFER_ID],
        ),
        default=chronicles_models.ChronicleProductIdentifierType.EAN.name,
    )
    product_identifier = fields.PCIntegerField(
        "Identifiant",
    )


class AttachOfferForm(forms_utils.PCForm):
    offer_id = fields.PCIntegerField(
        "ID d'offre",
    )


class CommentForm(forms_utils.PCForm):
    comment = fields.PCCommentField("Commentaire interne pour la chronique")


class CreateChronicleForm(forms_utils.PCForm):
    club_type = fields.PCSelectField(
        "Club",
        choices=(
            forms_utils.choices_from_enum(
                chronicles_models.ChronicleClubType, formatter=filters.format_chronicle_club_type
            )
        ),
        default=chronicles_models.ChronicleClubType.CINE_CLUB,
        validators=[
            DataRequired("Information obligatoire"),
        ],
    )
    email = fields.PCStringField(
        "Adresse email",
        validators=[
            DataRequired("Information obligatoire"),
            Length(min=1, max=150, message="Doit contenir entre %(min)d et %(max)d caractères"),
        ],
    )
    first_name = fields.PCStringField("Prénom")
    age = fields.PCIntegerField(
        "Age",
        validators=[
            Optional(""),
            NumberRange(min=15, max=23, message="Doit être entre %(min)d et %(max)d"),
        ],
    )
    city = fields.PCStringField(
        "Ville",
        validators=[
            Optional(""),
            Length(max=100, message="Doit contenir entre %(min)d et %(max)d caractères"),
        ],
    )
    is_identity_diffusible = fields.PCSwitchBooleanField("Accord de diffusion de l'identité")
    is_social_media_diffusible = fields.PCSwitchBooleanField("Accord de diffusion résaux sociaux")
    content = fields.PCTextareaField(
        "Texte de la chronique",
        validators=[
            DataRequired("Information obligatoire"),
            Length(min=10, max=10_000, message="Doit contenir entre %(min)d et %(max)d caractères"),
        ],
    )
    product_identifier_type = fields.PCSelectField(
        "Type d'identifiant",
        choices=forms_utils.choices_from_enum(
            enum_cls=chronicles_models.ChronicleProductIdentifierType,
            formatter=filters.format_chronicle_product_identifier_type,
        ),
        default=chronicles_models.ChronicleProductIdentifierType.EAN.name,
        validators=[
            DataRequired("Information obligatoire"),
        ],
    )
    product_identifier = fields.PCIntegerField("Identifiant")

    def validate_product_identifier(self, product_identifier_field: fields.PCStringField) -> fields.PCStringField:
        if self.product_identifier_type.data == chronicles_models.ChronicleProductIdentifierType.EAN.value:
            if not len(str(product_identifier_field.data)) == 13:
                raise ValidationError("Un EAN doit être composé de 13 chiffres")
        return product_identifier_field
