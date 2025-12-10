import typing
from collections import abc

from algoliasearch.search.models import search_response

from pcapi.core.search import testing

from .algolia import AlgoliaBackend


class TestingBackend(AlgoliaBackend):
    """A backend to be used by automated tests.

    We subclass a real-looking backend to be as close as possible to
    what we have in production. Only the communication with the
    external search service is faked.
    """

    search_store = testing.search_store

    def save_objects(self, index: str | None, serialized_object: list[dict]) -> None:
        assert index
        for obj in serialized_object:
            testing.search_store[index][obj["objectID"]] = obj

    def delete_objects(self, index: str | None, object_ids: abc.Collection[typing.Union[str, int]]) -> None:
        assert index
        for object_id in object_ids:
            testing.search_store[index].pop(object_id, None)

    def clear_objects(self, index: str | None) -> None:
        assert index
        testing.search_store[index] = {}

    def set_settings(self, index: str | None, algolia_settings: dict) -> None:
        assert index
        raise NotImplementedError()

    def get_settings(self, index: str | None) -> dict:
        assert index
        raise NotImplementedError()

    def search(
        self,
        index: str | None,
        query: str,
        params: dict[str, typing.Any],
    ) -> search_response.SearchResponse:
        assert index
        if query == "ok":
            start = params.get("page", 0) * 1000
            count = params.get("hitsPerPage", 20)
            return search_response.SearchResponse(
                hits=[{"objectID": i} for i in range(start, start + count)],
                processing_time_ms=10,
                query="query",
                params="?p=params",
            )
        return search_response.SearchResponse(
            hits=[],
            processing_time_ms=10,
            query="query",
            params="?p=params",
        )
