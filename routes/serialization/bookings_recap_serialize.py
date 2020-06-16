from typing import Dict

from flask import json

from domain.booking_recap.booking_recap import BookingRecap, EventBookingRecap, BookBookingRecap
from domain.booking_recap.bookings_recap_paginated import BookingsRecapPaginated
from utils.date import format_into_ISO_8601_with_timezone
from utils.human_ids import humanize


def serialize_bookings_recap_paginated(bookings_recap_paginated: BookingsRecapPaginated) -> json:
    return {
        'bookings_recap': [__serialize_booking_recap(booking_recap) for booking_recap in
                           bookings_recap_paginated.bookings_recap],
        'page': bookings_recap_paginated.page,
        'pages': bookings_recap_paginated.pages,
        'total': bookings_recap_paginated.total
    }


def __serialize_booking_recap(booking_recap: BookingRecap) -> Dict:
    serialized_booking_recap = {
        "stock": {
            "type": "thing",
            "offer_name": booking_recap.offer_name,
            "offer_identifier": humanize(booking_recap.offer_identifier),
        },
        "beneficiary": {
            "lastname": booking_recap.beneficiary_lastname,
            "firstname": booking_recap.beneficiary_firstname,
            "email": booking_recap.beneficiary_email,
        },
        "booking_token": booking_recap.booking_token,
        "booking_date": format_into_ISO_8601_with_timezone(booking_recap.booking_date),
        "booking_status": booking_recap.booking_status.value,
        "booking_is_duo": booking_recap.booking_is_duo,
        "venue_identifier": humanize(booking_recap.venue_identifier),
        "booking_amount": booking_recap.booking_amount,
        "booking_recap_history": booking_recap.booking_recap_history.__dict__
    }

    if isinstance(booking_recap, EventBookingRecap):
        serialized_booking_recap['stock']['type'] = "event"
        serialized_booking_recap['stock']['event_beginning_datetime'] = format_into_ISO_8601_with_timezone(
            booking_recap.event_beginning_datetime)

    if isinstance(booking_recap, BookBookingRecap):
        serialized_booking_recap['stock']['type'] = "book"
        serialized_booking_recap['stock']['offer_isbn'] = booking_recap.offer_isbn

    return serialized_booking_recap
