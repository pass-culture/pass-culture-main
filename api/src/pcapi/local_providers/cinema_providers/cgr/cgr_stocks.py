import datetime
import decimal
import logging
from typing import Iterator

from pcapi.connectors.cgr.cgr import get_movie_poster_from_api
from pcapi.connectors.serialization import cgr_serializers
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.external_bookings.cgr.client import CGRClientAPI
from pcapi.core.external_bookings.cgr.exceptions import CGRAPIException
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offers import api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.offers.repository as offers_repository
import pcapi.core.providers.models as providers_models
from pcapi.local_providers.cinema_providers.constants import ShowtimeFeatures
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.repository.providable_queries import get_last_update_for_provider
from pcapi.utils import date as utils_date


PREVIEW_SHOW = "avant première"
ICE_CINE_SHOW = "salle ICE"

logger = logging.getLogger(__name__)


class CGRStocks(LocalProvider):
    name = "CGR"
    can_create = True

    def __init__(self, venue_provider: providers_models.VenueProvider):
        super().__init__(venue_provider)
        self.venue = venue_provider.venue
        self.cinema_id = venue_provider.venueIdAtOfferProvider
        self.cgr_client_api = CGRClientAPI(self.cinema_id)
        self.isDuo = bool(venue_provider.isDuoOffers)
        self.films: Iterator[cgr_serializers.Film] = iter(self.cgr_client_api.get_films())
        self.last_offer: offers_models.Offer | None = None
        self.price_category_labels: list[offers_models.PriceCategoryLabel] = (
            offers_models.PriceCategoryLabel.query.filter(offers_models.PriceCategoryLabel.venue == self.venue).all()
        )
        self.price_category_lists_by_offer: dict[offers_models.Offer, list[offers_models.PriceCategory]] = {}
        self.provider = venue_provider.provider

    def __next__(self) -> list[ProvidableInfo]:
        self.film_infos = next(self.films)
        self.product = self.get_or_create_movie_product(self.film_infos)
        providable_information_list = []
        provider_offer_unique_id = _build_movie_uuid_for_offer(self.film_infos.IDFilmAlloCine, self.venue)

        offer_providable_info = self.create_providable_info(
            pc_object=offers_models.Offer,
            id_at_providers=provider_offer_unique_id,
            date_modified_at_provider=datetime.datetime.utcnow(),
            new_id_at_provider=provider_offer_unique_id,
        )
        providable_information_list.append(offer_providable_info)

        for show in self.film_infos.Seances:
            stock_showtime_unique_id = _build_stock_uuid(self.film_infos.IDFilm, self.venue, show.IDSeance)
            stock_providable_info = self.create_providable_info(
                pc_object=offers_models.Stock,
                id_at_providers=stock_showtime_unique_id,
                date_modified_at_provider=datetime.datetime.utcnow(),
                new_id_at_provider=stock_showtime_unique_id,
            )
            providable_information_list.append(stock_providable_info)

        return providable_information_list

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
            offer.name = self.film_infos.Titre
            offer.description = self.film_infos.Synopsis
            offer.durationMinutes = self.film_infos.Duree

        offer.extraData["allocineId"] = offer.extraData.get("allocineId") or self.film_infos.IDFilmAlloCine
        if self.film_infos.NumVisa:
            offer.extraData["visa"] = offer.extraData.get("visa") or str(self.film_infos.NumVisa)

        offer.product = self.product

    def fill_offer_attributes(self, offer: offers_models.Offer) -> None:
        offer.venueId = self.venue.id
        offer.offererAddress = self.venue.offererAddress
        offer.bookingEmail = self.venue.bookingEmail
        offer.withdrawalDetails = self.venue.withdrawalDetails
        offer.subcategoryId = subcategories.SEANCE_CINE.id

        self.update_from_movie_information(offer)

        is_new_offer_to_insert = offer.id is None
        if is_new_offer_to_insert:
            offer.isDuo = self.isDuo
            offer.id = offers_repository.get_next_offer_id_from_database()

        last_update_for_current_provider = get_last_update_for_provider(self.provider.id, offer)
        if not last_update_for_current_provider or last_update_for_current_provider.date() != datetime.date.today():
            if self.film_infos.Affiche:
                image_url = self.film_infos.Affiche
                try:
                    image = get_movie_poster_from_api(image_url)
                except CGRAPIException:
                    image = None
                    logger.info(
                        "Could not fetch movie poster",
                        extra={
                            "provider": "cgr",
                            "url": image_url,
                        },
                    )
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

    def fill_stock_attributes(self, stock: offers_models.Stock) -> None:
        assert self.last_offer
        stock.offer = self.last_offer

        showtime_cgr_id = _get_showtime_cgr_id_from_id_at_provider(stock.idAtProviders)
        if not showtime_cgr_id:
            self.log_provider_event(
                providers_models.LocalProviderEventType.SyncError,
                f"Error when trying to get showtime_cgr_id from idAtproviders={stock.idAtProviders}",
            )
            return
        showtime = _find_showtime_by_showtime_cgr_id(self.film_infos.Seances, showtime_cgr_id)
        if not showtime:
            self.log_provider_event(
                providers_models.LocalProviderEventType.SyncError, f"Show {showtime_cgr_id} not found in shows list"
            )
            return
        local_tz = utils_date.get_department_timezone(self.venue.departementCode)
        show_datetime = utils_date.local_datetime_to_default_timezone(
            datetime.datetime.combine(showtime.Date, showtime.Heure), local_tz
        )
        show_datetime = show_datetime.astimezone(tz=datetime.timezone.utc).replace(
            tzinfo=None
        )  # to enable comparison in finance event update
        old_beginning_datetime = stock.beginningDatetime
        stock.beginningDatetime = show_datetime
        stock.bookingLimitDatetime = show_datetime
        self.maybe_update_finance_event_pricing_date(stock, old_beginning_datetime)

        is_new_stock_to_insert = stock.id is None
        if is_new_stock_to_insert:
            stock.fieldsUpdated = []

        if "quantity" not in stock.fieldsUpdated:
            booked_quantity = 0 if is_new_stock_to_insert else stock.dnBookedQuantity
            stock.quantity = showtime.NbPlacesRestantes + booked_quantity

        show_price = decimal.Decimal(str(showtime.PrixUnitaire))
        price_label = showtime.libTarif

        features = [ShowtimeFeatures.VF.value if showtime.Version == "VF" else ShowtimeFeatures.VO.value]
        if showtime.Relief == "3D":
            features.append(ShowtimeFeatures.THREE_D.value)
        if showtime.bICE:
            features.append(ShowtimeFeatures.ICE.value)
        stock.features = features

        if "price" not in stock.fieldsUpdated:
            stock.price = show_price
            price_category = self.get_or_create_price_category(show_price, price_label)

            stock.priceCategory = price_category

    def get_or_create_price_category(self, price: decimal.Decimal, price_label: str) -> offers_models.PriceCategory:
        assert self.last_offer
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

    def get_or_create_movie_product(self, movie: cgr_serializers.Film) -> offers_models.Product | None:
        generic_movie = movie.to_generic_movie()
        id_at_providers = _build_movie_uuid_for_offer(movie.IDFilmAlloCine, self.venue)
        product = offers_api.upsert_movie_product_from_provider(generic_movie, self.provider, id_at_providers)

        return product

    def get_object_thumb(self) -> bytes:
        if self.film_infos.Affiche:
            image_url = self.film_infos.Affiche
            return get_movie_poster_from_api(image_url)
        return bytes()

    def shall_synchronize_thumbs(self) -> bool:
        return True

    def get_keep_poster_ratio(self) -> bool:
        return True


def _build_movie_uuid_for_offer(allocine_film_id: int, venue: offerers_models.Venue) -> str:
    return f"{allocine_film_id}%{venue.id}%CGR"


def _build_stock_uuid(film_id: int, venue: offerers_models.Venue, showtime_id: int) -> str:
    return f"{_build_movie_uuid_for_offer(film_id, venue)}#{showtime_id}"


def _get_showtime_cgr_id_from_id_at_provider(id_at_provider: str | None) -> int | None:
    if not id_at_provider:
        return None
    return int(id_at_provider.split("#")[1])


def _find_showtime_by_showtime_cgr_id(
    showtimes: list[cgr_serializers.Seance], showtime_id: int
) -> cgr_serializers.Seance | None:
    for showtime in showtimes:
        if showtime.IDSeance == showtime_id:
            return showtime
    return None
