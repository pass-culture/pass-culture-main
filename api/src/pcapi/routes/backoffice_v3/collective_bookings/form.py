import datetime

from flask_wtf import FlaskForm
import wtforms

from pcapi.core.categories import categories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.routes.backoffice_v3 import filters
from pcapi.routes.backoffice_v3.forms import fields
from pcapi.routes.backoffice_v3.forms import utils


class GetCollectiveBookingListForm(FlaskForm):
    class Meta:
        csrf = False

    q = fields.PCOptSearchField("ID réservation collective, ID offre, Nom ou ID de l'établissement")
    offerer = fields.PCTomSelectField(
        "Structures",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_v3_web.autocomplete_offerers",
    )
    venue = fields.PCTomSelectField(
        "Lieux", multiple=True, choices=[], validate_choice=False, endpoint="backoffice_v3_web.autocomplete_venues"
    )
    category = fields.PCSelectMultipleField(
        "Catégories", choices=utils.choices_from_enum(categories.CategoryIdLabelEnum)
    )
    status = fields.PCSelectMultipleField(
        "États", choices=utils.choices_from_enum(CollectiveBookingStatus, formatter=filters.format_booking_status)
    )
    cashflow_batches = fields.PCTomSelectField(
        "Virements",
        multiple=True,
        choices=[],
        validate_choice=False,
        endpoint="backoffice_v3_web.autocomplete_cashflow_batches",
    )
    from_date = fields.PCDateField("À partir du", validators=(wtforms.validators.Optional(),))
    to_date = fields.PCDateField("Jusqu'au", validators=(wtforms.validators.Optional(),))
    event_from_date = fields.PCDateField("Événement du", validators=(wtforms.validators.Optional(),))
    event_to_date = fields.PCDateField("Événement jusqu'au", validators=(wtforms.validators.Optional(),))
    limit = fields.PCSelectField(
        "Nombre maximum",
        choices=((20, "20"), (100, "100"), (500, "500"), (1000, "1000")),
        default="100",
        coerce=int,
        validators=(wtforms.validators.Optional(),),
    )

    def is_empty(self) -> bool:
        return not any(
            (
                self.q.data,
                self.offerer.data,
                self.venue.data,
                self.category.data,
                self.status.data,
                self.from_date.data,
                self.to_date.data,
                self.event_from_date.data,
                self.event_to_date.data,
                self.cashflow_batches.data,
            )
        )

    @property
    def pro_view_args(self) -> str:
        output = ""
        if len(self.venue.data) == 1 and not any(
            (
                self.q.data,
                self.offerer.data,
                self.category.data,
                self.status.data,
                self.event_from_date.data,
                self.event_to_date.data,
                self.cashflow_batches.data,
            )
        ):
            from_date = self.from_date.data if self.from_date.data else datetime.date.today()
            to_date = self.to_date.data if self.to_date.data else from_date - datetime.timedelta(days=30)
            output = (
                f"?page=1&bookingBeginningDate={str(from_date)}&bookingEndingDate={str(to_date)}&bookingStatusFilter=booked"
                f"&bookingStatusFilter=booked&offerType=all&offerVenueId={self.venue.data[0]}"
            )
        return output


class GetDownloadBookingsForm(FlaskForm):
    class Meta:
        csrf = False

    venue = fields.PCIntegerField("Lieux")
    from_date = fields.PCDateField("À partir du", validators=(wtforms.validators.Optional(),))
    to_date = fields.PCDateField("Jusqu'au", validators=(wtforms.validators.Optional(),))


class CancelBookingForm(FlaskForm):
    reason = fields.PCSelectWithPlaceholderValueField(
        "Raison",
        choices=utils.choices_from_enum(
            educational_models.CollectiveBookingCancellationReasons,
            formatter=filters.format_booking_cancellation_reason,
        ),
    )
