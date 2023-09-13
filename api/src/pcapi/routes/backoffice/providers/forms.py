from flask_wtf import FlaskForm
import wtforms

from ..forms import fields


class CreateProviderForm(FlaskForm):
    name = fields.PCStringField(
        "Nom du partenaire",
        validators=(
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.Length(min=1, max=140, message="Doit contenir moins de %(max)d caractères"),
        ),
    )
    siren = fields.PCStringField(
        "SIREN",
        validators=(
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.Length(min=9, max=9, message="Doit contenir %(max)d caractères"),
        ),
    )
    city = fields.PCStringField(
        "Ville (si le SIREN n'est pas déjà enregistré)",
        validators=(
            wtforms.validators.InputRequired("Information obligatoire"),
            wtforms.validators.Length(min=1, max=140, message="Doit contenir moins de %(max)d caractères"),
        ),
    )
    postal_code = fields.PCPostalCodeField("Code postal (si le SIREN n'est pas déjà enregistré)")
    logo_url = fields.PCOptStringField(
        "URL du logo",
        validators=(
            wtforms.validators.Optional(""),
            wtforms.validators.Length(max=1024, message="Doit contenir moins de %(max)d caractères"),
        ),
    )
    booking_external_url = fields.PCOptStringField(
        "URL de la route de validation de reservation",
        validators=(
            wtforms.validators.Optional(""),
            wtforms.validators.URL("Doit être une URL valide"),
            wtforms.validators.Length(max=1024, message="Doit contenir moins de %(max)d caractères"),
        ),
    )
    cancel_external_url = fields.PCOptStringField(
        "URL de la route d'annulation de reservation",
        validators=(
            wtforms.validators.Optional(""),
            wtforms.validators.URL("Doit être une URL valide"),
            wtforms.validators.Length(max=1024, message="Doit contenir moins de %(max)d caractères"),
        ),
    )
    notification_external_url = fields.PCOptStringField(
        "URL de la route de notification de nouvelles réservations ou d'annulation de réservations",
        validators=(
            wtforms.validators.Optional(""),
            wtforms.validators.URL("Doit être une URL valide"),
            wtforms.validators.Length(max=1024, message="Doit contenir moins de %(max)d caractères"),
        ),
    )
    enabled_for_pro = fields.PCSwitchBooleanField("Actif pour les pros", default="checked")
    is_active = fields.PCSwitchBooleanField("Actif", default="checked")


class EditProviderForm(CreateProviderForm):
    city = None  # type: ignore [assignment]
    postal_code = None  # type: ignore [assignment]
    siren = None  # type: ignore [assignment]
