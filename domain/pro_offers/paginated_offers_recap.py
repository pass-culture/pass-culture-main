from typing import List


class Stock:
    def __init__(self, identifier: int, is_event_expired: bool, remaining_quantity: int, offer_id: int):
        self.identifier = identifier
        self.is_event_expired = is_event_expired
        self.remaining_quantity = remaining_quantity
        self.offer_id = offer_id


class Venue:
    def __init__(self, identifier: int, is_virtual: bool, name: str, public_name: str):
        self.identifier = identifier
        self.is_virtual = is_virtual
        self.name = name
        self.public_name = public_name


class OfferRecap:
    def __init__(self,
                 identifier: int,
                 availability_message: str,
                 has_booking_limit_datetimes_passed: bool,
                 is_active: bool,
                 is_editable: bool,
                 is_fully_booked: bool,
                 is_event: bool,
                 is_thing: bool,
                 name: str,
                 stocks: List[Stock],
                 thumb_url: str,
                 offer_type: str,
                 venue: Venue
                 ):
        self.identifier = identifier
        self.availability_message = availability_message
        self.has_booking_limit_datetimes_passed = has_booking_limit_datetimes_passed
        self.is_active = is_active
        self.is_editable = is_editable
        self.is_fully_booked = is_fully_booked
        self.is_event = is_event
        self.is_thing = is_thing
        self.name = name
        self.stocks = stocks
        self.thumb_url = thumb_url
        self.offer_type = offer_type
        self.venue = venue


class PaginatedOffersRecap:
    def __init__(self, offers_recap: List[OfferRecap], total: int):
        self.offers = offers_recap
        self.total = total
