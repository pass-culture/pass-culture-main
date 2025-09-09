import enum
import re
import typing
import urllib.parse

import wtforms
from flask_wtf import FlaskForm

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import search as search_forms
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.forms.constants import area_choices

from .utils import CONNECT_AS_OBJECT_TYPES


DIGITS_AND_WHITESPACES_REGEX = re.compile(r"^[\d\s]+$")


class TypeOptions(enum.Enum):
    OFFERER = "offerer"
    VENUE = "venue"
    USER = "user"
    BANK_ACCOUNT = "bank-account"


def format_search_type_options(type_option: TypeOptions) -> str:
    match type_option:
        case TypeOptions.OFFERER:
            return "Entité juridique"
        case TypeOptions.VENUE:
            return "Partenaire culturel"
        case TypeOptions.USER:
            return "Compte pro"
        case TypeOptions.BANK_ACCOUNT:
            return "Compte bancaire"
        case _:
            return type_option.value


class ProSearchForm(search_forms.SearchForm):
    pro_type = fields.PCSelectField(
        "Type",
        choices=utils.choices_from_enum(TypeOptions, format_search_type_options),
        default=TypeOptions.OFFERER,
    )
    departments = fields.PCSelectMultipleField("Départements", choices=area_choices, full_row=True)

    def filter_q(self, q: str | None) -> str | None:
        # Remove spaces from SIREN, SIRET and IDs
        if q and DIGITS_AND_WHITESPACES_REGEX.match(q):
            return re.sub(r"\s+", "", q)
        return q

    def validate_pro_type(self, pro_type: fields.PCSelectField) -> fields.PCSelectField:
        try:
            pro_type.data = TypeOptions[pro_type.data]
        except KeyError:
            raise wtforms.validators.ValidationError("Le type sélectionné est invalide")
        return pro_type


class CompactProSearchForm(ProSearchForm):
    # Compact form on top of search results and details pages
    departments = fields.PCSelectMultipleField("Départements", choices=area_choices, search_inline=True)


class CreateVenueWithoutSIRETForm(FlaskForm):
    public_name = fields.PCStringField(
        "Nom d'usage du partenaire culturel",
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.Length(max=255, message="doit contenir au maximum %(max)d caractères"),
        ),
    )
    attachement_venue = fields.PCSelectWithPlaceholderValueField("SIRET de rattachement", choices=[], coerce=int)

    def __init__(self, offerer: offerers_models.Offerer, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.attachement_venue.choices = [
            (offerer_venue.id, f"{offerer_venue.siret} ({offerer_venue.common_name})")
            for offerer_venue in offerer.managedVenues
            if offerer_venue.siret
        ]


class ConnectAsForm(FlaskForm):
    object_id = fields.PCHiddenField()
    object_type = fields.PCHiddenField()
    redirect = fields.PCHiddenField(
        validators=[
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.Length(min=1, max=512, message="doit contenir entre %(min)d et %(max)d caractères"),
        ],
    )

    def validate_object_type(self, object_type: fields.PCHiddenField) -> fields.PCHiddenField:
        if object_type.data not in CONNECT_AS_OBJECT_TYPES:
            raise wtforms.validators.ValidationError("object type invalide")
        return object_type

    def validate_redirect(self, redirect: fields.PCHiddenField) -> fields.PCHiddenField:
        if not redirect.data.startswith("/"):
            raise wtforms.validators.ValidationError("doit être un chemin commençant par /")
        redirect.data = urllib.parse.quote(redirect.data, safe="/?=&")
        return redirect
