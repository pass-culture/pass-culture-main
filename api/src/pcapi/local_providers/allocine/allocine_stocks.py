from datetime import datetime
import decimal
import logging

from pcapi.connectors.serialization import allocine_serializers
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.providers.allocine_movie_list import create_product
import pcapi.core.providers.models as providers_models
from pcapi.domain.allocine import get_movie_poster
from pcapi.domain.allocine import get_movies_showtimes
from pcapi.domain.price_rule import AllocineStocksPriceRule
from pcapi.domain.price_rule import PriceRule
from pcapi.local_providers.cinema_providers.constants import ShowtimeFeatures
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.repository import db
from pcapi.repository import transaction
from pcapi.repository.providable_queries import get_last_update_for_provider
from pcapi.utils.date import get_department_timezone
from pcapi.utils.date import local_datetime_to_default_timezone


logger = logging.getLogger(__name__)

ACCEPTED_FEATURES_MAPPING = {
    allocine_serializers.AllocineShowtimeDiffusionVersion.DUBBED: ShowtimeFeatures.VF.value,
    allocine_serializers.AllocineShowtimeDiffusionVersion.LOCAL: ShowtimeFeatures.VF.value,
    allocine_serializers.AllocineShowtimeDiffusionVersion.ORIGINAL: ShowtimeFeatures.VO.value,
}


class AllocineStocks(LocalProvider):
    name = "Allociné"
    can_create = True

    def __init__(self, allocine_venue_provider: providers_models.AllocineVenueProvider):
        super().__init__(allocine_venue_provider)
        self.venue = allocine_venue_provider.venue
        self.theater_id = allocine_venue_provider.venueIdAtOfferProvider
        self.movies_showtimes = get_movies_showtimes(self.theater_id)
        self.isDuo = allocine_venue_provider.isDuo
        self.quantity = allocine_venue_provider.quantity
        self.room_internal_id = allocine_venue_provider.internalId
        self.price_and_price_rule_tuples: list[tuple[decimal.Decimal, PriceRule]] = (
            providers_models.AllocineVenueProviderPriceRule.query.filter(
                providers_models.AllocineVenueProviderPriceRule.allocineVenueProvider == allocine_venue_provider
            )
            .with_entities(
                providers_models.AllocineVenueProviderPriceRule.price,
                providers_models.AllocineVenueProviderPriceRule.priceRule,
            )
            .all()
        )

        self.movie: allocine_serializers.AllocineMovie
        self.showtimes: list[allocine_serializers.AllocineShowtime]
        self.label: offers_models.PriceCategoryLabel = offers_api.get_or_create_label("Tarif unique", self.venue)
        self.price_categories_by_offer: dict[offers_models.Offer, list[offers_models.PriceCategory]] = {}

    def __next__(self) -> list[ProvidableInfo]:
        movie_showtimes = next(self.movies_showtimes)
        self.movie = movie_showtimes.movie

        # FIXME (thconte: 2024-02-23)
        # We take advantage of the data received with this synchro to speed up
        # the completion of our product table with allocine movies until we are
        # confident that almost all scheduled movies are already known.
        # On the long term, this line should only be `get_movie_product`.
        # This can be measured with the occurences of the logs with
        # `technical_message_id=allocineId.not_found`
        self.product = self.get_or_create_movie_product(self.movie)

        self.showtimes = _filter_only_digital_and_non_experience_showtimes(movie_showtimes.showtimes)

        providable_information_list = []

        venue_movie_unique_id = _build_movie_uuid(self.movie, self.venue)
        offer_providable_information = self.create_providable_info(
            offers_models.Offer,
            id_at_providers=venue_movie_unique_id,
            new_id_at_provider=venue_movie_unique_id,
            date_modified_at_provider=datetime.utcnow(),
        )
        providable_information_list.append(offer_providable_information)

        for showtime in self.showtimes:
            id_at_providers = _build_stock_uuid(self.movie, self.venue, showtime)
            stock_providable_information = self.create_providable_info(
                offers_models.Stock,
                id_at_providers=id_at_providers,
                new_id_at_provider=id_at_providers,
                date_modified_at_provider=datetime.utcnow(),
            )
            providable_information_list.append(stock_providable_information)

        return providable_information_list

    def fill_object_attributes(self, pc_object: Model) -> None:
        if isinstance(pc_object, offers_models.Offer):
            self.fill_offer_attributes(pc_object)

        if isinstance(pc_object, offers_models.Stock):
            self.fill_stock_attributes(pc_object)

    def update_from_movie_information(self, offer: offers_models.Offer) -> None:
        offer.name = self.product.name
        offer.extraData = offer.extraData or offers_models.OfferExtraData()
        offer.description = self.product.description
        offer.durationMinutes = self.product.durationMinutes
        offer.product = self.product
        if self.product.extraData:
            offer.extraData.update(self.product.extraData)

        offer.extraData["theater"] = {
            "allocine_movie_id": self.movie.internalId,
            "allocine_room_id": self.room_internal_id,
        }

    def fill_offer_attributes(self, offer: offers_models.Offer) -> None:
        offer.venueId = self.venue.id
        offer.bookingEmail = self.venue.bookingEmail
        offer.withdrawalDetails = self.venue.withdrawalDetails
        offer.subcategoryId = subcategories.SEANCE_CINE.id
        self.update_from_movie_information(offer)

        if offer.id is None:  # Newly created offer
            offer.isDuo = self.isDuo

        last_update_for_current_provider = get_last_update_for_provider(self.provider.id, offer)
        if not last_update_for_current_provider or last_update_for_current_provider.date() != datetime.today().date():
            if image := self.get_object_thumb():
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

    def fill_stock_attributes(self, allocine_stock: offers_models.Stock) -> None:
        showtime_uuid = _get_showtimes_uuid_by_idAtProvider(allocine_stock.idAtProviders)  # type: ignore [arg-type]
        showtime = _find_showtime_by_showtime_uuid(self.showtimes, showtime_uuid)
        if not showtime:
            self.log_provider_event(
                providers_models.LocalProviderEventType.SyncError,
                f"Error: showtime with UUID {showtime_uuid} cannot be found",
            )
            logger.warning(
                "Showtime with UUID %s cannot be found",
                showtime_uuid,
                extra={"allocineId": self.movie.internalId, "theaterId": self.theater_id},
            )
            return

        allocine_stock.offer = self.last_offer
        if showtime.diffusionVersion in ACCEPTED_FEATURES_MAPPING:
            allocine_stock.features = [ACCEPTED_FEATURES_MAPPING.get(showtime.diffusionVersion)]

        local_tz = get_department_timezone(self.venue.departementCode)
        date_in_utc = local_datetime_to_default_timezone(showtime.startsAt, local_tz)
        allocine_stock.beginningDatetime = date_in_utc

        is_new_stock_to_insert = allocine_stock.id is None
        if is_new_stock_to_insert:
            allocine_stock.fieldsUpdated = []

        if "bookingLimitDatetime" not in allocine_stock.fieldsUpdated:
            allocine_stock.bookingLimitDatetime = date_in_utc

        if "quantity" not in allocine_stock.fieldsUpdated:
            allocine_stock.quantity = self.quantity

        if "price" not in allocine_stock.fieldsUpdated:
            price = self.apply_allocine_price_rule(allocine_stock)
            if allocine_stock.priceCategory is None:
                allocine_stock.price = price
                allocine_stock.priceCategory = self.get_or_create_allocine_price_category(price, allocine_stock)

            if allocine_stock.priceCategory.label == "Tarif unique":
                allocine_stock.price = price
                allocine_stock.priceCategory.price = price

    def get_or_create_allocine_price_category(
        self, price: decimal.Decimal, allocine_stock: offers_models.Stock
    ) -> offers_models.PriceCategory:
        offer = allocine_stock.offer
        if not offer in self.price_categories_by_offer:
            self.price_categories_by_offer[offer] = (
                offers_models.PriceCategory.query.filter_by(offer=offer)
                .order_by(offers_models.PriceCategory.id.desc())
                .all()
                if offer.id
                else []
            )
        price_categories = (category for category in self.price_categories_by_offer[offer] if category.price == price)
        price_category = next(price_categories, None)
        if price_category:
            return price_category

        price_category = offers_models.PriceCategory(priceCategoryLabel=self.label, price=price, offer=offer)
        self.price_categories_by_offer[offer].insert(0, price_category)
        return price_category

    def get_or_create_movie_product(self, movie: allocine_serializers.AllocineMovie) -> offers_models.Product:
        product = offers_models.Product.query.filter(
            offers_models.Product.extraData["allocineId"] == str(movie.internalId)
        ).one_or_none()

        if not product:
            with transaction():
                product = create_product(movie)
                db.session.add(product)

            logger.info(
                "Product created for allocine Id %d",
                movie.internalId,
                extra={"allocineId": movie.internalId, "theaterId": self.theater_id},
                technical_message_id="allocineId.not_found",
            )

        return product

    def apply_allocine_price_rule(self, allocine_stock: offers_models.Stock) -> decimal.Decimal:
        for price, price_rule in self.price_and_price_rule_tuples:
            if price_rule(allocine_stock):
                return price
        raise AllocineStocksPriceRule("Aucun prix par défaut n'a été trouvé")

    def get_object_thumb(self) -> bytes:
        if self.movie and self.movie.poster:
            image_url = str(self.movie.poster.url)
            return get_movie_poster(image_url)
        return bytes()

    def shall_synchronize_thumbs(self) -> bool:
        return True


