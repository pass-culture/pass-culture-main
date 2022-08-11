from datetime import datetime
from typing import Iterator
from typing import cast

import pytz
from sqlalchemy import Sequence

from pcapi import settings
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
from pcapi.core.booking_providers.cds.client import CineDigitalServiceAPI
from pcapi.core.booking_providers.models import Movie
from pcapi.core.categories import subcategories
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.providers.models import VenueProvider
from pcapi.core.providers.repository import get_cds_cinema_details
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.models import db
import pcapi.utils.date as utils_date


class CDSStocks(LocalProvider):
    name = "Ciné Office"
    can_create = True

    def __init__(self, venue_provider: VenueProvider):
        super().__init__(venue_provider)
        self.apiUrl = settings.CDS_API_URL
        self.venue = venue_provider.venue
        self.cinema_id = venue_provider.venueIdAtOfferProvider
        cinema_details = get_cds_cinema_details(venue_provider.venueIdAtOfferProvider)  # type: ignore [arg-type]
        self.apiToken = cinema_details.cinemaApiToken
        self.accountId = cinema_details.accountId
        self.isDuo = venue_provider.isDuoOffers if venue_provider.isDuoOffers else False
        self.movies: Iterator[Movie] = iter(self._get_cds_movies())
        self.shows = self._get_cds_shows()
        self.filtered_movie_showtimes = None
        self.last_offer_id: int | None = None

    def __next__(self) -> list[ProvidableInfo]:

        movie_infos = next(self.movies)
        if movie_infos:
            self.movie_information = movie_infos
            self.filtered_movie_showtimes = _find_showtimes_by_movie_id(self.shows, int(self.movie_information.id))  # type: ignore [assignment]
            if not self.filtered_movie_showtimes:
                return []

        providable_information_list = []

        product_providable_info = self.create_providable_info(
            Product, str(self.movie_information.id), datetime.utcnow(), str(self.movie_information.id)
        )
        providable_information_list.append(product_providable_info)

        venue_movie_unique_id = _build_movie_uuid(self.movie_information.id, self.venue)
        offer_providable_info = self.create_providable_info(
            Offer, venue_movie_unique_id, datetime.utcnow(), venue_movie_unique_id
        )
        providable_information_list.append(offer_providable_info)

        for show in self.filtered_movie_showtimes:  # type: ignore [attr-defined]
            id_at_providers = _build_stock_uuid(self.movie_information.id, self.venue, show["show_information"])
            stock_providable_info = self.create_providable_info(
                Stock, id_at_providers, datetime.utcnow(), id_at_providers
            )
            providable_information_list.append(stock_providable_info)

        return providable_information_list

    def fill_object_attributes(self, pc_object: Model) -> None:  # type: ignore [valid-type]
        if isinstance(pc_object, Product):
            self.fill_product_attributes(pc_object)

        if isinstance(pc_object, Offer):
            self.fill_offer_attributes(pc_object)

        if isinstance(pc_object, Stock):
            self.fill_stock_attributes(pc_object)

    def fill_product_attributes(self, cds_product: Product) -> None:
        cds_product.name = self.movie_information.title
        cds_product.subcategoryId = subcategories.SEANCE_CINE.id

        self.update_from_movie_information(cds_product, self.movie_information)

        is_new_product_to_insert = cds_product.id is None

        if is_new_product_to_insert:
            cds_product.id = get_next_product_id_from_database()
        self.last_product_id = cds_product.id

    def fill_offer_attributes(self, cds_offer: Offer) -> None:
        cds_offer.venueId = self.venue.id
        cds_offer.bookingEmail = self.venue.bookingEmail
        cds_offer.withdrawalDetails = self.venue.withdrawalDetails

        self.update_from_movie_information(cds_offer, self.movie_information)

        if self.movie_information.visa:
            cds_offer.extraData = {"visa": self.movie_information.visa}

        cds_offer.name = self.movie_information.title
        cds_offer.subcategoryId = subcategories.SEANCE_CINE.id
        cds_offer.productId = self.last_product_id

        is_new_offer_to_insert = cds_offer.id is None

        if is_new_offer_to_insert:
            cds_offer.id = get_next_offer_id_from_database()
            cds_offer.isDuo = self.isDuo

        self.last_offer_id = cds_offer.id

    def fill_stock_attributes(self, cds_stock: Stock):  # type: ignore [no-untyped-def]
        cds_stock.offerId = cast(int, self.last_offer_id)

        showtime_uuid = _get_showtimes_uuid_by_idAtProvider(cds_stock.idAtProviders)  # type: ignore [arg-type]
        showtime = _find_showtime_by_showtime_uuid(self.filtered_movie_showtimes, showtime_uuid)  # type: ignore [arg-type]
        if showtime:
            show_price = showtime["price"]
            show: ShowCDS = showtime["show_information"]

        local_tz = utils_date.get_department_timezone(self.venue.departementCode)
        datetime_in_utc = utils_date.local_datetime_to_default_timezone(show.showtime, local_tz)
        bookingLimitDatetime = utils_date.get_day_start(datetime_in_utc.date(), pytz.timezone(local_tz))
        cds_stock.beginningDatetime = datetime_in_utc
        is_internet_sale_gauge_active = self._get_cds_internet_sale_gauge()

        is_new_stock_to_insert = cds_stock.id is None
        if is_new_stock_to_insert:
            cds_stock.fieldsUpdated = []

        if "bookingLimitDatetime" not in cds_stock.fieldsUpdated:
            cds_stock.bookingLimitDatetime = bookingLimitDatetime

        if "quantity" not in cds_stock.fieldsUpdated:
            if is_internet_sale_gauge_active:
                cds_stock.quantity = show.internet_remaining_place
            else:
                cds_stock.quantity = show.remaining_place

        if "price" not in cds_stock.fieldsUpdated:
            cds_stock.price = show_price

        if not is_new_stock_to_insert:
            if is_internet_sale_gauge_active:
                cds_stock.quantity = show.internet_remaining_place + cds_stock.dnBookedQuantity
            else:
                cds_stock.quantity = show.remaining_place + cds_stock.dnBookedQuantity

    def update_from_movie_information(self, obj: Offer | Product, movie_information: Movie) -> None:
        if movie_information.description:
            obj.description = movie_information.description
        if self.movie_information.duration:
            obj.durationMinutes = movie_information.duration
        if not obj.extraData:
            obj.extraData = {}
        obj.extraData = {"visa": self.movie_information.visa}

    def get_object_thumb(self) -> bytes:
        if self.movie_information.posterpath:
            image_url = self.movie_information.posterpath
            return self._get_cds_movie_poster(image_url)
        return bytes()

    def get_object_thumb_index(self) -> int:
        return 1

    def get_keep_poster_ratio(self) -> bool:
        return True

    def _get_cds_internet_sale_gauge(self) -> bool:
        if not self.apiUrl:
            raise Exception("CDS API URL not configured in this env")
        client_cds = CineDigitalServiceAPI(
            cinema_id=self.venue_provider.venueIdAtOfferProvider,
            account_id=self.accountId,  # type: ignore [arg-type]
            api_url=self.apiUrl,
            cinema_api_token=self.apiToken,
        )
        return client_cds.get_internet_sale_gauge_active()

    def _get_cds_movies(self) -> list[Movie]:
        if not self.apiUrl:
            raise Exception("CDS API URL not configured in this env")
        client_cds = CineDigitalServiceAPI(
            cinema_id=self.venue_provider.venueIdAtOfferProvider,
            account_id=self.accountId,  # type: ignore [arg-type]
            api_url=self.apiUrl,
            cinema_api_token=self.apiToken,
        )
        return client_cds.get_venue_movies()

    def _get_cds_movie_poster(self, image_url: str) -> bytes:
        if not self.apiUrl:
            raise Exception("CDS API URL not configured in this env")
        client_cds = CineDigitalServiceAPI(
            cinema_id=self.venue_provider.venueIdAtOfferProvider,
            account_id=self.accountId,  # type: ignore [arg-type]
            api_url=self.apiUrl,
            cinema_api_token=self.apiToken,
        )
        return client_cds.get_movie_poster(image_url)

    def _get_cds_shows(self) -> list[dict]:
        if not self.apiUrl:
            raise Exception("CDS API URL not configured in this env")
        client_cds = CineDigitalServiceAPI(
            cinema_id=self.venue_provider.venueIdAtOfferProvider,
            account_id=self.accountId,  # type: ignore [arg-type]
            api_url=self.apiUrl,
            cinema_api_token=self.apiToken,
        )

        shows = client_cds.get_shows()

        shows_with_pass_culture_tariff = []
        for show in shows:
            min_price_voucher = client_cds.get_voucher_type_for_show(show)
            if min_price_voucher is not None:
                shows_with_pass_culture_tariff.append(
                    {"show_information": show, "price": min_price_voucher.tariff.price}
                )

        return shows_with_pass_culture_tariff


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


def _find_showtime_by_showtime_uuid(showtimes: list[dict], showtime_uuid: str) -> dict | None:
    for showtime in showtimes:
        if _build_showtime_uuid(showtime["show_information"]) == showtime_uuid:
            return showtime
    return None


def _get_showtimes_uuid_by_idAtProvider(id_at_provider: str):  # type: ignore [no-untyped-def]
    return id_at_provider.split("#")[1]


def _build_movie_uuid(movie_information_id: str, venue: Venue) -> str:
    return f"{movie_information_id}%{venue.siret}"


def _build_showtime_uuid(showtime_details: ShowCDS) -> str:
    return f"{showtime_details.id}/{showtime_details.showtime}"


def _build_stock_uuid(movie_information_id: str, venue: Venue, showtime_details: ShowCDS) -> str:
    return f"{_build_movie_uuid(movie_information_id, venue)}#{_build_showtime_uuid(showtime_details)}"
