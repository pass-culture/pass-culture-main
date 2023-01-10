import typing

from flask_wtf import FlaskForm
from wtforms import validators

import pcapi.core.offerers.models as offerers_models

from . import fields
from . import utils


class EditVirtualVenueForm(utils.PCForm):
    email = fields.PCEmailField("Email")
    phone_number = fields.PCPhoneNumberField("Numéro de téléphone")  # match Venue.contact.postal_code case


class EditVenueForm(EditVirtualVenueForm):
    siret = fields.PCStringField("siret")
    city = fields.PCStringField("Ville")
    postalCode = fields.PCPostalCodeField("Code postal")  # match Venue.postalCode case
    address = fields.PCStringField("Adresse")
    isPermanent = fields.PCSwitchBooleanField("Lieu permanent")

    def __init__(self, venue: offerers_models.Venue, *args: typing.Any, **kwargs: typing.Any) -> None:
        """
        Change the fields order to avoid having the email and phone
        number (inherited from EditVirtualVenueForm) at the top.
        """
        super().__init__(*args, **kwargs)

        # save venue in order to validate the siret field
        self.venue = venue

        # self._fields is a collections.OrderedDict
        self._fields.move_to_end("email")
        self._fields.move_to_end("phone_number")
        self._fields.move_to_end("isPermanent")

    def validate_siret(self, siret: fields.PCStringField) -> fields.PCStringField:
        if not siret.data or len(siret.data) != 14:
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
