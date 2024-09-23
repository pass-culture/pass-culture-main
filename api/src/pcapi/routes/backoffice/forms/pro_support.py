import typing

from flask_wtf import FlaskForm

import pcapi.routes.backoffice.forms.utils as forms_utils

from . import fields


class MoveSiretForm(FlaskForm):
    source_venue = fields.PCIntegerField(
        forms_utils.VenueRenaming("Venue ID du lieu source", "Venue ID du partenaire culturel source")
    )
    target_venue = fields.PCIntegerField(
        forms_utils.VenueRenaming("Venue ID du lieu cible", "Venue ID du partenaire culturel cible")
    )
    siret = fields.PCSiretField("SIRET")
    comment = fields.PCCommentField(
        typing.cast(
            str,
            forms_utils.VenueRenaming(
                "Commentaire associé au lieu source, sans SIRET",
                "Commentaire associé au partenaire culturel source, sans SIRET",
            ),
        )
    )
    override_revenue_check = fields.PCSwitchBooleanField("Ignorer la limite de revenus annuels")
