from flask import current_app

from pcapi.core.search import testing

from .algolia import AlgoliaBackend


class FakeClient:
    def __init__(self, key):
        self.key = key

    def save_objects(self, objects):
        for obj in objects:
            testing.search_store[self.key][obj["objectID"]] = obj

    def delete_objects(self, object_ids):
        for object_id in object_ids:
            testing.search_store[self.key].pop(object_id, None)

    def clear_objects(self):
        testing.search_store[self.key] = {}


class TestingBackend(AlgoliaBackend):
    """A backend to be used by automated tests.

    We subclass a real-looking backend to be as close as possible to
    what we have in production. Only the communication with the
    external search service is faked.
    """

    def __init__(self):  # pylint: disable=super-init-not-called
        self.algolia_offers_client = FakeClient("offers")
        self.algolia_venues_client = FakeClient("venues")
        self.algolia_collective_offers_client = FakeClient("testing-collective-offers")
        self.algolia_collective_offers_templates_client = FakeClient("testing-collective-offers-templates")
        self.redis_client = current_app.redis_client
