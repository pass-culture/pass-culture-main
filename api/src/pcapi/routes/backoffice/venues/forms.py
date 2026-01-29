import typing

import sqlalchemy.orm as sa_orm
import wtforms
from flask_wtf import FlaskForm
from wtforms import validators

from pcapi.connectors import acceslibre as acceslibre_connector
from pcapi.core.geography import constants as geography_constants
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.models import db
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.forms.constants import area_choices
from pcapi.routes.backoffice.utils import get_regions_choices
from pcapi.routes.backoffice.utils import has_current_user_permission
from pcapi.utils import siren as siren_utils


class EditVirtualVenueForm(utils.PCForm):
    tags = fields.PCTomSelectField(
        "Tags", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_web.autocomplete_criteria"
    )
    booking_email = fields.PCEmailField("Email (notifications de réservation)")
    phone_number = fields.PCPhoneNumberField("Numéro de téléphone")  # match Venue.contact.postal_code case


class EditVenueForm(EditVirtualVenueForm):
    name = fields.PCStringField(
        "Nom juridique",
        validators=[
            validators.DataRequired("Information obligatoire"),
            validators.Length(min=1, max=140, message="doit contenir entre %(min)d et %(max)d caractères"),
        ],
    )
    public_name = fields.PCOptStringField(
        "Nom d'usage",
        validators=(wtforms.validators.Length(max=255, message="doit contenir moins de %(max)d caractères"),),
    )
    siret = fields.PCOptSiretField("SIRET")
    postal_address_autocomplete = fields.PcPostalAddressAutocomplete(
        "Adresse",
        street="street",
        ban_id="ban_id",
        insee_code="insee_code",
        city="city",
        postal_code="postal_code",
        latitude="latitude",
        longitude="longitude",
        is_manual_address="is_manual_address",
        required=True,
        has_reset=True,
        has_manual_editing=True,
        limit=10,
    )
    street = fields.PCStringField(
        "Adresse",
        initially_hidden=True,
        validators=(
            wtforms.validators.Length(
                min=1, max=200, message="L'adresse doit contenir entre %(min)d et %(max)d caractères"
            ),
        ),
    )
    postal_code = fields.PCPostalCodeField("Code postal", initially_hidden=True)  # match Address.postalCode case
    city = fields.PCStringField(
        "Ville",
        initially_hidden=True,
        validators=(
            wtforms.validators.Length(min=1, max=50, message="doit contenir entre %(min)d et %(max)d caractères"),
        ),
    )
    latitude = fields.PCStringField("Latitude", initially_hidden=True)
    longitude = fields.PCStringField("Longitude", initially_hidden=True)
    ban_id = fields.PCOptStringField(
        "Identifiant Base Adresse Nationale",
        initially_hidden=True,
        validators=(wtforms.validators.Length(max=20, message="doit contenir au maximum %(max)d caractères"),),
    )
    insee_code = fields.PCOptStringField(
        "Code INSEE",
        initially_hidden=True,
        validators=(wtforms.validators.Length(max=5, message="doit contenir au maximum %(max)d caractères"),),
    )
    is_manual_address = fields.PCOptHiddenField("Édition manuelle de l'adresse")
    is_permanent = fields.PCSwitchBooleanField("Partenaire culturel permanent")
    acceslibre_url = fields.PCOptStringField(
        "URL chez acceslibre",
        validators=(wtforms.validators.Optional(), wtforms.validators.URL()),
    )

    def __init__(self, venue: offerers_models.Venue, *args: typing.Any, **kwargs: typing.Any) -> None:
        """
        Change the fields order to avoid having the email and phone
        number (inherited from EditVirtualVenueForm) at the top.
        """
        # save venue in order to validate the siret field
        self.venue = venue

        super().__init__(*args, **kwargs)

        # self._fields is a collections.OrderedDict
        self._fields.move_to_end("booking_email")
        self._fields.move_to_end("phone_number")
        self._fields.move_to_end("acceslibre_url")
        self._fields.move_to_end("is_permanent")

    def validate_public_name(self, public_name: fields.PCOptStringField) -> fields.PCOptStringField:
        # venue.publicName is no longer nullable in the database.
        # When cleared in the form, it is reset to the same (new) value as venue.name.
        if not public_name.data:
            public_name.data = self._fields["name"].data
        return public_name

    def filter_siret(self, raw_siret: str | None) -> str | None:
        # 'siret' field is disabled when user does not have permission, so it is not sent by the web browser,
        # force to ensure that is not considered as removed.
        if raw_siret is None and not has_current_user_permission(perm_models.Permissions.MOVE_SIRET):
            return self.venue.siret
        return raw_siret

    def validate_siret(self, siret: fields.PCStringField) -> fields.PCStringField:
        if siret.data:
            if not siren_utils.is_siret_or_ridet(siret.data):
                raise validators.ValidationError("Le format du SIRET n'est pas valide")

            if siret.data[:9] != self.venue.managingOfferer.siren:
                raise validators.ValidationError(
                    "Les 9 premiers caractères du SIRET doivent correspondre au SIREN de l'entité juridique"
                )

        return siret

    def validate_latitude(self, latitude: fields.PCOptStringField) -> fields.PCOptStringField:
        try:
            float_data = float(latitude.data)
        except ValueError:
            raise validators.ValidationError("La latitude doit s'écrire en degrés décimaux")
        if not -geography_constants.MAX_LATITUDE < float_data <= geography_constants.MAX_LATITUDE:
            raise validators.ValidationError(
                f"La latitude doit être comprise entre -{geography_constants.MAX_LATITUDE} et +{geography_constants.MAX_LATITUDE}"
            )
        return latitude

    def validate_longitude(self, longitude: fields.PCOptStringField) -> fields.PCOptStringField:
        try:
            float_data = float(longitude.data)
        except ValueError:
            raise validators.ValidationError("La longitude doit s'écrire en degrés décimaux")
        if not -geography_constants.MAX_LONGITUDE <= float_data <= geography_constants.MAX_LONGITUDE:
            raise validators.ValidationError(
                f"La longitude doit être comprise entre -{geography_constants.MAX_LONGITUDE} et +{geography_constants.MAX_LONGITUDE}"
            )
        return longitude

    def validate_acceslibre_url(self, acceslibre_url: fields.PCOptStringField) -> fields.PCOptStringField:
        if acceslibre_url.data and not (
            acceslibre_url.data.startswith("https://") or acceslibre_url.data.startswith("http://")
        ):
            raise validators.ValidationError("L'URL doit commencer par https:// ou http://")
        if acceslibre_url.data and len(acceslibre_url.data.split("/")) < 5:
            raise validators.ValidationError("L'URL doit contenir au moins cinq parties séparées par '/'")
        if acceslibre_url.data and (
            acceslibre_url.data.split("/")[-2] == "" or not utils.is_slug(acceslibre_url.data.split("/")[-2])
        ):
            raise validators.ValidationError(
                "L'URL doit se terminer par /<slug-chez-acceslibre>/ (un slug n'est composé que de minuscules et de tirets du milieu)"
            )
        if not acceslibre_connector.id_exists_at_acceslibre(slug=acceslibre_url.data.split("/")[-2]):
            raise validators.ValidationError("Cette URL n'existe pas chez acceslibre")
        # TODO: (pcharlet 2025-04-04) delete this condition when removing isPermanent. Keep next condition over self.venue.isOpenToPublic is False
        if self.is_permanent.data is False and acceslibre_url.data:
            if self.venue.isOpenToPublic:
                acceslibre_url.data = None
        if self.venue.isOpenToPublic is False and acceslibre_url.data:
            raise validators.ValidationError(
                "Vous ne pouvez pas ajouter d'url à ce partenaire culturel car il n'est pas ouvert au public"
            )

        return acceslibre_url


