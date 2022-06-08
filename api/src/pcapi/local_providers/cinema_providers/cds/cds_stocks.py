from datetime import datetime
from typing import Iterator
from typing import Union

from sqlalchemy import Sequence

from pcapi import settings
from pcapi.core.booking_providers.cds.client import CineDigitalServiceAPI
from pcapi.core.booking_providers.models import Movie
from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer
from pcapi.core.providers.models import VenueProvider
from pcapi.core.providers.repository import get_cds_cinema_api_token
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.product import Product


class CDSStocks(LocalProvider):
    name = "CDS"
    can_create = True

    def __init__(self, venue_provider: VenueProvider):
        super().__init__(venue_provider)
        self.apiUrl = settings.CDS_API_URL
        self.venue = venue_provider.venue
        self.cinema_id = venue_provider.venueIdAtOfferProvider
        self.isDuo = venue_provider.isDuoOffers if venue_provider.isDuoOffers else False
        self.movies: Iterator[Movie] = iter(self._get_cds_movies())

    def __next__(self) -> list[ProvidableInfo]:

        movie_infos = next(self.movies)
        if movie_infos:
            self.movie_information = movie_infos

        product_providable_info = self.create_providable_info(
            Product, self.movie_information.id, datetime.utcnow(), self.movie_information.id
        )
        offer_providable_info = self.create_providable_info(
            Offer, self.movie_information.id, datetime.utcnow(), self.movie_information.id
        )

        return [product_providable_info, offer_providable_info]

    def fill_object_attributes(self, pc_object: Model) -> None:
        if isinstance(pc_object, Product):
            self.fill_product_attributes(pc_object)

        if isinstance(pc_object, Offer):
            self.fill_offer_attributes(pc_object)

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

    def update_from_movie_information(self, obj: Union[Offer, Product], movie_information: Movie) -> None:
        if movie_information.description:
            obj.description = movie_information.description
        if self.movie_information.duration:
            obj.durationMinutes = movie_information.duration
        if not obj.extraData:
            obj.extraData = {}
        obj.extraData = {"visa": self.movie_information.visa}

    def _get_cds_movies(self) -> list[Movie]:
        if not self.apiUrl:
            raise Exception("CDS API URL not configured in this env")
        client_cds = CineDigitalServiceAPI(
            cinema_id=self.venue_provider.venueIdAtOfferProvider,
            api_url=self.apiUrl,
            cinema_api_token=get_cds_cinema_api_token(self.venue_provider.venueIdAtOfferProvider),
        )
        return client_cds.get_venue_movies()


def get_next_product_id_from_database():  # type: ignore [no-untyped-def]
    sequence = Sequence("product_id_seq")
    return db.session.execute(sequence)


def get_next_offer_id_from_database():  # type: ignore [no-untyped-def]
    sequence = Sequence("offer_id_seq")
    return db.session.execute(sequence)
