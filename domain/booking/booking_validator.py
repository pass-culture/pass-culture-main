from domain.booking.booking_exceptions import OfferIsAlreadyBooked, QuantityIsInvalid
from models import Offer
from repository import booking_queries


def check_offer_already_booked(offer: Offer, user_id: int):
    is_offer_already_booked_by_user = booking_queries.is_offer_already_booked_by_user(user_id, offer)
    if is_offer_already_booked_by_user:
        offer_is_already_booked = OfferIsAlreadyBooked()
        raise offer_is_already_booked


def check_quantity_is_valid(quantity: int, offer_is_duo: bool) -> None:
    if offer_is_duo and quantity not in (1, 2):
        quantity_is_invalid = QuantityIsInvalid("Vous devez réserver une place ou deux dans le cas d'une offre DUO.")
        raise quantity_is_invalid

    if not offer_is_duo and quantity != 1:
        quantity_is_invalid = QuantityIsInvalid("Vous ne pouvez réserver qu'une place pour cette offre.")
        raise quantity_is_invalid
