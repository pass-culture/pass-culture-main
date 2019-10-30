import os
import re
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Sequence

from domain.allocine import get_movie_showtime_list_from_allocine
from local_providers.local_provider import LocalProvider
from local_providers.providable_info import ProvidableInfo
from models import VenueProvider, Offer, Product, EventType
from models.db import Model, db


class AllocineStocks(LocalProvider):
    name = "Allociné"
    can_create = True

    def __init__(self, venue_provider: VenueProvider, **options):
        super().__init__(venue_provider, **options)
        self.token = os.environ.get('ALLOCINE_TOKEN', None)
        self.venue = venue_provider.venue
        self.theater_id = venue_provider.venueIdAtOfferProvider
        self.movie_showtime_list = iter(get_movie_showtime_list_from_allocine(self.token, self.theater_id))
        self.last_product_id = None
        self.movie_info = None

    def __next__(self) -> List[ProvidableInfo]:
        movie_json_info = next(self.movie_showtime_list)
        self.movie_info = retrieve_movie_information(movie_json_info)

        offer_providable_info = self.create_providable_info(Offer)
        product_providable_info = self.create_providable_info(Product)

        return [product_providable_info, offer_providable_info]

    def fill_object_attributes(self, allocine_pc_object: Model):
        if isinstance(allocine_pc_object, Product):
            self.fill_product_attributes(allocine_pc_object)

        if isinstance(allocine_pc_object, Offer):
            self.fill_offer_attributes(allocine_pc_object)

    def fill_product_attributes(self, allocine_product: Product):
        allocine_product.description = self.movie_info['description']
        allocine_product.durationMinutes = self.movie_info['duration']
        if not allocine_product.extraData:
            allocine_product.extraData = {}
        allocine_product.extraData["visa"] = self.movie_info['visa']
        allocine_product.extraData["stageDirector"] = self.movie_info['stageDirector']
        allocine_product.name = self.movie_info['title']
        allocine_product.type = str(EventType.CINEMA)
        new_product_to_insert = allocine_product.id is None

        if new_product_to_insert:
            self.last_product_id = self.get_next_product_id_from_sequence()
            allocine_product.id = self.last_product_id
        else:
            self.last_product_id = allocine_product.id

    def fill_offer_attributes(self, allocine_offer: Offer):
        allocine_offer.venueId = self.venue.id
        allocine_offer.bookingEmail = self.venue.bookingEmail
        allocine_offer.description = self.movie_info['description']
        allocine_offer.durationMinutes = self.movie_info['duration']
        if not allocine_offer.extraData:
            allocine_offer.extraData = {}
        if 'visa' in self.movie_info:
            allocine_offer.extraData["visa"] = self.movie_info['visa']
        if 'stageDirector' in self.movie_info:
            allocine_offer.extraData["stageDirector"] = self.movie_info['stageDirector']
        allocine_offer.isDuo = True
        allocine_offer.name = self.movie_info['title']
        allocine_offer.type = str(EventType.CINEMA)
        allocine_offer.productId = self.last_product_id

    def get_next_product_id_from_sequence(self):
        sequence = Sequence('product_id_seq')
        return db.session.execute(sequence)

    def create_providable_info(self, object_type: Model) -> ProvidableInfo:
        providable_info = ProvidableInfo()
        providable_info.id_at_providers = self.movie_info['id']
        providable_info.type = object_type
        providable_info.date_modified_at_provider = datetime.utcnow()
        return providable_info


def retrieve_movie_information(movie_json_information: dict) -> dict:
    movie_parsed_information = {}
    movie_information = movie_json_information['node']['movie']
    movie_parsed_information['id'] = movie_information['id']
    movie_parsed_information['description'] = _build_description_information(movie_information)
    movie_parsed_information['duration'] = _parse_movie_duration(movie_information['runtime'])
    movie_parsed_information['title'] = movie_information['title']

    stage_director_info_available = len(movie_information['credits']['edges']) > 0

    if stage_director_info_available:
        movie_parsed_information['stageDirector'] = _build_stage_director_information(movie_information)

    visa_number_available = len(movie_information['releases']) > 0

    if visa_number_available:
        movie_parsed_information['visa'] = _build_visa_information(movie_information)

    return movie_parsed_information


def _build_description_information(movie_info: dict) -> str:
    return "%s\n%s" % (movie_info['synopsis'],
                       movie_info['backlink']['url'])


def _build_visa_information(movie_info: dict) -> Optional[str]:
    return movie_info['releases'][0]['data']['visa_number']


def _build_stage_director_information(movie_info: dict) -> Optional[str]:
    return "%s %s" % (
        movie_info['credits']['edges'][0]['node']['person']['firstName'],
        movie_info['credits']['edges'][0]['node']['person']['lastName'])


def _parse_movie_duration(duration: str) -> int:
    duration_regex = re.compile("([0-9]+)(H)([0-9]+)")
    match = duration_regex.search(duration)
    return int(match.groups()[0]) * 60 + int(match.groups()[2])
