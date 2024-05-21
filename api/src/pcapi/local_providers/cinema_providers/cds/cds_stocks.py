from datetime import datetime
import decimal
import logging
from typing import Iterator

import sqlalchemy as sqla

from pcapi import settings
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
from pcapi.core.external_bookings.models import Movie
from pcapi.core.offerers.models import Venue
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.offers.repository as offers_repository
from pcapi.core.providers.models import VenueProvider
from pcapi.core.providers.repository import get_cds_cinema_details
from pcapi.local_providers.cinema_providers.constants import ShowtimeFeatures
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.models.feature import FeatureToggle
from pcapi.repository.providable_queries import get_last_update_for_provider
import pcapi.utils.date as utils_date


ACCEPTED_MEDIA_OPTIONS_TICKET_LABEL = {
    "VF": ShowtimeFeatures.VF.value,
    "VO": ShowtimeFeatures.VO.value,
    "3D": ShowtimeFeatures.THREE_D.value,
}

logger = logging.getLogger(__name__)


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
            cinema_id=venue_provider.venueIdAtOfferProvider,
            account_id=self.accountId,
            api_url=self.apiUrl,
            cinema_api_token=self.apiToken,
        )
        self.movies: Iterator[Movie] = iter(self.client_cds.get_venue_movies())
        self.media_options = self.client_cds.get_media_options()
        self.shows = self._get_cds_shows()
        self.filtered_movie_showtimes = None
        self.price_category_labels: list[offers_models.PriceCategoryLabel] = (
            offers_models.PriceCategoryLabel.query.filter(offers_models.PriceCategoryLabel.venue == self.venue).all()
        )
        self.price_category_lists_by_offer: dict[offers_models.Offer, list[offers_models.PriceCategory]] = {}

    def __next__(self) -> list[ProvidableInfo]:
        movie_infos = next(self.movies)
        if movie_infos:
            self.movie_information = movie_infos
            self.filtered_movie_showtimes = _find_showtimes_by_movie_id(self.shows, int(self.movie_information.id))  # type: ignore[assignment]
            if not self.filtered_movie_showtimes:
                return []

        self.product = self.get_movie_product(self.movie_information)
        if not self.product:
            logger.info(
                "Product not found for allocine Id %s",
                self.movie_information.allocineid,
                extra={"allocineId": self.movie_information.allocineid, "venueId": self.venue.id},
                technical_message_id="allocineId.not_found",
            )
            if FeatureToggle.WIP_SYNCHRONIZE_CINEMA_STOCKS_WITH_ALLOCINE_PRODUCTS.is_active():
                return []

        providable_information_list = []

        venue_movie_unique_id = _build_movie_uuid(self.movie_information.id, self.venue)
        offer_providable_info = self.create_providable_info(
            offers_models.Offer, venue_movie_unique_id, datetime.utcnow(), venue_movie_unique_id
        )
        providable_information_list.append(offer_providable_info)

        for show in self.filtered_movie_showtimes:  # type: ignore[attr-defined]
            stock_showtime_unique_id = _build_stock_uuid(
                self.movie_information.id, self.venue, show["show_information"]
            )
            stock_providable_info = self.create_providable_info(
                offers_models.Stock, stock_showtime_unique_id, datetime.utcnow(), stock_showtime_unique_id
            )
            providable_information_list.append(stock_providable_info)

        return providable_information_list

    def get_existing_object(
        self,
        model_type: type[offers_models.Product | offers_models.Offer | offers_models.Stock],
        id_at_providers: str,
    ) -> offers_models.Product | offers_models.Offer | offers_models.Stock | None:
        # exception to the ProvidableMixin because Offer no longer extends this class
        # idAtProviders has been replaced by idAtProvider property
        if model_type == offers_models.Offer:
            query = model_type.query.filter_by(idAtProvider=id_at_providers)
        elif model_type == offers_models.Stock:
            # Try to match both old and new idAtProviders
            # We can't know if we have an existing Stock with an old or a new idAtProviders construct
            # And we also want to try to clean old idAtProviders.
            # So if a provider change the showtime in future, it won't create duplicates anymore

            # TODO (dramelet, 2024-02-09): We can remove this in a few months when we won't
            # have any remaining up-to-date stocks using old construct `idAtProviders`
            old_id_at_providers, new_id_at_providers = _get_old_and_new_id_at_providers(id_at_providers)
            query = model_type.query.filter(
                sqla.or_(
                    offers_models.Stock.idAtProviders
                    == old_id_at_providers,  # i.e. "51%123%CDS#2/2022-07-01 12:00:00+02:00"
                    offers_models.Stock.idAtProviders == new_id_at_providers,  # i.e. "51%123%CDS#2"
                )
            ).with_for_update()
        else:
            query = model_type.query.filter_by(idAtProviders=id_at_providers)

        return query.one_or_none()

    def fill_object_attributes(self, pc_object: Model) -> None:
        if isinstance(pc_object, offers_models.Offer):
            self.fill_offer_attributes(pc_object)

        if isinstance(pc_object, offers_models.Stock):
            self.fill_stock_attributes(pc_object)

    def update_from_movie_information(self, offer: offers_models.Offer) -> None:
        offer.extraData = offer.extraData or offers_models.OfferExtraData()
        if self.product:
            offer.name = self.product.name
            offer.description = self.product.description
            offer.durationMinutes = self.product.durationMinutes
            if self.product.extraData:
                offer.extraData.update(self.product.extraData)
        else:
            offer.name = self.movie_information.title
            if self.movie_information.description:
                offer.description = self.movie_information.description
            if self.movie_information.duration:
                offer.durationMinutes = self.movie_information.duration

        if self.movie_information.allocineid:
            offer.extraData["allocineId"] = offer.extraData.get("allocineId") or int(self.movie_information.allocineid)

        offer.extraData["visa"] = offer.extraData.get("visa") or self.movie_information.visa

    def fill_offer_attributes(self, offer: offers_models.Offer) -> None:
        offer.venueId = self.venue.id
        offer.offererAddress = self.venue.offererAddress
        offer.bookingEmail = self.venue.bookingEmail
        offer.withdrawalDetails = self.venue.withdrawalDetails
        offer.product = self.product
        offer.subcategoryId = subcategories.SEANCE_CINE.id

        self.update_from_movie_information(offer)

        is_new_offer_to_insert = offer.id is None
        if is_new_offer_to_insert:
            offer.isDuo = self.isDuo
            offer.id = offers_repository.get_next_offer_id_from_database()
        last_update_for_current_provider = get_last_update_for_provider(self.provider.id, offer)

        if not last_update_for_current_provider or last_update_for_current_provider.date() != datetime.today().date():
            if self.movie_information.posterpath:
                image_url = self.movie_information.posterpath
                image = self.client_cds.get_movie_poster(image_url)
                if image:
                    offers_api.create_mediation(
                        user=None,
                        offer=offer,
                        credit=None,
                        image_as_bytes=image,
                        keep_ratio=True,
                        check_image_validity=False,
                    )
                    self.createdThumbs += 1

        self.last_offer = offer

    def fill_stock_attributes(self, cds_stock: offers_models.Stock) -> None:
        # `idAtProviders` can't be None at this point
        assert cds_stock.idAtProviders
        cds_stock.offer = self.last_offer

        showtime_uuid = _get_showtimes_uuid_by_idAtProvider(cds_stock.idAtProviders)

        # TODO (dramelet, 2024-02-09): We can remove this in a few months when we won't
        # have any remaining up-to-date stocks using old construct `idAtProviders`
        cds_stock.idAtProviders = _clean_cds_id_at_providers(cds_stock.idAtProviders)

        showtime = _find_showtime_by_showtime_uuid(self.filtered_movie_showtimes, showtime_uuid)  # type: ignore[arg-type]
        if not showtime:
            raise ValueError(
                "Could not find showtime for show %s, allocine id %s, venue id %s"
                % (showtime_uuid, self.movie_information.allocineid, self.venue.id)
            )

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
            show_price = decimal.Decimal(str(showtime["price"]))
            cds_stock.price = show_price
            price_category = self.get_or_create_price_category(show_price, showtime["price_label"])
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

    def get_movie_product(self, film: Movie) -> offers_models.Product | None:
        product = None
        if film.allocineid:
            product = offers_repository.get_movie_product_by_allocine_id(str(film.allocineid))

        if not product and film.visa:
            product = offers_repository.get_movie_product_by_visa(str(film.visa))

        return product