def _filter_only_digital_and_non_experience_showtimes(
    showtimes_information: list[allocine_serializers.AllocineShowtime],
) -> list[allocine_serializers.AllocineShowtime]:
    return list(
        filter(
            lambda showtime: showtime.projection == allocine_serializers.AllocineShowtimeProjection.DIGITAL
            and showtime.experience is None,
            showtimes_information,
        )
    )


def _find_showtime_by_showtime_uuid(
    showtimes: list[allocine_serializers.AllocineShowtime], showtime_uuid: str
) -> allocine_serializers.AllocineShowtime | None:
    for showtime in showtimes:
        if _build_showtime_uuid(showtime) == showtime_uuid:
            return showtime
    return None


def _get_showtimes_uuid_by_idAtProvider(id_at_provider: str) -> str:
    return id_at_provider.split("#")[1]


def _build_movie_uuid(movie: allocine_serializers.AllocineMovie, venue: Venue) -> str:
    return f"{movie.id}%{venue.id if not venue.siret else venue.siret}"


def _build_showtime_uuid(showtime: allocine_serializers.AllocineShowtime) -> str:
    return f"{showtime.diffusionVersion.value}/{showtime.startsAt.isoformat()}"


def _build_stock_uuid(
    movie: allocine_serializers.AllocineMovie, venue: Venue, showtime: allocine_serializers.AllocineShowtime
) -> str:
    return f"{_build_movie_uuid(movie, venue)}#{_build_showtime_uuid(showtime)}"
