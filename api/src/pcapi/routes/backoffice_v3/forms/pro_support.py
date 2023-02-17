from flask_wtf import FlaskForm
import wtforms

from . import fields


class MoveSiretForm(FlaskForm):
    source_venue = fields.PCIntegerField("Venue ID du lieu source")
    target_venue = fields.PCIntegerField("Venue ID du lieu cible")
    siret = fields.PCStringField(
        "SIRET",
        validators=[
            wtforms.validators.InputRequired("SIRET obligatoire"),
            wtforms.validators.Length(min=14, max=14, message="Le SIRET doit contenir exactement %(min)d chiffres"),
            wtforms.validators.Regexp(r"^\d{14}$", message="Le SIRET doit contenir exactement 14 chiffres"),
        ],
    )
    comment = fields.PCCommentField("Commentaire associé au lieu source, sans SIRET")
    override_revenue_check = fields.PCSwitchBooleanField("Ignorer la limite de revenus annuels")
