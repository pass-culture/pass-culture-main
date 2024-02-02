from flask_wtf import FlaskForm

from . import fields


class MoveSiretForm(FlaskForm):
    source_venue = fields.PCIntegerField("Venue ID du lieu source")
    target_venue = fields.PCIntegerField("Venue ID du lieu cible")
    siret = fields.PCSiretField("SIRET")
    comment = fields.PCCommentField("Commentaire associé au lieu source, sans SIRET")
    override_revenue_check = fields.PCSwitchBooleanField("Ignorer la limite de revenus annuels")
