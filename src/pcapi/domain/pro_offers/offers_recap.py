from datetime import datetime
from typing import Optional


class OfferRecapStock:
    def __init__(
        self,
        id: int,  # pylint: disable=redefined-builtin
        has_booking_limit_datetime_passed: bool,
        remaining_quantity: int,
        beginning_datetime: datetime,
    ):
        self.id = id
        self.has_booking_limit_datetime_passed = has_booking_limit_datetime_passed
        self.remaining_quantity = remaining_quantity
        self.beginning_datetime = beginning_datetime


class OfferRecapVenue:
    def __init__(
        self,
        id: int,  # pylint: disable=redefined-builtin
        is_virtual: bool,
        managing_offerer_id: int,
        name: str,
        public_name: str,
        offerer_name: str,
        venue_departement_code: Optional[str],
    ):
        self.id = id
        self.is_virtual = is_virtual
        self.managing_offerer_id = managing_offerer_id
        self.name = name
        self.offerer_name = offerer_name
        self.public_name = public_name
        self.departement_code = venue_departement_code


class OfferRecap:
    def __init__(
        self,
        id: int,  # pylint: disable=redefined-builtin
        has_booking_limit_datetimes_passed: bool,
        is_active: bool,
        is_editable: bool,
        is_event: bool,
        is_thing: bool,
        product_isbn: Optional[str],
        name: str,
        thumb_url: str,
        subcategory_id: Optional[str],
        venue_id: int,
        venue_is_virtual: bool,
        venue_managing_offerer_id: int,
        venue_name: str,
        venue_offerer_name: str,
        venue_public_name: str,
        venue_departement_code: Optional[str],
        stocks: list[dict],
        status: str,
    ):
        self.id = id
        self.has_booking_limit_datetimes_passed = has_booking_limit_datetimes_passed
        self.is_active = is_active
        self.is_editable = is_editable
        self.is_event = is_event
        self.is_thing = is_thing
        self.product_isbn = product_isbn
        self.name = name
        self.thumb_url = thumb_url
        self.subcategoryId = subcategory_id
        self.venue = OfferRecapVenue(
            venue_id,
            venue_is_virtual,
            venue_managing_offerer_id,
            venue_name,
            venue_public_name,
            venue_offerer_name,
            venue_departement_code,
        )
        self.stocks = [
            OfferRecapStock(
                stock["id"],
                stock["has_booking_limit_datetime_passed"],
                stock["remaining_quantity"],
                stock["beginning_datetime"],
            )
            for stock in stocks
        ]
        self.status = status


class OffersRecap:
    def __init__(self, offers_recap: list[OfferRecap]):
        self.offers = offers_recap
