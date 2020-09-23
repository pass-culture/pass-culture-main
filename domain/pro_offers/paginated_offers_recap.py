from typing import Dict, List

from domain.identifier.identifier import Identifier



class OfferRecapStock:
    def __init__(self, identifier: int, remaining_quantity: int):
        self.identifier = Identifier(identifier)
        self.remaining_quantity = remaining_quantity


class OfferRecapVenue:
    def __init__(self, identifier: int, is_virtual: bool, managing_offerer_id: int, name: str, public_name: str):
        self.identifier = Identifier(identifier)
        self.is_virtual = is_virtual
        self.managing_offerer_id = Identifier(managing_offerer_id)
        self.name = name
        self.public_name = public_name


class OfferRecap:
    def __init__(self,
                 identifier: int,
                 has_booking_limit_datetimes_passed: bool,
                 is_active: bool,
                 is_editable: bool,
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
                 stocks: List[Dict],
                 ):
        self.identifier = Identifier(identifier)
        self.has_booking_limit_datetimes_passed = has_booking_limit_datetimes_passed
        self.is_active = is_active
        self.is_editable = is_editable
        self.is_event = is_event
        self.is_thing = is_thing
        self.name = name
        self.thumb_url = thumb_url
        self.offer_type = offer_type
        self.venue = OfferRecapVenue(venue_identifier, venue_is_virtual, venue_managing_offerer_id, venue_name, venue_public_name)
        self.stocks = [OfferRecapStock(stock["identifier"], stock["remaining_quantity"]) for stock in stocks]


class PaginatedOffersRecap:
    def __init__(self, offers_recap: List[OfferRecap], current_page: int, total_pages: int, total_offers: int):
        self.offers = offers_recap
        self.current_page = current_page
        self.total_pages = total_pages
        self.total_offers = total_offers
