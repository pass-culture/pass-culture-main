import enum
import re
import typing

from flask_wtf import FlaskForm
import wtforms

from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.connectors.entreprise import models as sirene_models
from pcapi.connectors.entreprise import sirene
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.repository import find_offerer_by_siren
from pcapi.core.users import models as users_models
from pcapi.core.users.repository import find_pro_or_non_attached_pro_user_by_email_query
from pcapi.models.feature import FeatureToggle
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import search as search_forms
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.forms.constants import area_choices


DIGITS_AND_WHITESPACES_REGEX = re.compile(r"^[\d\s]+$")


class TypeOptions(enum.Enum):
    OFFERER = "offerer"
    VENUE = "venue"
    USER = "user"
    BANK_ACCOUNT = "bank-account"


def format_search_type_options(type_option: TypeOptions) -> str:
    match type_option:
        case TypeOptions.OFFERER:
            return "Structure"
        case TypeOptions.VENUE:
            return "Lieu"
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

    # We can't use exclude_opts in pro_type definition because choices would not be updated when changing the value of
    # WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY. This init function can be removed at the same time as the feature flag.
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        if not FeatureToggle.WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY.is_active():
            self.pro_type.choices = [
                choice for choice in self.pro_type.choices if choice[0] != TypeOptions.BANK_ACCOUNT.name
            ]


class CompactProSearchForm(ProSearchForm):
    # Compact form on top of search results and details pages
    departments = fields.PCSelectMultipleField("Départements", choices=area_choices, search_inline=True)


class CreateOffererForm(FlaskForm):
    email = fields.PCEmailField("Adresse email du compte pro")
    siret = fields.PCSiretField("SIRET")
    public_name = fields.PCStringField(
        "Nom d'usage du lieu",
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.Length(max=255, message="doit contenir au maximum %(max)d caractères"),
        ),
    )
    venue_type_code = fields.PCSelectWithPlaceholderValueField(
        "Activité principale", choices=utils.choices_from_enum(offerers_models.VenueTypeCode)
    )
    web_presence = fields.PCOptStringField(
        "Site internet, réseau social",
        validators=(wtforms.validators.Length(max=255, message="doit contenir au maximum %(max)d caractères"),),
    )
    target = fields.PCSelectWithPlaceholderValueField(
        "Offres ciblées",
        choices=utils.choices_from_enum(offerers_models.Target, formatter=filters.format_venue_target),
    )
    ds_id = fields.PCIntegerField("N° Dossier Démarches Simplifiées")

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._user: users_models.User | None = None
        self._siret_info: sirene_models.SiretInfo | None = None

    @property
    def user(self) -> users_models.User:
        assert self._user, "user has not been validated"
        return self._user

    @property
    def siret_info(self) -> sirene_models.SiretInfo:
        assert self._siret_info, "siret has not been validated"
        return self._siret_info

    def validate_email(self, email: fields.PCEmailField) -> fields.PCEmailField:
        if email.data:
            self._user = find_pro_or_non_attached_pro_user_by_email_query(email.data).one_or_none()
            if not self._user:
                raise wtforms.validators.ValidationError(f"Aucun compte pro n'existe avec l'adresse {email.data}")
        return email

    def validate_siret(self, siret: fields.PCSiretField) -> fields.PCSiretField:
        if siret.data and len(siret.data) == 14 and siret.data.isnumeric():
            siren = siret.data[:9]
            if find_offerer_by_siren(siren):
                raise wtforms.validators.ValidationError(f"Une structure existe déjà avec le SIREN {siren}")

            try:
                siret_info = sirene.get_siret(siret.data, raise_if_non_public=False)
            except sirene_exceptions.UnknownEntityException:
                raise wtforms.validators.ValidationError(f"Le SIRET {siret.data} n'existe pas")
            except sirene_exceptions.ApiException:
                raise wtforms.validators.ValidationError("Une erreur s'est produite lors de l'appel à l'API Sirene")

            if not siret_info.active:
                raise wtforms.validators.ValidationError(f"L'établissement portant le SIRET {siret.data} est fermé")
            if siret_info.diffusible:
                raise wtforms.validators.ValidationError(
                    f"L'établissement portant le SIRET {siret.data} est diffusible, l'acteur culturel peut créer la structure sur PC Pro"
                )
            self._siret_info = siret_info

        return siret
