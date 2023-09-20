from datetime import datetime


class OfferRecapStock:
    def __init__(
        self,
        id: int,  # pylint: disable=redefined-builtin
        has_booking_limit_datetime_passed: bool,
        remaining_quantity: int,
        beginning_datetime: datetime,
        dnBookedQuantity: int,
    ):
        self.id = id
        self.has_booking_limit_datetime_passed = has_booking_limit_datetime_passed
        self.remaining_quantity = remaining_quantity
        self.beginning_datetime = beginning_datetime
        self.dnBookedQuantity = dnBookedQuantity


class OfferRecapVenue:
    def __init__(
        self,
        id: int,  # pylint: disable=redefined-builtin
        is_virtual: bool,
        managing_offerer_id: int,
        name: str,
        public_name: str | None,
        offerer_name: str,
        venue_departement_code: str | None,
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
        product_ean: str | None,
        name: str,
        thumb_url: str | None,
        subcategory_id: str | None,
        venue_id: int,
        venue_is_virtual: bool,
        venue_managing_offerer_id: int,
        venue_name: str,
        venue_offerer_name: str,
        venue_public_name: str | None,
        venue_departement_code: str | None,
        stocks: list[dict],
        status: str,
        is_showcase: bool,
    ):
        self.id = id
        self.has_booking_limit_datetimes_passed = has_booking_limit_datetimes_passed
        self.is_active = is_active
        self.is_editable = is_editable
        self.is_event = is_event
        self.is_thing = is_thing
        self.product_ean = product_ean
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
                stock["dnBookedQuantity"],
            )
            for stock in stocks
        ]
        self.status = status
        self.is_showcase = is_showcase


class OffersRecap:
    def __init__(self, offers_recap: list[OfferRecap]):
        self.offers = offers_recap
