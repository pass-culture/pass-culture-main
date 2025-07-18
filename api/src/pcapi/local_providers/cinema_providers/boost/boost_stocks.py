import decimal
import logging
import uuid
from datetime import datetime
from typing import Iterator

import PIL

from pcapi import settings
from pcapi.connectors import thumb_storage
from pcapi.connectors.serialization import boost_serializers
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.boost.client import BoostClientAPI
from pcapi.core.external_bookings.boost.client import get_pcu_pricing_if_exists
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.providers.models import VenueProvider
from pcapi.local_providers.cinema_providers.constants import ShowtimeFeatures
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.movie_festivals import api as movie_festivals_api
from pcapi.local_providers.movie_festivals import constants as movie_festivals_constants
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.models import db
from pcapi.repository.providable_queries import get_last_update_for_provider
from pcapi.utils.date import get_naive_utc_now


logger = logging.getLogger(__name__)

ACCEPTED_VERSIONS_MAPPING = {
    "VF": ShowtimeFeatures.VF.value,
    "VO": ShowtimeFeatures.VO.value,
}

ACCEPTED_FORMATS_MAPPING = {"3D": ShowtimeFeatures.THREE_D.value}

ACCEPTED_ATTRIBUT_MAPPING = {"ICE Immersive": ShowtimeFeatures.ICE.value}


