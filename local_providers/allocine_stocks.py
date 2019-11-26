import os
import re
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Sequence

from domain.allocine import get_movies_showtimes, get_movie_poster
from local_providers.local_provider import LocalProvider
from local_providers.providable_info import ProvidableInfo
from models import VenueProvider, Offer, Product, EventType
from models.db import Model, db
from models.local_provider_event import LocalProviderEventType

DUBBED_VERSION = 'DUBBED'
LOCAL_VERSION = 'LOCAL'
ORIGINAL_VERSION = 'ORIGINAL'
FRENCH_VERSION_SUFFIX = 'VF'
ORIGINAL_VERSION_SUFFIX = 'VO'


class AllocineStocks(LocalProvider):
    name = "Allociné"
    can_create = True

    def __init__(self, venue_provider: VenueProvider):
        super().__init__(venue_provider)
        self.api_key = os.environ.get('ALLOCINE_API_KEY', None)
        self.venue = venue_provider.venue
        self.theater_id = venue_provider.venueIdAtOfferProvider
        self.movies_showtimes = get_movies_showtimes(self.api_key, self.theater_id)
        self.last_product_id = None
        self.movie_information = None

    def __next__(self) -> List[ProvidableInfo]:
        raw_movie_information = next(self.movies_showtimes)
        try:
            self.movie_information = retrieve_movie_information(raw_movie_information['node']['movie'])
            self.movie_showtimes = raw_movie_information['node']['showtimes']
        except KeyError:
            self.log_provider_event(LocalProviderEventType.SyncError,
                                    f"Error parsing information for movie: {raw_movie_information['node']['movie']}")
            return []

        providable_information_list = [self.create_providable_info(Product,
                                                                   self.movie_information['id'],
                                                                   datetime.utcnow())]
        print(providable_information_list)
        if _has_original_version_product(self.movie_showtimes):
            print('has original')
            offer_vo_providable_information = self.create_providable_info(Offer,
                                                                          f"{self.movie_information['id']}-{ORIGINAL_VERSION_SUFFIX}",
                                                                          datetime.utcnow())
            providable_information_list.append(offer_vo_providable_information)

        if _has_french_version_product(self.movie_showtimes):
            print('has french')
            offer_vf_providable_information = self.create_providable_info(Offer,
                                                                          f"{self.movie_information['id']}-{FRENCH_VERSION_SUFFIX}",
                                                                          datetime.utcnow())
            providable_information_list.append(offer_vf_providable_information)
        print(providable_information_list)
        return providable_information_list


    def fill_object_attributes(self, pc_object: Model):
        if isinstance(pc_object, Product):
            self.fill_product_attributes(pc_object)

        if isinstance(pc_object, Offer):
            self.fill_offer_attributes(pc_object)

    def fill_product_attributes(self, allocine_product: Product):
        allocine_product.thumbCount = 0
        allocine_product.description = self.movie_information['description']
        allocine_product.durationMinutes = self.movie_information['duration']
        if not allocine_product.extraData:
            allocine_product.extraData = {}
        if 'visa' in self.movie_information:
            allocine_product.extraData["visa"] = self.movie_information['visa']
        if 'stageDirector' in self.movie_information:
            allocine_product.extraData["stageDirector"] = self.movie_information['stageDirector']
        allocine_product.name = self.movie_information['title']

        allocine_product.type = str(EventType.CINEMA)
        is_new_product_to_insert = allocine_product.id is None

        if is_new_product_to_insert:
            allocine_product.id = self.get_next_product_id_from_database()
        self.last_product_id = allocine_product.id

    def fill_offer_attributes(self, allocine_offer: Offer):
        allocine_offer.venueId = self.venue.id
        allocine_offer.bookingEmail = self.venue.bookingEmail
        allocine_offer.description = self.movie_information['description']
        allocine_offer.durationMinutes = self.movie_information['duration']
        if not allocine_offer.extraData:
            allocine_offer.extraData = {}
        if 'visa' in self.movie_information:
            allocine_offer.extraData["visa"] = self.movie_information['visa']
        if 'stageDirector' in self.movie_information:
            allocine_offer.extraData["stageDirector"] = self.movie_information['stageDirector']
        allocine_offer.isDuo = True

        movie_version = ORIGINAL_VERSION_SUFFIX if _is_original_version_offer(allocine_offer.idAtProviders) is True else FRENCH_VERSION_SUFFIX

        allocine_offer.name = f"{self.movie_information['title']} - {movie_version}"
        allocine_offer.type = str(EventType.CINEMA)
        allocine_offer.productId = self.last_product_id

    def get_next_product_id_from_database(self):
        sequence = Sequence('product_id_seq')
        return db.session.execute(sequence)

    def get_object_thumb(self) -> bytes:
        image_url = self.movie_information['poster_url']
        return get_movie_poster(image_url)

    def get_object_thumb_index(self) -> int:
        return 1


def retrieve_movie_information(raw_movie_information: dict) -> dict:
    parsed_movie_information = dict()
    parsed_movie_information['id'] = raw_movie_information['id']
    parsed_movie_information['description'] = _build_description(raw_movie_information)
    parsed_movie_information['duration'] = _parse_movie_duration(raw_movie_information['runtime'])
    parsed_movie_information['title'] = raw_movie_information['title']
    parsed_movie_information['poster_url'] = _format_poster_url(raw_movie_information['poster']['url'])
    is_stage_director_info_available = len(raw_movie_information['credits']['edges']) > 0

    if is_stage_director_info_available:
        parsed_movie_information['stageDirector'] = _build_stage_director_full_name(raw_movie_information)

    is_operating_visa_available = len(raw_movie_information['releases']) > 0 \
                                  and len(raw_movie_information['releases'][0]['data']) > 0

    if is_operating_visa_available:
        parsed_movie_information['visa'] = _get_operating_visa(raw_movie_information)

    return parsed_movie_information


def _build_description(movie_info: dict) -> str:
    allocine_movie_url = movie_info['backlink']['url'].replace("\\", "")
    return f"{movie_info['synopsis']}\n{movie_info['backlink']['label']}: {allocine_movie_url}"


def _format_poster_url(url: str) -> str:
    return url.replace("\/", "/")


def _get_operating_visa(movie_info: dict) -> Optional[str]:
    return movie_info['releases'][0]['data']['visa_number']


def _build_stage_director_full_name(movie_info: dict) -> str:
    stage_director_first_name = movie_info['credits']['edges'][0]['node']['person']['firstName']
    stage_director_last_name = movie_info['credits']['edges'][0]['node']['person']['lastName']
    return f"{stage_director_first_name} {stage_director_last_name}"


def _parse_movie_duration(duration: str) -> Optional[int]:
    if not duration:
        return None
    hours_minutes = "([0-9]+)H([0-9]+)"
    duration_regex = re.compile(hours_minutes)
    match = duration_regex.search(duration)
    movie_duration_hours = int(match.groups()[0])
    movie_duration_minutes = int(match.groups()[1])
    return movie_duration_hours * 60 + movie_duration_minutes

def _has_original_version_product(movies_showtimes: List[dict]) -> bool:
    return ORIGINAL_VERSION in list(map(lambda movie: movie['diffusionVersion'], movies_showtimes))

def _has_french_version_product(movies_showtimes: List[dict]) -> bool:
    return LOCAL_VERSION or DUBBED_VERSION in list(map(lambda movie: movie['diffusionVersion'], movies_showtimes))

def _is_original_version_offer(idAtProviders: str) -> bool:
    return idAtProviders[-3:] == f"-{ORIGINAL_VERSION_SUFFIX}"

