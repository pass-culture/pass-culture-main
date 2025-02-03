from flask_wtf import FlaskForm

from . import fields


class MoveSiretForm(FlaskForm):
    source_venue = fields.PCIntegerField("Venue ID du partenaire culturel source")
    target_venue = fields.PCIntegerField("Venue ID du partenaire culturel cible")
    siret = fields.PCSiretField("SIRET")
    comment = fields.PCCommentField("Commentaire associé au partenaire culturel source, sans SIRET")
    override_revenue_check = fields.PCSwitchBooleanField("Ignorer la limite de revenus annuels")
