import typing

from flask_wtf import FlaskForm
import sqlalchemy as sa
import wtforms
from wtforms import validators

import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.permissions import models as perm_models
from pcapi.routes.backoffice_v3.utils import get_regions_choices
from pcapi.routes.backoffice_v3.utils import has_current_user_permission

from . import fields
from . import utils
from ..forms import empty as empty_forms
from .constants import area_choices


class EditVirtualVenueForm(utils.PCForm):
    tags = fields.PCTomSelectField(
        "Tags", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_criteria"
    )
    booking_email = fields.PCEmailField("Email (notifications de réservation)")
    phone_number = fields.PCPhoneNumberField("Numéro de téléphone")  # match Venue.contact.postal_code case


class EditVenueForm(EditVirtualVenueForm):
    name = fields.PCStringField(
        "Nom juridique",
        validators=(wtforms.validators.Length(max=140, message="doit contenir moins de %(max)d caractères"),),
    )
    public_name = fields.PCOptStringField(
        "Nom d'usage",
        validators=(wtforms.validators.Length(max=255, message="doit contenir moins de %(max)d caractères"),),
    )
    siret = fields.PCOptStringField("siret")
    postal_address_autocomplete = fields.PcPostalAddressAutocomplete(
        "Adresse",
        address="address",
        city="city",
        postal_code="postal_code",
        latitude="latitude",
        longitude="longitude",
        required=True,
        has_reset=True,
        has_manual_editing=True,
        limit=10,
    )
    address = fields.PCHiddenField(
        "Adresse",
        validators=(wtforms.validators.Length(max=200, message="doit contenir moins de %(max)d caractères"),),
    )
    city = fields.PCHiddenField(
        "Ville",
        validators=(
            wtforms.validators.Length(min=1, max=50, message="doit contenir entre %(min)d et %(max)d caractères"),
        ),
    )
    postal_code = fields.PCPostalCodeHiddenField("Code postal")  # match Venue.postalCode case
    latitude = fields.PCOptHiddenField("Latitude")
    longitude = fields.PCOptHiddenField("Longitude")
    is_permanent = fields.PCSwitchBooleanField("Lieu permanent")

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
        self._fields.move_to_end("is_permanent")

    def filter_siret(self, raw_siret: str | None) -> str | None:
        # 'siret' field is disabled when user does not have permission, so it is not sent by the web browser,
        # force to ensure that is not considered as removed.
        if raw_siret is None and not has_current_user_permission(perm_models.Permissions.MOVE_SIRET):
            return self.venue.siret
        return raw_siret

    def validate_siret(self, siret: fields.PCStringField) -> fields.PCStringField:
        if siret.data:
            if len(siret.data) != 14:
                raise validators.ValidationError("Un siret doit comporter 14 chiffres")

            try:
                int(siret.data)
            except (ValueError, TypeError):
                raise validators.ValidationError("Un siret doit comporter 14 chiffres")

            if siret.data[:9] != self.venue.managingOfferer.siren:
                raise validators.ValidationError(
                    "Les 9 premiers caractères du SIRET doivent correspondre au SIREN de la structure"
                )

        return siret


class CommentForm(FlaskForm):
    comment = fields.PCCommentField("Commentaire interne pour le lieu")


def _get_all_venue_labels_query() -> sa.orm.Query:
    return offerers_models.VenueLabel.query.order_by(offerers_models.VenueLabel.label)


class GetVenuesListForm(utils.PCForm):
    class Meta:
        csrf = False

    type = fields.PCSelectMultipleField("Type de lieu", choices=utils.choices_from_enum(VenueTypeCode))
    venue_label = fields.PCQuerySelectMultipleField(
        "Label",
        query_factory=_get_all_venue_labels_query,
        get_pk=lambda venue_label: venue_label.id,
        get_label=lambda venue_label: venue_label.label,
    )
    criteria = fields.PCTomSelectField(
        "Tags", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_criteria"
    )
    regions = fields.PCSelectMultipleField("Régions", choices=get_regions_choices())
    department = fields.PCSelectMultipleField("Départements", choices=area_choices)
    limit = fields.PCSelectField(
        "Nombre maximum",
        choices=((100, "100"), (500, "500"), (1000, "1000"), (3000, "3000")),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )
    order = wtforms.HiddenField(
        "order", default="desc", validators=(wtforms.validators.Optional(), wtforms.validators.AnyOf(("asc", "desc")))
    )

    def is_empty(self) -> bool:
        return not any(
            (
                self.type.data,
                self.venue_label.data,
                self.criteria.data,
                self.regions.data,
                self.department.data,
            )
        )


class BatchEditVenuesForm(empty_forms.BatchForm):
    criteria = fields.PCTomSelectField(
        "Tags", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_criteria"
    )
    all_permanent = fields.PCCheckboxField("Marquer tous les lieux comme permanents")
    all_not_permanent = fields.PCCheckboxField("Marquer tous les lieux comme non permanents")

    def validate_all_permanent(self, all_permanent: fields.PCCheckboxField) -> fields.PCCheckboxField:
        if all_permanent.data and self._fields["all_not_permanent"].data:
            raise wtforms.ValidationError("Impossible de passer tous les lieux en permanents et non permanents")

        return all_permanent
