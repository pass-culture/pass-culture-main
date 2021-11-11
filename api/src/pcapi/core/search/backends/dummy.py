from flask import current_app

from .algolia import AlgoliaBackend


class FakeClient:
    def save_objects(self, objects):
        pass

    def delete_objects(self, object_ids):
        pass

    def clear_objects(self):
        pass


class DummyBackend(AlgoliaBackend):
    """A backend that does not communicate with the external search
    service.

    We subclass a real-looking backend to be as close as possible to
    what we have in production. Only the communication with the
    external search service is faked.

    Note that we still use Redis for the queue. We could implement all
    Redis-related functions as no-op, but it's not worth.
    """

    def __init__(self):  # pylint: disable=super-init-not-called
        self.algolia_offers_client = FakeClient()
        self.algolia_venues_client = FakeClient()
        self.redis_client = current_app.redis_client
