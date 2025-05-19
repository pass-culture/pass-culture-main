import typing

import wtforms
from flask_wtf import FlaskForm

from ..forms import fields


class EditProviderForm(FlaskForm):
    name = fields.PCStringField(
        "Nom du partenaire",
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.Length(min=1, max=140, message="Doit contenir moins de %(max)d caractères"),
        ),
    )
    logo_url = fields.PCOptStringField(
        "URL du logo",
        validators=(
            wtforms.validators.Optional(""),
            wtforms.validators.Length(max=1024, message="Doit contenir moins de %(max)d caractères"),
        ),
    )
    booking_external_url = fields.PCOptStringField(
        "URL de la route de validation de réservation",
        validators=(
            wtforms.validators.Optional(""),
            wtforms.validators.URL("Doit être une URL valide"),
            wtforms.validators.Length(max=1024, message="Doit contenir moins de %(max)d caractères"),
        ),
    )
    cancel_external_url = fields.PCOptStringField(
        "URL de la route d'annulation de réservation",
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
    provider_hmac_key = fields.PCOptPasswordField("Clé de signature des requêtes")
    enabled_for_pro = fields.PCSwitchBooleanField("Actif pour les pros", default="checked")
    is_active = fields.PCSwitchBooleanField("Actif", default="checked")

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.provider_hmac_key.flags.disabled = True


class CreateProviderForm(EditProviderForm):
    siren = fields.PCStringField(
        "SIREN",
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.Length(min=9, max=9, message="Doit contenir %(max)d caractères"),
        ),
    )
    city = fields.PCStringField(
        "Ville (si le SIREN n'est pas déjà enregistré)",
        validators=(
            wtforms.validators.DataRequired("Information obligatoire"),
            wtforms.validators.Length(min=1, max=140, message="Doit contenir moins de %(max)d caractères"),
        ),
    )
    postal_code = fields.PCPostalCodeField("Code postal (si le SIREN n'est pas déjà enregistré)")

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self._fields.move_to_end("postal_code", last=False)
        self._fields.move_to_end("city", last=False)
        self._fields.move_to_end("siren", last=False)
        self._fields.move_to_end("name", last=False)
        self.provider_hmac_key.flags.hidden = True
