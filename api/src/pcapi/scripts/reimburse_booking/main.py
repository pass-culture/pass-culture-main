from datetime import datetime
import json
import os

from pcapi.app import app
from pcapi.core.bookings.api import _cancel_booking
from pcapi.core.bookings.api import mark_as_unused
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.finance.repository import has_reimbursement
from pcapi.core.offers import repository as offers_repository
from pcapi.models import db
from pcapi.repository import repository
from pcapi.repository import transaction


app.app_context().push()


def main() -> None:
    data_path = f"{os.path.dirname(os.path.abspath(__file__))}/bookings.json"
    with open(data_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    for booking in Booking.query.filter(Booking.id.in_(data["indiv"])):
        if has_reimbursement(booking):
            with transaction():
                stock = offers_repository.get_and_lock_stock(stock_id=booking.stockId)
                booking.cancellationDate = datetime.utcnow()
                booking.cancellationReason = BookingCancellationReasons.BACKOFFICE
                booking.status = BookingStatus.CANCELLED
                stock.dnBookedQuantity -= booking.quantity
                repository.save(booking, stock)
        else:
            mark_as_unused(booking)
            _cancel_booking(booking, BookingCancellationReasons.BACKOFFICE)

    CollectiveBooking.query.filter(CollectiveBooking.id.in_(data["collective"])).update(
        {
            "cancellationDate": datetime.utcnow(),
            "cancellationReason": CollectiveBookingCancellationReasons.BACKOFFICE,
            "status": CollectiveBookingStatus.CANCELLED,
        }
    )
    db.session.commit()


main()