class FraudForm(FlaskForm):
    confidence_level = fields.PCSelectField(
        "Validation des offres",
        choices=utils.choices_from_enum(
            offerers_models.OffererConfidenceLevel, formatter=filters.format_confidence_level
        ),
        default_text="Suivre les règles",
        validators=(wtforms.validators.Optional(""),),
    )
    comment = fields.PCOptCommentField("Commentaire visible uniquement par l'équipe Fraude et Conformité")

    def filter_confidence_level(self, raw_confidence_level: str | None) -> str | None:
        if not raw_confidence_level:
            return None  # instead of empty string
        return raw_confidence_level


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour le partenaire culturel")


def _get_all_venue_labels_query() -> sa_orm.Query:
    return db.session.query(offerers_models.VenueLabel).order_by(offerers_models.VenueLabel.label)


class GetVenuesListForm(utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID ou liste d'ID de partenaire culturel, nom du partenaire culturel")
    type = fields.PCSelectMultipleField(
        "Type de partenaire culturel",
        choices=utils.choices_from_enum(offerers_models.VenueTypeCode),
    )
    venue_label = fields.PCQuerySelectMultipleField(
        "Label",
        query_factory=_get_all_venue_labels_query,
        get_pk=lambda venue_label: venue_label.id,
        get_label=lambda venue_label: venue_label.label,
    )
    criteria = fields.PCTomSelectField(
        "Tags", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_web.autocomplete_criteria"
    )
    offerer = fields.PCTomSelectField(
        "Entités juridiques",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
    )
    regions = fields.PCSelectMultipleField("Régions", choices=get_regions_choices())
    department = fields.PCSelectMultipleField("Départements", choices=area_choices)
    provider = fields.PCTomSelectField(
        "Partenaire technique",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_providers",
    )
    only_validated_offerers = fields.PCSwitchBooleanField(
        "Uniquement les entités juridiques validées",
        full_row=True,
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
    order = wtforms.HiddenField(
        "order", default="desc", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("asc", "desc")))
    )

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._fields.move_to_end("q", last=False)
        if self.is_empty():
            # default value checked does not work in wtforms.BooleanField
            self.only_validated_offerers.data = True

    def is_empty(self) -> bool:
        return not any(
            (
                self.q.data,
                self.type.data,
                self.venue_label.data,
                self.criteria.data,
                self.offerer.data,
                self.regions.data,
                self.department.data,
                self.provider.data,
            )
        )


