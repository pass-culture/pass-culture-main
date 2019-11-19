from typing import List

from models import Recommendation, Booking, User
from repository import booking_queries
from routes.serialization import as_dict
from utils.human_ids import dehumanize
from utils.includes import RECOMMENDATION_INCLUDES, WEBAPP_GET_BOOKING_INCLUDES


def serialize_recommendations(recommendations: List[Recommendation], user: User) -> dict:
    serialized_recommendations = [serialize_recommendation(recommendation, user, query_booking=False)
                                  for recommendation in recommendations]
    bookings = booking_queries.find_for_my_bookings_page(user.id)
    bookings_by_offer = _get_bookings_by_offer(bookings)
    for serialized_recommendation in serialized_recommendations:
        offer_id = dehumanize(serialized_recommendation["offerId"])
        if offer_id in bookings_by_offer:
            bookings_for_recommendation = bookings_by_offer[offer_id]
        else:
            bookings_for_recommendation = []
        serialized_recommendation['bookings'] = _serialize_bookings(bookings_for_recommendation)

    return serialized_recommendations


def serialize_recommendation(recommendation: Recommendation, user: User, query_booking: bool = True) -> dict:
    serialized_recommendation = as_dict(recommendation, includes=RECOMMENDATION_INCLUDES)
    if query_booking and recommendation.offer:
        bookings = booking_queries.find_from_recommendation(recommendation, user)
        serialized_recommendation['bookings'] = _serialize_bookings(bookings)
    return serialized_recommendation


def _serialize_bookings(bookings: List[Booking]) -> List[dict]:
    return list(map(_serialize_booking, bookings))


def _serialize_booking(booking: Booking) -> dict:
    return as_dict(booking, includes=WEBAPP_GET_BOOKING_INCLUDES)


def _get_bookings_by_offer(bookings: List[Booking]) -> list:
    bookings_by_offer = {}

    for booking in bookings:
        offer_id = booking.stock.offerId
        if offer_id in bookings_by_offer:
            bookings_by_offer[offer_id].append(booking)
        else:
            bookings_by_offer[offer_id] = [booking]

    return bookings_by_offer
