import typing

from flask_wtf import FlaskForm

from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings.models import BookingStatus
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.bookings.form import BaseBookingListForm
from pcapi.routes.backoffice.forms import fields
from pcapi.routes.backoffice.forms import utils
from pcapi.routes.backoffice.forms.empty import BatchForm


class GetIndividualBookingListForm(BaseBookingListForm):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.q.label.text = "Code contremarque, Nom, email ou ID (offre, bénéficiaire ou résa)"
        self.status.choices = utils.choices_from_enum(BookingStatus, formatter=filters.format_booking_status)


class CancelBookingForm(FlaskForm):
    reason = fields.PCSelectWithPlaceholderValueField(
        "Raison",
        choices=utils.choices_from_enum(
            bookings_models.BookingCancellationReasons, formatter=filters.format_booking_cancellation_reason
        ),
    )


class BatchCancelBookingForm(BatchForm, CancelBookingForm):
    pass