class BatchEditVenuesForm(empty_forms.BatchForm):
    criteria = fields.PCTomSelectField(
        "Tags", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_web.autocomplete_criteria"
    )
    all_permanent = fields.PCCheckboxField("Marquer tous les partenaires culturels comme permanents")
    all_not_permanent = fields.PCCheckboxField("Marquer tous les partenaires culturels comme non permanents")

    def validate_all_permanent(self, all_permanent: fields.PCCheckboxField) -> fields.PCCheckboxField:
        if all_permanent.data and self._fields["all_not_permanent"].data:
            raise wtforms.ValidationError(
                "Impossible de passer tous les partenaires culturels en permanents et non permanents"
            )

        return all_permanent


class RemovePricingPointForm(utils.PCForm):
    comment = fields.PCCommentField("Commentaire interne")
    override_revenue_check = fields.PCSwitchBooleanField(
        "Ignorer la limite de revenus annuels (accord de la comptabilité nécessaire)",
        full_row=True,
    )


class PricingPointForm(utils.PCForm):
    allow_self = True

    new_pricing_point = fields.PCSelectWithPlaceholderValueField(
        "Nouveau point de valorisation", choices=[], coerce=int
    )

    def __init__(self, venue: offerers_models.Venue, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.new_pricing_point.choices = [
            (offerer_venue.id, f"{offerer_venue.name} ({offerer_venue.siret})")
            for offerer_venue in venue.managingOfferer.managedVenues
            if offerer_venue.siret and (self.allow_self or offerer_venue.id != venue.id)
        ]


class RemoveSiretForm(RemovePricingPointForm, PricingPointForm):
    allow_self = False
    comment = fields.PCCommentField("Commentaire qui apparaîtra sur le partenaire culturel")
