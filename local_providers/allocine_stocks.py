import os
import re
from datetime import datetime, timedelta
from typing import List, Optional

from dateutil.parser import parse
from sqlalchemy import Sequence

from domain.allocine import get_movies_showtimes, get_movie_poster
from local_providers.local_provider import LocalProvider
from local_providers.providable_info import ProvidableInfo
from models import VenueProvider, Offer, Product, EventType, Stock
from models.db import Model, db
from models.local_provider_event import LocalProviderEventType

DIGITAL_PROJECTION = 'DIGITAL'
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
        self.movie_information = None
        self.filtered_movie_showtimes = None
        self.last_product_id = None
        self.last_vf_offer_id = None
        self.last_vo_offer_id = None

    def __next__(self) -> List[ProvidableInfo]:
        raw_movie_information = next(self.movies_showtimes)
        try:
            self.movie_information = retrieve_movie_information(raw_movie_information['node']['movie'])
            self.filtered_movie_showtimes = _filter_only_digital_and_non_experience_showtimes(raw_movie_information
                                                                                              ['node']['showtimes'])
            showtimes_number = len(self.filtered_movie_showtimes)

        except KeyError:
            self.log_provider_event(LocalProviderEventType.SyncError,
                                    f"Error parsing information for movie: {raw_movie_information['node']['movie']}")
            return []

        providable_information_list = [self.create_providable_info(Product,
                                                                   self.movie_information['id'],
                                                                   datetime.utcnow())]

        if _has_original_version_product(self.filtered_movie_showtimes):
            original_version_offer_providable_information = self.create_providable_info(Offer,
                                                                                        f"{self.movie_information['id']}"
                                                                                        f"-{ORIGINAL_VERSION_SUFFIX}",
                                                                                        datetime.utcnow())

            providable_information_list.append(original_version_offer_providable_information)

        if _has_french_version_product(self.filtered_movie_showtimes):
            french_version_offer_providable_information = self.create_providable_info(Offer,
                                                                                      f"{self.movie_information['id']}-"
                                                                                      f"{FRENCH_VERSION_SUFFIX}",
                                                                                      datetime.utcnow())
            providable_information_list.append(french_version_offer_providable_information)

        stock_providable_information = [self.create_providable_info(Stock, f"{self.movie_information['id']}-"
                                f"{showtime_number}", datetime.utcnow()) for showtime_number in range(showtimes_number)]

        providable_information_list += stock_providable_information

        return providable_information_list

    def fill_object_attributes(self, pc_object: Model):
        if isinstance(pc_object, Product):
            self.fill_product_attributes(pc_object)

        if isinstance(pc_object, Offer):
            self.fill_offer_attributes(pc_object)

        if isinstance(pc_object, Stock):
            self.fill_stock_attributes(pc_object)

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
            allocine_product.id = get_next_product_id_from_database()
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

        movie_version = ORIGINAL_VERSION_SUFFIX if _is_original_version_offer(allocine_offer.idAtProviders) \
            else FRENCH_VERSION_SUFFIX

        allocine_offer.name = f"{self.movie_information['title']} - {movie_version}"
        allocine_offer.type = str(EventType.CINEMA)
        allocine_offer.productId = self.last_product_id

        is_new_offer_to_insert = allocine_offer.id is None

        if is_new_offer_to_insert:
            allocine_offer.id = get_next_offer_id_from_database()

        if movie_version == ORIGINAL_VERSION_SUFFIX:
            self.last_vo_offer_id = allocine_offer.id
        else:
            self.last_vf_offer_id = allocine_offer.id

    def fill_stock_attributes(self, allocine_stock: Stock):
        stock_number = _get_stock_number_from_stock_id(allocine_stock.idAtProviders)

        try:
            parsed_showtimes = retrieve_showtime_information(self.filtered_movie_showtimes[stock_number])

        except KeyError:
            self.log_provider_event(LocalProviderEventType.SyncError,
                                f"Error parsing information for movie: {self.filtered_movie_showtimes[stock_number]}")
            return []

        diffusion_version = parsed_showtimes['diffusionVersion']

        allocine_stock.offerId = self.last_vo_offer_id if diffusion_version == ORIGINAL_VERSION else \
            self.last_vf_offer_id

        allocine_stock.beginningDatetime = parsed_showtimes['startsAt']
        allocine_stock.bookingLimitDatetime = parsed_showtimes['startsAt']
        allocine_stock.available = None
        allocine_stock.price = 0

        movie_duration = self.movie_information['duration']
        if movie_duration is not None:
            allocine_stock.endDatetime = allocine_stock.beginningDatetime + timedelta(minutes=movie_duration)

    def get_object_thumb(self) -> bytes:
        image_url = self.movie_information['poster_url']
        return get_movie_poster(image_url)

    def get_object_thumb_index(self) -> int:
        return 1


def get_next_product_id_from_database():
    sequence = Sequence('product_id_seq')
    return db.session.execute(sequence)


def get_next_offer_id_from_database():
    sequence = Sequence('offer_id_seq')
    return db.session.execute(sequence)


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


def retrieve_showtime_information(showtime_information: dict) -> dict:
    parsed_showtime_information = dict()
    parsed_showtime_information['startsAt'] = parse(showtime_information['startsAt'])
    parsed_showtime_information['diffusionVersion'] = showtime_information['diffusionVersion']
    parsed_showtime_information['projection'] = showtime_information['projection'][0]
    parsed_showtime_information['experience'] = showtime_information['experience']

    return parsed_showtime_information


def _filter_only_digital_and_non_experience_showtimes(showtimes_information: List[dict]) -> List[dict]:
    filtered_movie_information = list(filter(lambda showtime: showtime['projection'][0] == DIGITAL_PROJECTION and
                                                              showtime['experience'] is None, showtimes_information))
    return filtered_movie_information


def _get_stock_number_from_stock_id(id_at_providers: str) -> int:
    return int(id_at_providers.split("-", 1)[1])


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
    movies = list(map(lambda movie: movie['diffusionVersion'], movies_showtimes))
    return LOCAL_VERSION in movies or DUBBED_VERSION in movies


def _is_original_version_offer(id_at_providers: str) -> bool:
    return id_at_providers[-3:] == f"-{ORIGINAL_VERSION_SUFFIX}"
