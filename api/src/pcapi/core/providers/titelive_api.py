import abc
import datetime
import typing

from pcapi import repository
from pcapi.connectors import titelive
from pcapi.connectors.serialization.titelive_serializers import TiteliveProductSearchResponse
from pcapi.connectors.serialization.titelive_serializers import TiteliveSearchResultType
from pcapi.core.offers import models as offers_models
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.models import db


class TiteliveSearch(abc.ABC, typing.Generic[TiteliveSearchResultType]):
    titelive_base: titelive.TiteliveBase

    def __init__(self) -> None:
        self.provider = providers_repository.get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)

    def synchronize_products(self, from_date: datetime.date | None = None) -> None:
        if from_date is None:
            from_date = self.get_last_sync_date()

        start_sync_event = self.log_sync_status(providers_models.LocalProviderEventType.SyncStart)
        db.session.add(start_sync_event)

        products_to_update_pages = self.get_updated_titelive_pages(from_date)
        for titelive_page in products_to_update_pages:
            with repository.transaction():
                updated_products = self.upsert_titelive_page(titelive_page)
                db.session.add_all(updated_products)

        stop_sync_event = self.log_sync_status(providers_models.LocalProviderEventType.SyncEnd)
        db.session.add(stop_sync_event)

    def get_last_sync_date(self) -> datetime.date:
        last_sync_event = (
            providers_models.LocalProviderEvent.query.filter(
                providers_models.LocalProviderEvent.provider == self.provider,
                providers_models.LocalProviderEvent.type == providers_models.LocalProviderEventType.SyncEnd,
                providers_models.LocalProviderEvent.payload == self.titelive_base.value,
            )
            .order_by(providers_models.LocalProviderEvent.id.desc())
            .first()
        )
        if last_sync_event is None:
            raise TiteliveDatabaseNotInitializedException()
        return last_sync_event.date.date()

    def log_sync_status(
        self, provider_event_type: providers_models.LocalProviderEventType
    ) -> providers_models.LocalProviderEvent:
        return providers_models.LocalProviderEvent(
            date=datetime.datetime.utcnow(),
            payload=self.titelive_base.value,
            provider=self.provider,
            type=provider_event_type,
        )

    def get_updated_titelive_pages(
        self,
        from_date: datetime.date,
    ) -> typing.Iterator[TiteliveProductSearchResponse[TiteliveSearchResultType]]:
        page_index = 1
        titelive_product_page = None
        while titelive_product_page is None or len(titelive_product_page.result) == titelive.MAX_RESULTS_PER_PAGE:
            titelive_json_response = titelive.search_products(self.titelive_base, from_date, page_index)
            titelive_product_page = self.deserialize_titelive_search_json(titelive_json_response)
            allowed_product_page = self.filter_allowed_products(titelive_product_page)
            yield allowed_product_page
            page_index += 1

    @abc.abstractmethod
    def deserialize_titelive_search_json(
        self, titelive_json_response: dict[str, typing.Any]
    ) -> TiteliveProductSearchResponse[TiteliveSearchResultType]:
        raise NotImplementedError()

    def filter_allowed_products(
        self,
        titelive_product_page: TiteliveProductSearchResponse[TiteliveSearchResultType],
    ) -> TiteliveProductSearchResponse[TiteliveSearchResultType]:
        return titelive_product_page

    def upsert_titelive_page(
        self,
        titelive_page: TiteliveProductSearchResponse[TiteliveSearchResultType],
    ) -> list[offers_models.Product]:
        titelive_results = titelive_page.result
        titelive_eans = [article.gencod for result in titelive_results for article in result.article]

        products = offers_models.Product.query.filter(
            offers_models.Product.extraData["ean"].astext.in_(titelive_eans),
            offers_models.Product.lastProvider == self.provider,  # pylint: disable=comparison-with-callable
        ).all()
        products_by_ean: dict[str, offers_models.Product] = {p.extraData["ean"]: p for p in products}
        for titelive_search_result in titelive_results:
            products_by_ean = self.upsert_titelive_result_in_dict(titelive_search_result, products_by_ean)

        return list(products_by_ean.values())

    @abc.abstractmethod
    def upsert_titelive_result_in_dict(
        self, titelive_search_result: TiteliveSearchResultType, products_by_ean: dict[str, offers_models.Product]
    ) -> dict[str, offers_models.Product]:
        raise NotImplementedError()


class TiteliveDatabaseNotInitializedException(Exception):
    pass
