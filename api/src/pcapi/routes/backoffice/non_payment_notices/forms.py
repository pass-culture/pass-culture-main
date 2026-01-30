import datetime

from flask_wtf import FlaskForm
from wtforms import validators

from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils as forms_utils


class GetNoticesSearchForm(forms_utils.PCForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID ou référence de l'avis d'impayé, nom ou email de l'émetteur")

    status = fields.PCSelectMultipleField(
        "États",
        choices=forms_utils.choices_from_enum(
            offerers_models.NoticeStatus,
            formatter=filters.format_notice_status,
        ),
    )

    notice_type = fields.PCSelectMultipleField(
        "Type d'avis",
        choices=forms_utils.choices_from_enum(
            offerers_models.NoticeType,
            formatter=filters.format_notice_type,
        ),
    )

    offerer = fields.PCTomSelectField(
        "Entités juridiques",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_offerers",
    )

    venue = fields.PCTomSelectField(
        "Partenaires culturels",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_pricing_points",
    )

    batch = fields.PCTomSelectField(
        "N° de virement",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_cashflow_batches",
    )

    limit = fields.PCLimitField(
        "Nombre maximum de résultats",
        choices=(
            (100, "Afficher 100 résultats maximum"),
            (500, "Afficher 500 résultats maximum"),
            (1000, "Afficher 1000 résultats maximum"),
        ),
        default="100",
        coerce=int,
        validators=(validators.Optional(),),
    )

    from_to_date = fields.PCDateRangeField(
        "Reçus entre",
        validators=(validators.Optional(),),
        max_date=datetime.date.today(),
        reset_to_blank=True,
    )

    def is_empty(self) -> bool:
        return not any(
            (
                self.q.data,
                self.status.data,
                self.notice_type.data,
                self.offerer.data,
                self.venue.data,
                self.batch.data,
                self.from_to_date.data,
            )
        )


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
    fees = fields.PCDecimalField(
        "Montant des frais (inclus dans le montant total)",
        use_locale=True,
        validators=[
            validators.Optional(),
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
        "Partenaire culturel",
        multiple=False,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_venues",
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


class EditNonPaymentNoticeForm(CreateNonPaymentNoticeForm):
    pass


class SetPendingForm(FlaskForm):
    motivation = fields.PCSelectField(
        "Motif",
        choices=forms_utils.choices_from_enum(
            offerers_models.NoticeStatusMotivation,
            formatter=filters.format_notice_status_motivation,
            exclude_opts=(
                offerers_models.NoticeStatusMotivation.ALREADY_PAID,
                offerers_models.NoticeStatusMotivation.REJECTED,
                offerers_models.NoticeStatusMotivation.NO_LINKED_BANK_ACCOUNT,
            ),
        ),
    )


class CloseForm(FlaskForm):
    motivation = fields.PCSelectField(
        "Motif",
        choices=forms_utils.choices_from_enum(
            offerers_models.NoticeStatusMotivation,
            formatter=filters.format_notice_status_motivation,
            exclude_opts=(
                offerers_models.NoticeStatusMotivation.OFFERER_NOT_FOUND,
                offerers_models.NoticeStatusMotivation.PRICE_NOT_FOUND,
            ),
        ),
    )
    recipient = fields.PCSelectField(
        "Destinataire", choices=forms_utils.choices_from_enum(offerers_models.NoticeRecipientType)
    )
    batch = fields.PCTomSelectField(
        "N° de virement",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_web.autocomplete_cashflow_batches",
        validators=[validators.InputRequired("Information obligatoire")],
    )
