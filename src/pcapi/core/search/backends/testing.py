from flask import current_app

from pcapi.core.search import testing

from .algolia import AlgoliaBackend


class FakeClient:
    def save_objects(self, objects):
        for obj in objects:
            testing.search_store[obj["objectID"]] = obj

    def delete_objects(self, object_ids):
        for object_id in object_ids:
            testing.search_store.pop(object_id, None)

    def clear_objects(self):
        testing.search_store = {}


class TestingBackend(AlgoliaBackend):
    """A backend to be used by automated tests.

    We subclass a real-looking backend to be as close as possible to
    what we have in production. Only the communication with the
    external search service is faked.
    """

    def __init__(self):  # pylint: disable=super-init-not-called
        self.algolia_client = FakeClient()
        self.redis_client = current_app.redis_client
