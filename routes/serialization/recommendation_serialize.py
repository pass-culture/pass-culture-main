import time
from typing import List, Dict

from models import Recommendation, BookingSQLEntity
from repository import booking_queries
from routes.serialization import as_dict
from utils.human_ids import dehumanize
from utils.includes import RECOMMENDATION_INCLUDES


def serialize_recommendations(recommendations: List[Recommendation], user_id: int) -> List[Dict]:
    serialized_recommendations = [serialize_recommendation(recommendation, user_id, query_booking=False)
                                  for recommendation in recommendations]
    bookings = booking_queries.find_user_bookings_for_recommendation(user_id)
    bookings_by_offer = _get_bookings_by_offer(bookings)
    for serialized_recommendation in serialized_recommendations:
        offer_id = dehumanize(serialized_recommendation["offerId"])
        if offer_id in bookings_by_offer:
            bookings_for_recommendation = bookings_by_offer[offer_id]
        else:
            bookings_for_recommendation = []
        serialized_recommendation['bookings'] = _serialize_bookings(bookings_for_recommendation)

    return serialized_recommendations


def serialize_recommendation(recommendation: Recommendation, user_id: int, query_booking: bool = True) -> Dict:
    serialized_recommendation = as_dict(recommendation, includes=RECOMMENDATION_INCLUDES)
    if query_booking and recommendation.offer:
        bookings = booking_queries.find_from_recommendation(recommendation, user_id)
        serialized_recommendation['bookings'] = _serialize_bookings(bookings)

    add_offer_and_stock_information(serialized_recommendation)

    return serialized_recommendation


def add_offer_and_stock_information(serialized_recommendation: Dict) -> None:
    serialized_recommendation['offer']['isBookable'] = True
    for index, stock in enumerate(serialized_recommendation['offer']['stocks']):
        serialized_recommendation['offer']['stocks'][index]['isBookable'] = True
        serialized_recommendation['offer']['stocks'][index]['remainingQuantity'] = 'unlimited'


def _serialize_bookings(bookings: List[BookingSQLEntity]) -> List[Dict]:
    return list(map(as_dict, bookings))


def _get_bookings_by_offer(bookings: List[BookingSQLEntity]) -> Dict:
    bookings_by_offer = {}

    for booking in bookings:
        offer_id = booking.stock.offerId
        if offer_id in bookings_by_offer:
            bookings_by_offer[offer_id].append(booking)
        else:
            bookings_by_offer[offer_id] = [booking]

    return bookings_by_offer
