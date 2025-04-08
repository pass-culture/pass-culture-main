import typing

from pcapi import settings
from pcapi.core.search import testing

from .algolia import AlgoliaBackend


class FakeClient:
    def __init__(self, key: str) -> None:
        self.key = key

    def save_objects(self, objects: typing.Iterable[dict]) -> None:
        for obj in objects:
            testing.search_store[self.key][obj["objectID"]] = obj

    def delete_objects(self, object_ids: typing.Iterable[int]) -> None:
        for object_id in object_ids:
            testing.search_store[self.key].pop(object_id, None)

    def clear_objects(self) -> None:
        testing.search_store[self.key] = {}

    def search(self, query: str, params: dict) -> dict:
        if query == "ok":
            start = params.get("page", 0) * 1000
            count = params.get("hitsPerPage", 20)
            return {"hits": [{"objectID": i} for i in range(start, start + count)]}
        return {"hits": []}


class TestingBackend(AlgoliaBackend):
    """A backend to be used by automated tests.

    We subclass a real-looking backend to be as close as possible to
    what we have in production. Only the communication with the
    external search service is faked.
    """

    def create_algolia_clients(self) -> None:
        assert settings.ALGOLIA_OFFERS_INDEX_NAME  # helps mypy
        assert settings.ALGOLIA_VENUES_INDEX_NAME  # helps mypy
        assert settings.ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME  # helps mypy
        self.index_mapping = {
            settings.ALGOLIA_OFFERS_INDEX_NAME: FakeClient("offers"),
            settings.ALGOLIA_VENUES_INDEX_NAME: FakeClient("venues"),
            settings.ALGOLIA_COLLECTIVE_OFFER_TEMPLATES_INDEX_NAME: FakeClient("collective-offers-templates"),
        }