class BoostStocks(LocalProvider):
    name = "Boost"
    can_create = True

    def __init__(
        self,
        venue_provider: VenueProvider,
        enable_debug: bool = False,
    ):
        super().__init__(venue_provider)
        self.venue = venue_provider.venue
        self._boost_api_client = BoostClientAPI(
            venue_provider.venueIdAtOfferProvider,
            request_timeout=settings.EXTERNAL_BOOKINGS_TIMEOUT_IN_SECONDS,
            enable_debug=enable_debug,
        )
        self.isDuo = venue_provider.isDuoOffers if venue_provider.isDuoOffers else False
        self.attributs: list[boost_serializers.CinemaAttribut] = self._boost_api_client.get_cinemas_attributs()
        self.showtimes: Iterator[boost_serializers.ShowTime4] = iter(self._boost_api_client.get_showtimes())
        self.price_category_labels: list[offers_models.PriceCategoryLabel] = (
            db.session.query(offers_models.PriceCategoryLabel)
            .filter(offers_models.PriceCategoryLabel.venue == self.venue)
            .all()
        )

        self.price_category_lists_by_offer: dict[offers_models.Offer, list[offers_models.PriceCategory]] = {}
        self.provider = venue_provider.provider

    def __next__(self) -> list[ProvidableInfo]:
        showtime = next(self.showtimes)
        self.product = self.get_or_create_movie_product(showtime.film)
        self.showtime_details = showtime
        self.pcu_pricing: boost_serializers.ShowtimePricing | None = get_pcu_pricing_if_exists(
            self.showtime_details.showtimePricing
        )
        if not self.pcu_pricing:
            return []

        providable_information_list = []

        provider_movie_unique_id = _build_movie_uuid(self.showtime_details.film.id, self.venue)
        offer_providable_info = self.create_providable_info(
            offers_models.Offer, provider_movie_unique_id, datetime.utcnow(), provider_movie_unique_id
        )
        providable_information_list.append(offer_providable_info)

        showtime_id = _build_stock_uuid(self.showtime_details.film.id, self.venue, self.showtime_details.id)
        stock_providable_info = self.create_providable_info(
            offers_models.Stock, showtime_id, datetime.utcnow(), showtime_id
        )
        providable_information_list.append(stock_providable_info)

        return providable_information_list

    def fill_object_attributes(self, pc_object: Model) -> None:
        if isinstance(pc_object, offers_models.Offer):
            self.fill_offer_attributes(pc_object)

        if isinstance(pc_object, offers_models.Stock):
            self.fill_stock_attributes(pc_object)

    def update_from_movie_information(
        self, offer: offers_models.Offer, movie_information: boost_serializers.Film2
    ) -> None:
        if self.product:
            offer.name = self.product.name
            offer.description = None
            offer.durationMinutes = None
            offer.extraData = None
        else:
            offer.name = self.showtime_details.film.titleCnc
            if movie_information.duration:
                offer.durationMinutes = movie_information.duration

            offer.extraData = offer._extraData or offers_models.OfferExtraData()
            if movie_information.numVisa != 0:
                offer.extraData["visa"] = offer.extraData.get("visa") or str(movie_information.numVisa)

        offer.product = self.product

    def fill_offer_attributes(self, offer: offers_models.Offer) -> None:
        offer.venueId = self.venue.id
        offer.offererAddress = self.venue.offererAddress
        offer.bookingEmail = self.venue.bookingEmail
        offer.withdrawalDetails = self.venue.withdrawalDetails
        offer.subcategoryId = subcategories.SEANCE_CINE.id
        offer.publicationDatetime = offer.publicationDatetime or get_naive_utc_now()
        self.update_from_movie_information(offer, self.showtime_details.film)

        is_new_offer_to_insert = offer.id is None
        if is_new_offer_to_insert:
            offer.isDuo = self.isDuo
            offer.id = offers_repository.get_next_offer_id_from_database()

        last_update_for_current_provider = get_last_update_for_provider(self.provider.id, offer)

        if not last_update_for_current_provider or last_update_for_current_provider.date() != datetime.today().date():
            if self.showtime_details.film.posterUrl:
                image = self._boost_api_client.get_movie_poster(self.showtime_details.film.posterUrl)
                if image and self.product and not self.product.productMediations:
                    try:
                        image_id = str(uuid.uuid4())
                        mediation = offers_models.ProductMediation(
                            productId=self.product.id,
                            lastProvider=self.provider,
                            imageType=offers_models.ImageType.POSTER,
                            uuid=image_id,
                        )
                        db.session.add(mediation)
                        thumb_storage.create_thumb(
                            self.product,
                            image,
                            storage_id_suffix_str="",
                            keep_ratio=True,
                            object_id=image_id,
                        )
                        db.session.flush()

                        self.createdThumbs += 1
                    except (offers_exceptions.ImageValidationError, PIL.UnidentifiedImageError) as e:
                        self.erroredThumbs += 1
                        logger.warning("Error: Offer image could not be created. Reason: %s", e)
        self.last_offer = offer

    def fill_stock_attributes(self, stock: offers_models.Stock) -> None:
        stock.offer = self.last_offer
        # a pydantic validator has already converted the showDate to a UTC datetime
        old_beginning_datetime = stock.beginningDatetime
        stock.beginningDatetime = self.showtime_details.showDate
        stock.bookingLimitDatetime = self.showtime_details.showDate
        self.maybe_update_finance_event_pricing_date(stock, old_beginning_datetime)

        is_new_stock_to_insert = stock.id is None
        if is_new_stock_to_insert:
            stock.fieldsUpdated = []

        if "quantity" not in stock.fieldsUpdated:
            booked_quantity = 0 if is_new_stock_to_insert else stock.dnBookedQuantity
            stock.quantity = self.showtime_details.numberSeatsRemaining + booked_quantity

        features = (
            [ACCEPTED_VERSIONS_MAPPING.get(self.showtime_details.version["code"])]
            if self.showtime_details.version["code"] in ACCEPTED_VERSIONS_MAPPING
            else []
        )
        if self.showtime_details.format["title"] in ACCEPTED_FORMATS_MAPPING:
            features.append(ACCEPTED_FORMATS_MAPPING.get(self.showtime_details.format["title"]))

        showtime_attributs = []
        for attribut in self.attributs:
            if (
                accepted_attribut := ACCEPTED_ATTRIBUT_MAPPING.get(attribut.title)
            ) and attribut.id in self.showtime_details.attributs:
                showtime_attributs.append(accepted_attribut)

        features.extend(showtime_attributs)

        stock.features = features

        if movie_festivals_api.should_apply_movie_festival_rate(stock.offer.id, stock.beginningDatetime.date()):
            stock.price = movie_festivals_constants.FESTIVAL_RATE
            stock.priceCategory = self.get_or_create_price_category(
                movie_festivals_constants.FESTIVAL_RATE,
                movie_festivals_constants.FESTIVAL_NAME,
            )
        elif "price" not in stock.fieldsUpdated:
            assert self.pcu_pricing  # helps mypy
            price = self.pcu_pricing.amountTaxesIncluded
            stock.price = price

            price_label = self.pcu_pricing.title
            price_category = self.get_or_create_price_category(price, price_label)
            stock.priceCategory = price_category

    def get_or_create_movie_product(self, movie: boost_serializers.Film2) -> offers_models.Product | None:
        generic_movie = movie.to_generic_movie()
        id_at_providers = _build_movie_uuid(movie.id, self.venue)
        product = offers_api.upsert_movie_product_from_provider(generic_movie, self.provider, id_at_providers)

        return product

    def get_or_create_price_category(self, price: decimal.Decimal, price_label: str) -> offers_models.PriceCategory:
        if self.last_offer not in self.price_category_lists_by_offer:
            self.price_category_lists_by_offer[self.last_offer] = (
                db.session.query(offers_models.PriceCategory)
                .filter(offers_models.PriceCategory.offer == self.last_offer)
                .all()
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
        image_url = self.showtime_details.film.posterUrl
        return self._boost_api_client.get_movie_poster(image_url) if image_url else bytes()

    def shall_synchronize_thumbs(self) -> bool:
        return True

    def get_keep_poster_ratio(self) -> bool:
        return True


def _build_movie_uuid(film_id: int, venue: Venue) -> str:
    return f"{film_id}%{venue.id}%Boost"


def _build_stock_uuid(film_id: int, venue: Venue, showtime_id: int) -> str:
    return f"{_build_movie_uuid(film_id, venue)}#{showtime_id}"
