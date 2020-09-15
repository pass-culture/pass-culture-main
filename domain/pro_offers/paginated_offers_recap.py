from typing import List, Dict


class OfferRecapStock:
    def __init__(self, identifier: int, is_event_expired: bool, remaining_quantity: int):
        self.identifier = identifier
        self.is_event_expired = is_event_expired
        self.remaining_quantity = remaining_quantity


class OfferRecapVenue:
    def __init__(self, identifier: int, is_virtual: bool, managing_offerer_id: int, name: str, public_name: str):
        self.identifier = identifier
        self.is_virtual = is_virtual
        self.managing_offerer_id = managing_offerer_id
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
                 thumb_url: str,
                 offer_type: str,
                 venue_identifier: int,
                 venue_is_virtual: bool,
                 venue_managing_offerer_id: int,
                 venue_name: str,
                 venue_public_name: str,
                 stocks: [Dict],
                 ):
        [print(stock) for stock in stocks]
        self.identifier = identifier
        self.availability_message = availability_message
        self.has_booking_limit_datetimes_passed = has_booking_limit_datetimes_passed
        self.is_active = is_active
        self.is_editable = is_editable
        self.is_fully_booked = is_fully_booked
        self.is_event = is_event
        self.is_thing = is_thing
        self.name = name
        self.thumb_url = thumb_url
        self.offer_type = offer_type
        self.venue = OfferRecapVenue(venue_identifier, venue_is_virtual, venue_managing_offerer_id, venue_name, venue_public_name)
        self.stocks = [OfferRecapStock(stock["identifier"], stock["is_event_expired"], stock["remaining_quantity"]) for stock in stocks]


class PaginatedOffersRecap:
    def __init__(self, offers_recap: List[OfferRecap], total: int):
        self.offers = offers_recap
        self.total = total
