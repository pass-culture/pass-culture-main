from collections import abc
import contextlib
import typing


if typing.TYPE_CHECKING:
    import pcapi.core.educational.models as educational_models
    import pcapi.core.offerers.models as offerers_models
    import pcapi.core.offers.models as offers_models


class SearchBackend:
    def __str__(self) -> str:  # useful in logs
        return str(self.__class__.__name__)

    def enqueue_offer_ids(self, offer_ids: abc.Collection[int]) -> None:
        raise NotImplementedError()

    def enqueue_collective_offer_template_ids(self, collective_offer_template_ids: abc.Collection[int]) -> None:
        raise NotImplementedError()

    def enqueue_offer_ids_in_error(self, offer_ids: abc.Collection[int]) -> None:
        raise NotImplementedError()

    def enqueue_venue_ids_in_error(self, venue_ids: abc.Collection[int]) -> None:
        raise NotImplementedError()

    def enqueue_collective_offer_template_ids_in_error(
        self, collective_offer_template_ids: abc.Collection[int]
    ) -> None:
        raise NotImplementedError()

    def enqueue_venue_ids(self, venue_ids: abc.Collection[int]) -> None:
        raise NotImplementedError()

    def enqueue_venue_ids_for_offers(self, venue_ids: abc.Collection[int]) -> None:
        raise NotImplementedError()

    def pop_offer_ids_from_queue(self, count: int, from_error_queue: bool = False) -> contextlib.AbstractContextManager:
        raise NotImplementedError()

    def pop_venue_ids_for_offers_from_queue(self, count: int) -> contextlib.AbstractContextManager:
        raise NotImplementedError()

    def count_offers_to_index_from_queue(self, from_error_queue: bool = False) -> int:
        raise NotImplementedError()

    def check_offer_is_indexed(self, offer: "offers_models.Offer") -> bool:
        raise NotImplementedError()

    def index_offers(
        self, offers: "abc.Collection[offers_models.Offer]", last_30_days_bookings: dict[int, int]
    ) -> None:
        raise NotImplementedError()

    def index_collective_offer_templates(
        self, collective_offer_templates: "abc.Collection[educational_models.CollectiveOfferTemplate]"
    ) -> None:
        raise NotImplementedError()

    def index_venues(self, venues: "abc.Collection[offerers_models.Venue]") -> None:
        raise NotImplementedError()

    def unindex_offer_ids(self, offer_ids: abc.Collection[int]) -> None:
        raise NotImplementedError()

    def unindex_all_offers(self) -> None:
        raise NotImplementedError()

    def unindex_venue_ids(self, venue_ids: abc.Collection[int]) -> None:
        raise NotImplementedError()

    def unindex_all_collective_offer_templates(self) -> None:
        raise NotImplementedError()

    def unindex_collective_offer_template_ids(self, collective_offer_template_ids: abc.Collection[int]) -> None:
        raise NotImplementedError()

    def unindex_all_venues(self) -> None:
        raise NotImplementedError()

    def pop_venue_ids_from_queue(
        self,
        count: int,
        from_error_queue: bool = False,
    ) -> contextlib.AbstractContextManager:
        raise NotImplementedError()

    def pop_collective_offer_template_ids_from_queue(
        self,
        count: int,
        from_error_queue: bool = False,
    ) -> contextlib.AbstractContextManager:
        raise NotImplementedError()

    @classmethod
    def serialize_offer(cls, offer: "offers_models.Offer", last_30_days_bookings: int) -> dict:
        raise NotImplementedError()

    @classmethod
    def serialize_venue(cls, venue: "offerers_models.Venue") -> dict:
        raise NotImplementedError()

    def clean_processing_queues(self) -> None:
        raise NotImplementedError()
