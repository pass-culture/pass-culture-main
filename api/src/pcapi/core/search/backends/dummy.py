import logging
import typing
from collections import abc

from algoliasearch.search.models import search_response

from .algolia import AlgoliaBackend


logger = logging.getLogger(__name__)


class DummyBackend(AlgoliaBackend):
    """A backend that does not communicate with the external search
    service.
    """

    @typing.override
    def save_objects(self, index: str | None, serialized_object: list[dict]) -> None:
        logger.info(
            "Dummy save_objects",
            extra={"index": index, "object_ids": [o["objectID"] for o in serialized_object]},
        )

    @typing.override
    def delete_objects(self, index: str | None, object_ids: abc.Collection[typing.Union[str, int]]) -> None:
        logger.info("Dummy delete_objects", extra={"index": index, "object_ids": object_ids})

    @typing.override
    def clear_objects(self, index: str | None) -> None:
        logger.info("Dummy clear_objects", extra={"index": index})

    @typing.override
    def set_settings(self, index: str | None, algolia_settings: dict) -> None:
        logger.info("Dummy set_settings", extra={"index": index})

    @typing.override
    def get_settings(self, index: str | None) -> dict:
        logger.info("Dummy get_settings", extra={"index": index})

        return {}

    @typing.override
    def search(
        self,
        index: str | None,
        query: str,
        params: dict[str, typing.Any],
    ) -> search_response.SearchResponse:
        logger.info("Dummy search", extra={"index": index, "query": query, "params": params})

        return search_response.SearchResponse(
            hits=[],
            processing_time_ms=10,
            query="query",
            params="?p=params",
        )
