from typing import Iterable

import pcapi.core.offers.models as offers_models


class SearchBackend:
    def __str__(self) -> str:  # useful in logs
        return str(self.__class__.__name__)

    def enqueue_offer_ids(self, offer_ids: Iterable[int]) -> None:
        raise NotImplementedError()

    def enqueue_offer_ids_in_error(self, offer_ids: Iterable[int]) -> None:
        raise NotImplementedError()

    def enqueue_venue_ids_for_offers(self, venue_ids: Iterable[int]) -> None:
        raise NotImplementedError()

    def pop_offer_ids_from_queue(self, count: int, from_error_queue: bool = False) -> set[int]:
        raise NotImplementedError()

    def get_venue_ids_for_offers_from_queue(self, count: int) -> set[int]:
        raise NotImplementedError()

    def delete_venue_ids_for_offers_from_queue(self, venue_ids: Iterable[int]) -> None:
        raise NotImplementedError()

    def count_offers_to_index_from_queue(self, from_error_queue: bool = False) -> int:
        raise NotImplementedError()

    def check_offer_is_indexed(self, offer: offers_models.Offer) -> bool:
        raise NotImplementedError()

    def index_offers(self, offers: Iterable[offers_models.Offer]) -> None:
        raise NotImplementedError()

    def unindex_offer_ids(self, offers: Iterable[int]) -> None:
        raise NotImplementedError()

    def unindex_all_offers(self) -> None:
        raise NotImplementedError()

    @classmethod
    def serialize_offer(cls, offer: offers_models.Offer) -> dict:
        raise NotImplementedError()
