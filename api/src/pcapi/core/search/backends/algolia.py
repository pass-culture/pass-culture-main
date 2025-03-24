from collections import abc
import logging
import typing

import algoliasearch.search.client as search_client
from algoliasearch.search.models.batch_response import BatchResponse
from algoliasearch.search.models.index_settings import IndexSettings
from algoliasearch.search.models.search_response import SearchResponse
from algoliasearch.search.models.updated_at_response import UpdatedAtResponse

from pcapi import settings
import pcapi.core.educational.models as educational_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
from pcapi.core.search import SearchError
from pcapi.core.search.backends import base
from pcapi.utils import human_ids

from . import redis_queues
from . import serialization


logger = logging.getLogger(__name__)

MAX_SEARCH_QUERY_COUNT = 1000


class AlgoliaBackend(
    serialization.AlgoliaSerializationMixin, redis_queues.AlgoliaIndexingQueuesMixin, base.SearchBackend
):
    def save_objects(self, index: str | None, serialized_object: list[dict]) -> typing.List[BatchResponse]:
        assert index
        with search_client.SearchClientSync(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_API_KEY) as client:
            return client.save_objects(index, serialized_object)

    def delete_objects(self, index: str | None, object_ids: abc.Collection[str]) -> list[BatchResponse]:
        assert index
        with search_client.SearchClientSync(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_API_KEY) as client:
            return client.delete_objects(index, list(object_ids))

    def clear_objects(self, index: str | None) -> UpdatedAtResponse:
        assert index
        with search_client.SearchClientSync(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_API_KEY) as client:
            return client.clear_objects(index)

    def set_settings(self, index: str | None, algolia_settings: dict) -> None:
        assert index
        with search_client.SearchClientSync(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_API_KEY) as client:
            client.set_settings(index, IndexSettings.from_dict(algolia_settings) or {})

    def get_settings(self, index: str | None) -> dict:
        assert index
        with search_client.SearchClientSync(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_API_KEY) as client:
            return client.get_settings(index).to_dict()

    def search(
        self,
        index: str | None,
        query: str,
        params: dict[str, typing.Any],
    ) -> SearchResponse:
        assert index
        with search_client.SearchClientSync(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_API_KEY) as client:
            return client.search_single_index(index, {"query": query}.update(**params))

    def index_offers(self, offers: abc.Collection[offers_models.Offer], last_30_days_bookings: dict[int, int]) -> None:
        # Warning: if you ever need to alter the DB, please make sure you take into account that
        # the calling function index_offers_in_queue does a rollback to remove any reading lock
        # during processing.
        if not offers:
            return
        objects = [self.serialize_offer(offer, last_30_days_bookings.get(offer.id) or 0) for offer in offers]

        self.save_objects(settings.ALGOLIA_OFFERS_INDEX_NAME, objects)

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
        self.save_objects(settings.ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME, objects)

    def index_venues(self, venues: abc.Collection[offerers_models.Venue]) -> None:
        if not venues:
            return
        objects = [self.serialize_venue(venue) for venue in venues]
        self.save_objects(settings.ALGOLIA_VENUES_INDEX_NAME, objects)

    def unindex_offer_ids(self, offer_ids: abc.Collection[int]) -> None:
        if not offer_ids:
            return
        self.delete_objects(settings.ALGOLIA_OFFERS_INDEX_NAME, [str(offer_id) for offer_id in offer_ids])
        self.remove_offer_ids_from_store(offer_ids)

    def unindex_all_offers(self) -> None:
        self.clear_objects(settings.ALGOLIA_OFFERS_INDEX_NAME)
        self.remove_all_offers_from_store()

    def unindex_venue_ids(self, venue_ids: abc.Collection[int]) -> None:
        if not venue_ids:
            return
        self.delete_objects(settings.ALGOLIA_VENUES_INDEX_NAME, [str(venue_id) for venue_id in venue_ids])

    def unindex_collective_offer_template_ids(self, collective_offer_template_ids: abc.Collection[int]) -> None:
        if not collective_offer_template_ids:
            return
        self.delete_objects(
            settings.ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME,
            [
                serialization._transform_collective_offer_template_id(collective_offer_template_id)
                for collective_offer_template_id in collective_offer_template_ids
            ],
        )

    def unindex_all_venues(self) -> None:
        self.clear_objects(settings.ALGOLIA_VENUES_INDEX_NAME)

    def unindex_all_collective_offer_templates(self) -> None:
        self.clear_objects(settings.ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME)

    def search_offer_ids(self, query: str = "", count: int = 20, **params: typing.Any) -> list[int]:
        ids: list[int] = []
        for page, _count in enumerate(range(0, count, MAX_SEARCH_QUERY_COUNT)):
            # handle algolia pagination of results
            hits_per_page = min(count, count - _count, MAX_SEARCH_QUERY_COUNT)
            params["page"] = page
            params["hitsPerPage"] = hits_per_page
            try:
                results = self.search(settings.ALGOLIA_OFFERS_INDEX_NAME, query, params)
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

            for hit in results.hits:
                object_id = hit.object_id
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

            if len(results.hits) < hits_per_page:
                break
        return ids
