from typing import List, Dict

from flask import json, jsonify

from domain.booking_recap.booking_recap import BookingRecap
from utils.date import format_into_ISO_8601


def serialize_bookings_recap(bookings_recap: List[BookingRecap]) -> json:
    return jsonify([__serialize_booking_recap(booking_recap) for booking_recap in bookings_recap])


def __serialize_booking_recap(booking_recap: BookingRecap) -> Dict:
    return {
        "stock": {
            "offer_name": booking_recap.offer_name,
        },
        "beneficiary": {
            "lastname": booking_recap.beneficiary_lastname,
            "firstname": booking_recap.beneficiary_firstname,
            "email": booking_recap.beneficiary_email,
        },
        "booking_token": booking_recap.booking_token,
        "booking_date": format_into_ISO_8601(booking_recap.booking_date),
    }
