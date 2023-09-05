import typing

from flask_wtf import FlaskForm

from pcapi.core.educational import models as educational_models
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.routes.backoffice_v3 import filters
from pcapi.routes.backoffice_v3.bookings.form import BaseBookingListForm
from pcapi.routes.backoffice_v3.forms import fields
from pcapi.routes.backoffice_v3.forms import utils


class GetCollectiveBookingListForm(BaseBookingListForm):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.q.label.text = "ID réservation collective, ID offre, Nom ou ID de l'établissement"
        self.status.choices = utils.choices_from_enum(CollectiveBookingStatus, formatter=filters.format_booking_status)


class CancelBookingForm(FlaskForm):
    reason = fields.PCSelectWithPlaceholderValueField(
        "Raison",
        choices=utils.choices_from_enum(
            educational_models.CollectiveBookingCancellationReasons,
            formatter=filters.format_booking_cancellation_reason,
        ),
    )
