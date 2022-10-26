from datetime import datetime
from typing import Iterator
from typing import cast

import pytz
from sqlalchemy.sql.schema import Sequence

from pcapi.connectors.serialization import boost_serializers
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.boost.client import BoostClientAPI
from pcapi.core.external_bookings.models import Movie
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.providers.models import VenueProvider
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.models import db
import pcapi.utils.date as utils_date


BOOST_PASS_CULTURE_PRICING_CODE = "PCU"


def get_pcu_pricing_if_exists(
    showtime_pricing_list: list[boost_serializers.ShowtimePricing],
) -> boost_serializers.ShowtimePricing | None:
    return next(
        (pricing for pricing in showtime_pricing_list if pricing.pricingCode == BOOST_PASS_CULTURE_PRICING_CODE), None
    )


class BoostStocks(LocalProvider):
    name = "Boost"
    can_create = True

    def __init__(self, venue_provider: VenueProvider):
        super().__init__(venue_provider)
        self.venue = venue_provider.venue
        self.cinema_id = venue_provider.venueIdAtOfferProvider
        self.isDuo = venue_provider.isDuoOffers if venue_provider.isDuoOffers else False
        self.showtimes: Iterator[boost_serializers.ShowTime3] = iter(self._get_showtimes())
        self.last_offer_id: int | None = None

    def __next__(self) -> list[ProvidableInfo]:
        showtime = next(self.showtimes)
        if showtime:
            self.showtime_details = self._get_showtime_details(showtime.id)
            self.pcu_pricing = get_pcu_pricing_if_exists(self.showtime_details.showtimePricing)
            if not self.pcu_pricing:
                return []

        providable_information_list = []

        product_providable_info = self.create_providable_info(
            Product, str(self.showtime_details.film.id), datetime.utcnow(), str(self.showtime_details.film.id)
        )
        providable_information_list.append(product_providable_info)

        venue_movie_unique_id = _build_movie_uuid(self.showtime_details.film.id, self.venue)
        offer_providable_info = self.create_providable_info(
            Offer, venue_movie_unique_id, datetime.utcnow(), venue_movie_unique_id
        )
        providable_information_list.append(offer_providable_info)

        showtime_id = _build_stock_uuid(self.showtime_details.film.id, self.venue, self.showtime_details.id)
        stock_providable_info = self.create_providable_info(Stock, showtime_id, datetime.utcnow(), showtime_id)
        providable_information_list.append(stock_providable_info)

        return providable_information_list

    def fill_object_attributes(self, pc_object: Model) -> None:
        if isinstance(pc_object, Product):
            self.fill_product_attributes(pc_object)

        if isinstance(pc_object, Offer):
            self.fill_offer_attributes(pc_object)

        if isinstance(pc_object, Stock):
            self.fill_stock_attributes(pc_object)

    def fill_product_attributes(self, product: Product) -> None:
        product.name = self.showtime_details.film.titleCnc
        product.subcategoryId = subcategories.SEANCE_CINE.id

        self.update_from_movie_information(product, self.showtime_details.film.to_generic_movie())

        is_new_product_to_insert = product.id is None

        if is_new_product_to_insert:
            product.id = get_next_product_id_from_database()
        self.last_product_id = product.id

    def fill_offer_attributes(self, offer: Offer) -> None:
        offer.venueId = self.venue.id
        offer.bookingEmail = self.venue.bookingEmail
        offer.withdrawalDetails = self.venue.withdrawalDetails

        self.update_from_movie_information(offer, self.showtime_details.film.to_generic_movie())

        if self.showtime_details.film.numVisa:
            offer.extraData = {"visa": self.showtime_details.film.numVisa}

        offer.name = self.showtime_details.film.titleCnc
        offer.subcategoryId = subcategories.SEANCE_CINE.id
        offer.productId = self.last_product_id

        is_new_offer_to_insert = offer.id is None

        if is_new_offer_to_insert:
            offer.id = get_next_offer_id_from_database()
            offer.isDuo = self.isDuo

        self.last_offer_id = offer.id

    def fill_stock_attributes(self, stock: Stock) -> None:
        stock.offerId = cast(int, self.last_offer_id)

        local_tz = utils_date.get_department_timezone(self.venue.departementCode)
        datetime_in_utc = utils_date.local_datetime_to_default_timezone(self.showtime_details.showDate, local_tz)
        booking_limit_datetime = utils_date.get_day_start(datetime_in_utc.date(), pytz.timezone(local_tz))
        stock.beginningDatetime = datetime_in_utc

        is_new_stock_to_insert = stock.id is None
        if is_new_stock_to_insert:
            stock.fieldsUpdated = []

        if "bookingLimitDatetime" not in stock.fieldsUpdated:
            stock.bookingLimitDatetime = booking_limit_datetime

        if "quantity" not in stock.fieldsUpdated:
            stock.quantity = self.showtime_details.numberRemainingSeatsForOnlineSale

        if "price" not in stock.fieldsUpdated:
            assert self.pcu_pricing  # helps mypy
            stock.price = self.pcu_pricing.amountTaxesIncluded

        if not is_new_stock_to_insert:
            stock.quantity = self.showtime_details.numberRemainingSeatsForOnlineSale + stock.dnBookedQuantity

    def update_from_movie_information(self, obj: Offer | Product, movie_information: Movie) -> None:
        if movie_information.description:
            obj.description = movie_information.description
        if movie_information.duration:
            obj.durationMinutes = movie_information.duration

        if not obj.extraData:
            obj.extraData = {}
        obj.extraData = {"visa": movie_information.visa}

    def get_object_thumb(self) -> bytes:
        return bytes()

    def get_object_thumb_index(self) -> int:
        return 1

    def get_keep_poster_ratio(self) -> bool:
        return True

    def _get_showtimes(self) -> list[boost_serializers.ShowTime3]:
        client_boost = BoostClientAPI(self.cinema_id)
        return client_boost.get_showtimes()

    def _get_showtime_details(self, showtime_id: int) -> boost_serializers.ShowTime:
        client_boost = BoostClientAPI(self.cinema_id)
        return client_boost.get_showtime(showtime_id)


def get_next_product_id_from_database() -> int:
    sequence: Sequence = Sequence("product_id_seq")
    return db.session.execute(sequence)


def get_next_offer_id_from_database() -> int:
    sequence: Sequence = Sequence("offer_id_seq")
    return db.session.execute(sequence)


def _find_showtimes_by_movie_id(showtimes_information: list[dict], movie_id: int) -> list[dict]:
    return list(
        filter(
            lambda showtime: showtime["show_information"].media.id == movie_id,
            showtimes_information,
        )
    )


def _get_showtimes_uuid_by_idAtProvider(id_at_provider: str) -> str:
    return id_at_provider.split("#")[1]


def _build_movie_uuid(movie_information_id: int, venue: Venue) -> str:
    return f"{movie_information_id}%{venue.id}"


def _build_stock_uuid(film_id: int, venue: Venue, showtime_id: int) -> str:
    return f"{_build_movie_uuid(film_id, venue)}#{showtime_id}"
