from flask_wtf import FlaskForm
from wtforms import validators

from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils as forms_utils


class CreateNonPaymentNoticeForm(FlaskForm):
    class Meta:
        locales = ["fr_FR", "fr"]

    date_received = fields.PCDateField("Date de réception de l'avis")

    notice_type = fields.PCSelectField(
        "Type d'avis",
        choices=forms_utils.choices_from_enum(offerers_models.NoticeType, formatter=filters.format_notice_type),
    )

    amount = fields.PCDecimalField(
        "Montant",
        use_locale=True,
        validators=[
            validators.DataRequired("Information obligatoire"),
            validators.NumberRange(min=0, message="Doit contenir un nombre positif"),
        ],
    )

    reference = fields.PCStringField("Référence")
    emitter_name = fields.PCStringField("Nom de l'émetteur")
    emitter_email = fields.PCEmailField("Adresse email de l'émetteur")

    offerer = fields.PCTomSelectField(
        "Entité juridique",
        multiple=False,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
    )
    venue = fields.PCTomSelectField(
        "Partenaire culturel (avec SIRET)",
        multiple=False,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_pricing_points",
    )

    def validate(self, extra_validators: dict | None = None) -> bool:
        offerer_id = self.offerer.data[0] if (self.offerer.data and self.offerer.data[0]) else None
        venue_id = self.venue.data[0] if (self.venue.data and self.venue.data[0]) else None

        if offerer_id and venue_id:
            if int(offerer_id) != (
                db.session.query(offerers_models.Venue)
                .filter(offerers_models.Venue.id == venue_id)
                .one()
                .managingOffererId
            ):
                self.venue.errors = ["Le partenaire culturel doit être sur l'entité juridique sélectionnée"]
                return False

        if not offerer_id and venue_id:
            self.offerer.data = [
                (
                    db.session.query(offerers_models.Venue)
                    .filter(offerers_models.Venue.id == venue_id)
                    .one()
                    .managingOffererId
                )
            ]

        return super().validate(extra_validators)
