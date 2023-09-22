import typing

from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.routes.backoffice import filters
from pcapi.routes.backoffice.bookings.form import BaseBookingListForm
from pcapi.routes.backoffice.forms import utils


class GetCollectiveBookingListForm(BaseBookingListForm):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.q.label.text = "ID réservation collective, ID offre, Nom ou ID de l'établissement"
        self.status.choices = utils.choices_from_enum(CollectiveBookingStatus, formatter=filters.format_booking_status)
