from typing import List, Dict

from flask import json, jsonify

from domain.booking_recap.booking_recap import BookingRecap, EventBookingRecap
from utils.date import format_into_ISO_8601


def serialize_bookings_recap(bookings_recap: List[BookingRecap]) -> json:
    return jsonify([__serialize_booking_recap(booking_recap) for booking_recap in bookings_recap])


def __serialize_booking_recap(booking_recap: BookingRecap) -> Dict:
    serialized_booking_recap = {
        "stock": {
            "type": "thing",
            "offer_name": booking_recap.offer_name,
        },
        "beneficiary": {
            "lastname": booking_recap.beneficiary_lastname,
            "firstname": booking_recap.beneficiary_firstname,
            "email": booking_recap.beneficiary_email,
        },
        "booking_token": booking_recap.booking_token,
        "booking_date": format_into_ISO_8601(booking_recap.booking_date),
        "booking_status": booking_recap.booking_status.value,
        "booking_is_duo": booking_recap.booking_is_duo,
    }

    if isinstance(booking_recap, EventBookingRecap):
        serialized_booking_recap['stock']['type'] = "event"
        serialized_booking_recap['stock']['event_beginning_datetime'] = format_into_ISO_8601(
            booking_recap.event_beginning_datetime)

    return serialized_booking_recap
