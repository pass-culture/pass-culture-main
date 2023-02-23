import datetime
from typing import Iterator

from sqlalchemy import Sequence

from pcapi.connectors.cgr.cgr import get_movie_poster_from_api
from pcapi.connectors.serialization import cgr_serializers
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.cgr.client import CGRClientAPI
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.models as providers_models
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.models import db


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
        self.last_product_id: int | None = None
        self.last_offer: offers_models.Offer | None = None

    def __next__(self) -> list[ProvidableInfo]:
        self.film_infos = next(self.films)

        providable_information_list = []
        # The Product ID must be unique
        provider_product_unique_id = _build_movie_uuid_for_product(self.film_infos.IDFilmAlloCine)
        provider_offer_unique_id = _build_movie_uuid_for_offer(self.film_infos.IDFilmAlloCine, self.venue)
        product_providable_info = self.create_providable_info(
            pc_object=offers_models.Product,
            id_at_providers=provider_product_unique_id,
            date_modified_at_provider=datetime.datetime.utcnow(),
            new_id_at_provider=provider_product_unique_id,
        )
        providable_information_list.append(product_providable_info)

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
        if isinstance(pc_object, offers_models.Product):
            self.fill_product_attributes(pc_object)

        if isinstance(pc_object, offers_models.Offer):
            self.fill_offer_attributes(pc_object)

        if isinstance(pc_object, offers_models.Stock):
            self.fill_stock_attributes(pc_object)

    def fill_product_attributes(self, product: offers_models.Product) -> None:
        product.name = self.film_infos.Titre
        product.subcategoryId = subcategories.SEANCE_CINE.id
        product.description = self.film_infos.Synopsis
        product.durationMinutes = self.film_infos.Duree
        if product.extraData is None:
            product.extraData = {}
        if self.film_infos.NumVisa:
            product.extraData["visa"] = str(self.film_infos.NumVisa)

        is_new_product_to_insert = product.id is None

        if is_new_product_to_insert:
            product.id = get_next_product_id_from_database()
        self.last_product_id = product.id

    def fill_offer_attributes(self, offer: offers_models.Offer) -> None:
        offer.venueId = self.venue.id
        offer.name = self.film_infos.Titre
        offer.description = self.film_infos.Synopsis
        offer.bookingEmail = self.venue.bookingEmail
        offer.withdrawalDetails = self.venue.withdrawalDetails
        offer.durationMinutes = self.film_infos.Duree
        offer.subcategoryId = subcategories.SEANCE_CINE.id
        if offer.extraData is None:
            offer.extraData = {}
        if self.film_infos.NumVisa:
            offer.extraData["visa"] = str(self.film_infos.NumVisa)
        assert self.last_product_id
        offer.productId = self.last_product_id

        is_new_offer_to_insert = offer.id is None

        if is_new_offer_to_insert:
            offer.isDuo = self.isDuo

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

        stock.beginningDatetime = datetime.datetime.combine(showtime.Date, showtime.Heure)
        stock.bookingLimitDatetime = datetime.datetime.combine(showtime.Date, showtime.Heure)

        is_new_stock_to_insert = stock.id is None
        if is_new_stock_to_insert:
            stock.fieldsUpdated = []

        if "quantity" not in stock.fieldsUpdated:
            stock.quantity = showtime.NbPlacesRestantes

        if "price" not in stock.fieldsUpdated:
            stock.price = showtime.PrixUnitaire

        if not is_new_stock_to_insert:
            stock.quantity = showtime.NbPlacesRestantes + stock.dnBookedQuantity

    def get_object_thumb(self) -> bytes:
        if self.film_infos.Affiche:
            image_url = self.film_infos.Affiche
            return get_movie_poster_from_api(image_url)
        return bytes()

    def shall_synchronize_thumbs(self) -> bool:
        return True

    def get_keep_poster_ratio(self) -> bool:
        return True


def _build_movie_uuid_for_product(allocine_film_id: int) -> str:
    return f"{allocine_film_id}%CGR"


def _build_movie_uuid_for_offer(allocine_film_id: int, venue: offerers_models.Venue) -> str:
    return f"{allocine_film_id}%{venue.id}%CGR"


def _build_stock_uuid(film_id: int, venue: offerers_models.Venue, showtime_id: int) -> str:
    return f"{_build_movie_uuid_for_offer(film_id, venue)}#{showtime_id}"


def get_next_product_id_from_database() -> int:
    sequence: Sequence = Sequence("product_id_seq")
    return db.session.execute(sequence)


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
