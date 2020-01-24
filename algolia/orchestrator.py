import os
from typing import List, Dict

from algolia.api import add_objects, clear_objects, delete_objects
from algolia.builder import build_object
from algolia.rules_engine import is_eligible_for_indexing
from repository import offer_queries
from utils.converter import from_tuple_to_int
from utils.human_ids import humanize

ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE = int(os.environ.get('ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE', 10000))


def orchestrate(offer_ids: List[int], is_clear: bool = False) -> None:
    if is_clear:
        clear_objects()

    indexing_objects = []
    deleting_objects = []
    offers = offer_queries.get_offers_by_ids(offer_ids)

    for offer in offers:
        if is_eligible_for_indexing(offer):
            indexing_objects.append(build_object(offer=offer))
        else:
            deleting_objects.append(humanize(offer.id))

    if len(indexing_objects) > 0:
        add_objects(objects=indexing_objects)

    if len(deleting_objects) > 0:
        delete_objects(object_ids=deleting_objects)


def orchestrate_from_venue_providers(venue_providers: List[Dict]) -> None:
    for venue_provider in venue_providers:
        has_still_offers = True
        page = 0
        while has_still_offers is True:
            last_provider_id = venue_provider['lastProviderId']
            venue_id = int(venue_provider['venueId'])
            offer_ids_as_tuple = offer_queries.get_paginated_offer_ids_by_venue_id_and_last_provider_id(
                last_provider_id=last_provider_id,
                limit=ALGOLIA_OFFERS_BY_VENUE_PROVIDER_CHUNK_SIZE,
                page=page,
                venue_id=venue_id
            )
            offer_ids_as_int = from_tuple_to_int(offer_ids_as_tuple)

            if len(offer_ids_as_tuple) > 0:
                orchestrate(offer_ids=offer_ids_as_int)
                page += 1
            else:
                has_still_offers = False
