import logging
import typing

from flask import current_app

from .algolia import AlgoliaBackend


logger = logging.getLogger(__name__)


class FakeClient:
    def save_objects(self, objects: typing.Iterable[dict]) -> None:
        logger.info(
            "Dummy indexation of objects",
            extra={"object_ids": [o["objectID"] for o in objects]},
        )

    def delete_objects(self, object_ids: typing.Iterable[int]) -> None:
        logger.info("Dummy deletion of objects", extra={"object_ids": object_ids})

    def clear_objects(self) -> None:
        logger.info("Dummy clear of all objects")


class DummyBackend(AlgoliaBackend):
    """A backend that does not communicate with the external search
    service.

    We subclass a real-looking backend to be as close as possible to
    what we have in production. Only the communication with the
    external search service is faked.

    Note that we still use Redis for the queue. We could implement all
    Redis-related functions as no-op, but it's not worth.
    """

    def __init__(self) -> None:  # pylint: disable=super-init-not-called
        self.algolia_offers_client = FakeClient()
        self.algolia_venues_client = FakeClient()
        self.algolia_collective_offers_client = FakeClient()
        self.algolia_collective_offers_templates_client = FakeClient()
        self.redis_client = current_app.redis_client  # type: ignore[attr-defined]
