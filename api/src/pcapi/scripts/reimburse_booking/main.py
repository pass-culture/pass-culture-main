from datetime import datetime
import json
import os

from pcapi.app import app
from pcapi.core.bookings.api import _cancel_booking
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.models import db


app.app_context().push()


def main() -> None:
    data_path = f"{os.path.dirname(os.path.abspath(__file__))}/bookings.json"
    with open(data_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    for booking in Booking.query.filter(Booking.id.in_(data["indiv"])):
        _cancel_booking(
            booking=booking,
            reason=BookingCancellationReasons.BACKOFFICE,
            cancel_even_if_used=True,
            raise_if_error=False,
            one_side_cancellation=True,
        )
    CollectiveBooking.query.filter(CollectiveBooking.id.in_(data["collective"])).update(
        {
            "cancellationDate": datetime.utcnow(),
            "cancellationReason": CollectiveBookingCancellationReasons.BACKOFFICE,
            "status": CollectiveBookingStatus.CANCELLED,
        }
    )
    db.session.commit()


main()
