import logging
import typing
from collections import abc

import algoliasearch.http.requester
import algoliasearch.search_client

import pcapi.core.artist.models as artists_models
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi import settings
from pcapi.core.search import SearchError
from pcapi.core.search.backends import base
from pcapi.utils import human_ids
from pcapi.utils import requests

from . import redis_queues
from . import serialization


logger = logging.getLogger(__name__)

MAX_SEARCH_QUERY_COUNT = 1000


def create_algolia_client() -> algoliasearch.search_client.SearchClient:
    config = algoliasearch.search_client.SearchConfig(
        app_id=settings.ALGOLIA_APPLICATION_ID,
        api_key=settings.ALGOLIA_API_KEY,
    )
    requester = algoliasearch.http.requester.Requester()
    requester._session = requests.Session()  # inject our own session handler that logs
    transporter = algoliasearch.search_client.Transporter(requester, config)
    return algoliasearch.search_client.SearchClient(transporter, config)


class AlgoliaBackend(
    serialization.AlgoliaSerializationMixin, redis_queues.AlgoliaIndexingQueuesMixin, base.SearchBackend
):
    def __init__(self) -> None:
        super().__init__()
        client = create_algolia_client()
        self.algolia_artists_client = client.init_index(settings.ALGOLIA_ARTISTS_INDEX_NAME)
        self.algolia_offers_client = client.init_index(settings.ALGOLIA_OFFERS_INDEX_NAME)
        self.algolia_collective_offers_templates_client = client.init_index(
            settings.ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME
        )
        self.algolia_venues_client = client.init_index(settings.ALGOLIA_VENUES_INDEX_NAME)

    def index_artists(self, artists: artists_models.Artist) -> None:
        self.algolia_artists_client.save_objects([self.serialize_artist(artist) for artist in artists])

    def index_offers(self, offers: abc.Collection[offers_models.Offer], last_30_days_bookings: dict[int, int]) -> None:
        # Warning: if you ever need to alter the DB, please make sure you take into account that
        # the calling function index_offers_in_queue does a rollback to remove any reading lock
        # during processing.
        if not offers:
            return
        objects = [self.serialize_offer(offer, last_30_days_bookings.get(offer.id) or 0) for offer in offers]
        self.algolia_offers_client.save_objects(objects)

        offer_ids = [offer.id for offer in offers]
        self.add_offer_ids_to_store(offer_ids)

    def index_collective_offer_templates(
        self,
        collective_offer_templates: abc.Collection[educational_models.CollectiveOfferTemplate],
    ) -> None:
        if not collective_offer_templates:
            return
        objects = [
            self.serialize_collective_offer_template(collective_offer_template)
            for collective_offer_template in collective_offer_templates
        ]
        self.algolia_collective_offers_templates_client.save_objects(objects)

    def index_venues(self, venues: abc.Collection[offerers_models.Venue]) -> None:
        if not venues:
            return
        objects = [self.serialize_venue(venue) for venue in venues]
        self.algolia_venues_client.save_objects(objects)

    def unindex_offer_ids(self, offer_ids: abc.Collection[int]) -> None:
        if not offer_ids:
            return
        self.algolia_offers_client.delete_objects(offer_ids)
        self.remove_offer_ids_from_store(offer_ids)

    def unindex_all_offers(self) -> None:
        self.algolia_offers_client.clear_objects()
        self.remove_all_offers_from_store()

    def unindex_venue_ids(self, venue_ids: abc.Collection[int]) -> None:
        if not venue_ids:
            return
        self.algolia_venues_client.delete_objects(venue_ids)

    def unindex_collective_offer_template_ids(self, collective_offer_template_ids: abc.Collection[int]) -> None:
        if not collective_offer_template_ids:
            return
        self.algolia_collective_offers_templates_client.delete_objects(
            [
                serialization._transform_collective_offer_template_id(collective_offer_template_id)
                for collective_offer_template_id in collective_offer_template_ids
            ]
        )

    def unindex_all_venues(self) -> None:
        self.algolia_venues_client.clear_objects()

    def unindex_all_collective_offer_templates(self) -> None:
        self.algolia_collective_offers_templates_client.clear_objects()

    def search_offer_ids(self, query: str = "", count: int = 20, **params: typing.Any) -> list[int]:
        ids: list[int] = []
        for page, _count in enumerate(range(0, count, MAX_SEARCH_QUERY_COUNT)):
            # handle algolia pagination of results
            hits_per_page = min(count, count - _count, MAX_SEARCH_QUERY_COUNT)
            params["page"] = page
            params["hitsPerPage"] = hits_per_page
            try:
                results = self.algolia_offers_client.search(query, params)
            except Exception as exp:
                logger.exception(
                    "Failed to search in algolia: %s",
                    exp,
                    extra={
                        "query": query,
                        "params": params,
                    },
                )
                raise SearchError("Failed to search in algolia")

            for result in results.get("hits", []):
                object_id = result["objectID"]
                if object_id.isdigit():
                    ids.append(int(object_id))
                else:
                    # Some object id are still humanized.
                    try:
                        dehumanized_id = human_ids.dehumanize(object_id)
                        assert dehumanized_id is not None  # helps mypy
                        ids.append(dehumanized_id)
                    except human_ids.NonDehumanizableId:
                        pass

            if len(results.get("hits", [])) < hits_per_page:
                break
        return ids
