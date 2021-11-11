from flask import current_app

from pcapi.core.search import testing

from .appsearch import AppSearchBackend


class FakeClient:
    def __init__(self, key):
        self.key = key

    def create_or_update_documents(self, documents):
        for document in documents:
            testing.search_store[self.key][document["id"]] = document

    def delete_documents(self, document_ids):
        for document_id in document_ids:
            testing.search_store[self.key].pop(document_id, None)

    def delete_all_documents(self):
        testing.search_store[self.key] = {}


class TestingBackend(AppSearchBackend):
    """A backend to be used by automated tests.

    We subclass a real-looking backend to be as close as possible to
    what we have in production. Only the communication with the
    external search service is faked.
    """

    def __init__(self):  # pylint: disable=super-init-not-called
        self.offers_engine = FakeClient("offers")
        self.venues_engine = FakeClient("venues")
        self.educational_offers_engine = FakeClient("educational-offers")
        self.redis_client = current_app.redis_client