def _find_showtimes_by_movie_id(showtimes_information: list[dict], movie_id: int) -> list[dict]:
    return list(
        filter(
            lambda showtime: showtime["show_information"].media.id == movie_id,
            showtimes_information,
        )
    )


def _find_showtime_by_showtime_uuid(showtimes: list[dict], showtime_uuid: str) -> dict | None:
    for showtime in showtimes:
        if showtime_uuid in (
            _build_old_showtime_uuid(showtime["show_information"]),
            _build_new_showtime_uuid(showtime["show_information"]),
        ):
            return showtime
    return None


def _get_showtimes_uuid_by_idAtProvider(id_at_provider: str) -> str:
    return id_at_provider.split("#")[1]


def _build_movie_uuid(movie_information_id: str, venue: Venue) -> str:
    """This must be unique, among all Providers and Venues"""
    return f"{movie_information_id}%{venue.id}%CDS"


def _build_new_showtime_uuid(showtime_details: ShowCDS) -> str:
    return str(showtime_details.id)


# TODO (dramelet, 2024-02-09) Remove this and rename the upper function
# in a few months when we won't have any Stocks using the old construct
# of the `idAtProviders`
def _build_old_showtime_uuid(showtime_details: ShowCDS) -> str:
    return f"{showtime_details.id}/{showtime_details.showtime}"


def _get_old_and_new_id_at_providers(id_at_providers: str) -> tuple[str, str]:
    return id_at_providers, id_at_providers.split("/")[0]


def _build_stock_uuid(movie_information_id: str, venue: Venue, showtime_details: ShowCDS) -> str:
    # TODO (dramelet, 2024-02-09): In a few months, we will be able to safely build
    # `idAtProviders` without the showtime. But for now, we need to be able to match a stock
    # in both ways.
    return f"{_build_movie_uuid(movie_information_id, venue)}#{_build_old_showtime_uuid(showtime_details)}"


def _clean_cds_id_at_providers(cds_stock_id_at_providers: str) -> str:
    """We don't want to build `idAtProviders` using showtime anymore, like this:
        51%547%CDS#2/2022-07-01 12:00:00+02:00"

    The provider showtime.id is enough (as for any others providers), which look like this:
        51%547%CDS#2
    """
    return cds_stock_id_at_providers.split("/")[0]
