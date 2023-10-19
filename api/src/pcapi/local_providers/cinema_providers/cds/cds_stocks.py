from datetime import datetime
import decimal
from typing import Iterator

from pcapi import settings
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
from pcapi.core.external_bookings.models import Movie
from pcapi.core.offerers.models import Venue
import pcapi.core.offers.models as offers_models
from pcapi.core.offers.repository import get_next_product_id_from_database
from pcapi.core.providers.models import VenueProvider
from pcapi.core.providers.repository import get_cds_cinema_details
from pcapi.local_providers.cinema_providers.constants import ShowtimeFeatures
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
import pcapi.utils.date as utils_date


ACCEPTED_MEDIA_OPTIONS_TICKET_LABEL = {
    "VF": ShowtimeFeatures.VF.value,
    "VO": ShowtimeFeatures.VO.value,
    "3D": ShowtimeFeatures.THREE_D.value,
}


class CDSStocks(LocalProvider):
    name = "Ciné Office"
    can_create = True

    def __init__(self, venue_provider: VenueProvider):
        super().__init__(venue_provider)
        self.apiUrl = settings.CDS_API_URL
        if not self.apiUrl:
            raise ValueError("CDS API URL not configured in this env")
        self.venue = venue_provider.venue
        self.cinema_id = venue_provider.venueIdAtOfferProvider
        cinema_details = get_cds_cinema_details(venue_provider.venueIdAtOfferProvider)
        self.apiToken = cinema_details.cinemaApiToken
        self.accountId = cinema_details.accountId
        self.isDuo = venue_provider.isDuoOffers if venue_provider.isDuoOffers else False
        self.client_cds = CineDigitalServiceAPI(
            cinema_id=self.venue_provider.venueIdAtOfferProvider,
            account_id=self.accountId,
            api_url=self.apiUrl,
            cinema_api_token=self.apiToken,
        )
        self.movies: Iterator[Movie] = iter(self.client_cds.get_venue_movies())
        self.media_options = self.client_cds.get_media_options()
        self.shows = self._get_cds_shows()
        self.filtered_movie_showtimes = None
        self.price_category_labels: list[
            offers_models.PriceCategoryLabel
        ] = offers_models.PriceCategoryLabel.query.filter(offers_models.PriceCategoryLabel.venue == self.venue).all()
        self.price_category_lists_by_offer: dict[offers_models.Offer, list[offers_models.PriceCategory]] = {}

    def __next__(self) -> list[ProvidableInfo]:
        movie_infos = next(self.movies)
        if movie_infos:
            self.movie_information = movie_infos
            self.filtered_movie_showtimes = _find_showtimes_by_movie_id(self.shows, int(self.movie_information.id))  # type: ignore [assignment]
            if not self.filtered_movie_showtimes:
                return []

        providable_information_list = []

        # The Product ID must be unique
        provider_movie_unique_id = _build_movie_uuid(self.movie_information.id, self.venue)
        product_providable_info = self.create_providable_info(
            pc_object=offers_models.Product,
            id_at_providers=provider_movie_unique_id,
            date_modified_at_provider=datetime.utcnow(),
            new_id_at_provider=provider_movie_unique_id,
        )
        providable_information_list.append(product_providable_info)

        venue_movie_unique_id = _build_movie_uuid(self.movie_information.id, self.venue)
        offer_providable_info = self.create_providable_info(
            offers_models.Offer, venue_movie_unique_id, datetime.utcnow(), venue_movie_unique_id
        )
        providable_information_list.append(offer_providable_info)

        for show in self.filtered_movie_showtimes:  # type: ignore [attr-defined]
            stock_showtime_unique_id = _build_stock_uuid(
                self.movie_information.id, self.venue, show["show_information"]
            )
            stock_providable_info = self.create_providable_info(
                offers_models.Stock, stock_showtime_unique_id, datetime.utcnow(), stock_showtime_unique_id
            )
            providable_information_list.append(stock_providable_info)

        return providable_information_list

    def fill_object_attributes(self, pc_object: Model) -> None:
        if isinstance(pc_object, offers_models.Product):
            self.fill_product_attributes(pc_object)

        if isinstance(pc_object, offers_models.Offer):
            self.fill_offer_attributes(pc_object)

        if isinstance(pc_object, offers_models.Stock):
            self.fill_stock_attributes(pc_object)

    def fill_product_attributes(self, cds_product: offers_models.Product) -> None:
        cds_product.name = self.movie_information.title
        cds_product.subcategoryId = subcategories.SEANCE_CINE.id

        self.update_from_movie_information(cds_product, self.movie_information)

        is_new_product_to_insert = cds_product.id is None
        if is_new_product_to_insert:
            cds_product.id = get_next_product_id_from_database()

        self.last_product = cds_product

    def fill_offer_attributes(self, cds_offer: offers_models.Offer) -> None:
        cds_offer.venueId = self.venue.id
        cds_offer.bookingEmail = self.venue.bookingEmail
        cds_offer.withdrawalDetails = self.venue.withdrawalDetails

        self.update_from_movie_information(cds_offer, self.movie_information)

        if self.movie_information.visa:
            cds_offer.extraData = {"visa": self.movie_information.visa}

        cds_offer.name = self.movie_information.title
        cds_offer.subcategoryId = subcategories.SEANCE_CINE.id
        cds_offer.product = self.last_product

        is_new_offer_to_insert = cds_offer.id is None
        if is_new_offer_to_insert:
            cds_offer.isDuo = self.isDuo

        self.last_offer = cds_offer

    def fill_stock_attributes(self, cds_stock: offers_models.Stock):  # type: ignore [no-untyped-def]
        cds_stock.offer = self.last_offer

        showtime_uuid = _get_showtimes_uuid_by_idAtProvider(cds_stock.idAtProviders)  # type: ignore [arg-type]
        showtime = _find_showtime_by_showtime_uuid(self.filtered_movie_showtimes, showtime_uuid)  # type: ignore [arg-type]
        if showtime:
            price_label = showtime["price_label"]
            show_price = decimal.Decimal(str(showtime["price"]))
            show: ShowCDS = showtime["show_information"]

        local_tz = utils_date.get_department_timezone(self.venue.departementCode)
        datetime_in_utc = utils_date.local_datetime_to_default_timezone(show.showtime, local_tz)
        cds_stock.beginningDatetime = datetime_in_utc
        cds_stock.bookingLimitDatetime = datetime_in_utc
        is_internet_sale_gauge_active = self.client_cds.get_internet_sale_gauge_active()

        is_new_stock_to_insert = cds_stock.id is None
        if is_new_stock_to_insert:
            cds_stock.fieldsUpdated = []

        if "quantity" not in cds_stock.fieldsUpdated:
            booked_quantity = 0 if is_new_stock_to_insert else cds_stock.dnBookedQuantity
            if is_internet_sale_gauge_active:
                quantity = show.internet_remaining_place + booked_quantity
            else:
                quantity = show.remaining_place + booked_quantity
            cds_stock.quantity = quantity

        features = [
            self.media_options.get(option.media_options_id.id)
            for option in show.shows_mediaoptions_collection
            if self.media_options.get(option.media_options_id.id) in ACCEPTED_MEDIA_OPTIONS_TICKET_LABEL
        ]

        # sort features list to have always same order for all providers VO/VF then 3D
        cds_stock.features = sorted(
            [ACCEPTED_MEDIA_OPTIONS_TICKET_LABEL.get(feature) for feature in features if feature], reverse=True
        )

        if "price" not in cds_stock.fieldsUpdated:
            cds_stock.price = show_price
            price_category = self.get_or_create_price_category(show_price, price_label)
            cds_stock.priceCategory = price_category

    def get_or_create_price_category(self, price: decimal.Decimal, price_label: str) -> offers_models.PriceCategory:
        if self.last_offer not in self.price_category_lists_by_offer:
            self.price_category_lists_by_offer[self.last_offer] = (
                offers_models.PriceCategory.query.filter(offers_models.PriceCategory.offer == self.last_offer).all()
                if self.last_offer.id
                else []
            )
        price_categories = self.price_category_lists_by_offer[self.last_offer]

        price_category = next(
            (category for category in price_categories if category.price == price and category.label == price_label),
            None,
        )
        if not price_category:
            price_category_label = self.get_or_create_price_category_label(price_label)
            price_category = offers_models.PriceCategory(
                price=price, priceCategoryLabel=price_category_label, offer=self.last_offer
            )
            price_categories.append(price_category)

        return price_category

    def get_or_create_price_category_label(self, price_label: str) -> offers_models.PriceCategoryLabel:
        price_category_label = next((label for label in self.price_category_labels if label.label == price_label), None)
        if not price_category_label:
            price_category_label = offers_models.PriceCategoryLabel(label=price_label, venue=self.venue)
            self.price_category_labels.append(price_category_label)

        return price_category_label

    def update_from_movie_information(
        self, obj: offers_models.Offer | offers_models.Product, movie_information: Movie
    ) -> None:
        if movie_information.description:
            obj.description = movie_information.description
        if self.movie_information.duration:
            obj.durationMinutes = movie_information.duration
        obj.extraData = {"visa": self.movie_information.visa}

    def get_object_thumb(self) -> bytes:
        if self.movie_information.posterpath:
            image_url = self.movie_information.posterpath
            return self.client_cds.get_movie_poster(image_url)
        return bytes()

    def shall_synchronize_thumbs(self) -> bool:
        return True

    def get_keep_poster_ratio(self) -> bool:
        return True

    def _get_cds_shows(self) -> list[dict]:
        shows = self.client_cds.get_shows()

        shows_with_pass_culture_tariff = []
        for show in shows:
            min_price_voucher = self.client_cds.get_voucher_type_for_show(show)
            if min_price_voucher and min_price_voucher.tariff:
                shows_with_pass_culture_tariff.append(
                    {
                        "show_information": show,
                        "price": min_price_voucher.tariff.price,
                        "price_label": min_price_voucher.tariff.label,
                    }
                )

        return shows_with_pass_culture_tariff


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
    """This must be unique, among all Providers and Venues"""
    return f"{movie_information_id}%{venue.siret}%CDS"


def _build_showtime_uuid(showtime_details: ShowCDS) -> str:
    return f"{showtime_details.id}/{showtime_details.showtime}"


def _build_stock_uuid(movie_information_id: str, venue: Venue, showtime_details: ShowCDS) -> str:
    return f"{_build_movie_uuid(movie_information_id, venue)}#{_build_showtime_uuid(showtime_details)}"
