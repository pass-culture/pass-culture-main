import abc
import datetime
import functools
import logging
import typing
import uuid

import PIL

from pcapi import repository
from pcapi import settings
from pcapi.connectors import thumb_storage
from pcapi.connectors import titelive
from pcapi.connectors.serialization.titelive_serializers import TiteliveProductSearchResponse
from pcapi.connectors.serialization.titelive_serializers import TiteliveSearchResultType
from pcapi.core.offers import models as offers_models
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.models import db
from pcapi.utils import requests


logger = logging.getLogger(__name__)


def insert_local_provider_event_on_error(method: typing.Callable) -> typing.Callable:
    @functools.wraps(method)
    def method_with_local_provider_event(self: "TiteliveSearch", *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        try:
            return method(self, *args, **kwargs)
        except Exception as e:
            with repository.transaction():
                sync_error_event = self.log_sync_status(
                    providers_models.LocalProviderEventType.SyncError, e.__class__.__name__
                )
                db.session.add(sync_error_event)

            raise

    return method_with_local_provider_event


class TiteliveSearch(abc.ABC, typing.Generic[TiteliveSearchResultType]):
    titelive_base: titelive.TiteliveBase

    def __init__(self) -> None:
        self.provider = providers_repository.get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)

    @insert_local_provider_event_on_error
    def synchronize_products(self, from_date: datetime.date | None = None, from_page: int = 1) -> None:
        if from_date is None:
            from_date = self.get_last_sync_date()

        with repository.transaction():
            start_sync_event = self.log_sync_status(providers_models.LocalProviderEventType.SyncStart)
            db.session.add(start_sync_event)

        products_to_update_pages = self.get_updated_titelive_pages(from_date, from_page)
        for titelive_page in products_to_update_pages:
            with repository.transaction():
                updated_products = self.upsert_titelive_page(titelive_page)
                db.session.add_all(updated_products)

            with repository.transaction():
                updated_thumb_products = self.update_product_thumbnails(updated_products, titelive_page)
                db.session.add_all(updated_thumb_products)

        with repository.transaction():
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
        self, provider_event_type: providers_models.LocalProviderEventType, message: str | None = None
    ) -> providers_models.LocalProviderEvent:
        message = f"{self.titelive_base.value} : {message}" if message else self.titelive_base.value
        return providers_models.LocalProviderEvent(
            date=datetime.datetime.utcnow(),
            payload=message,
            provider=self.provider,
            type=provider_event_type,
        )

    def get_updated_titelive_pages(
        self, from_date: datetime.date, from_page: int
    ) -> typing.Iterator[TiteliveProductSearchResponse[TiteliveSearchResultType]]:
        page_index = from_page
        has_next_page = True
        while has_next_page:
            titelive_json_response = titelive.search_products(self.titelive_base, from_date, page_index)
            titelive_product_page = self.deserialize_titelive_search_json(titelive_json_response)
            titlive_recent_product_page = self.filter_recent_products(titelive_product_page, from_date)
            allowed_product_page = self.filter_allowed_products(titlive_recent_product_page)
            allowed_product_page.result = [oeuvre for oeuvre in allowed_product_page.result if oeuvre.article]
            yield allowed_product_page
            # sometimes titelive returns a partially filled page while having a next page in store for us
            has_next_page = bool(titelive_product_page.result)
            page_index += 1

    @abc.abstractmethod
    def deserialize_titelive_search_json(
        self, titelive_json_response: dict[str, typing.Any]
    ) -> TiteliveProductSearchResponse[TiteliveSearchResultType]:
        raise NotImplementedError()

    def filter_recent_products(
        self,
        titelive_product_page: TiteliveProductSearchResponse[TiteliveSearchResultType],
        from_date: datetime.date,
    ) -> TiteliveProductSearchResponse[TiteliveSearchResultType]:
        """Filters out articles that were not updated since from_date."""
        for oeuvre in titelive_product_page.result:
            oeuvre.article = [article for article in oeuvre.article if article.datemodification >= from_date]
        return titelive_product_page

    def filter_allowed_products(
        self,
        titelive_product_page: TiteliveProductSearchResponse[TiteliveSearchResultType],
    ) -> TiteliveProductSearchResponse[TiteliveSearchResultType]:
        return titelive_product_page

    def upsert_titelive_page(
        self,
        titelive_page: TiteliveProductSearchResponse[TiteliveSearchResultType],
    ) -> list[offers_models.Product]:
        titelive_eans = [article.gencod for result in titelive_page.result for article in result.article]

        products = offers_models.Product.query.filter(
            offers_models.Product.extraData["ean"].astext.in_(titelive_eans),
            offers_models.Product.lastProviderId.is_not(None),
        ).all()

        titelive_page, products = self.dodge_sync_collision(titelive_page, products)

        products_by_ean: dict[str, offers_models.Product] = {p.extraData["ean"]: p for p in products}
        for titelive_search_result in titelive_page.result:
            products_by_ean = self.upsert_titelive_result_in_dict(titelive_search_result, products_by_ean)

        return list(products_by_ean.values())

    def dodge_sync_collision(
        self,
        titelive_page: TiteliveProductSearchResponse[TiteliveSearchResultType],
        existing_products: list[offers_models.Product],
    ) -> tuple[TiteliveProductSearchResponse[TiteliveSearchResultType], list[offers_models.Product]]:
        """Returns the titelive search page and product list without products that were already imported
        by another provider, and logs as error the removed products EAN and their provider."""
        products_from_other_provider = [p for p in existing_products if p.lastProvider != self.provider]
        if not products_from_other_provider:
            return titelive_page, existing_products

        # Some EANs like 0030206040920 are both a book and a CD, as such Titelive returns those articles
        # for both books and music. However, EANs from providers must be unique in our database, and this
        # is enforced by a unicity constraint in Product.idAtProviders.
        # Those EANs are assigned in our database to the first provider that imports them. Provider change
        # must be done manually.
        other_provider_by_product_ean = {
            p.extraData["ean"]: p.lastProviderId for p in products_from_other_provider if p.extraData
        }
        logger.error("Conflicting products already exist: %s, skipping", other_provider_by_product_ean)

        for oeuvre in titelive_page.result:
            oeuvre.article = [
                article for article in oeuvre.article if article.gencod not in other_provider_by_product_ean
            ]
        titelive_page.result = [oeuvre for oeuvre in titelive_page.result if oeuvre.article]

        current_provider_managed_products = [p for p in existing_products if p.lastProvider == self.provider]
        return titelive_page, current_provider_managed_products

    @abc.abstractmethod
    def upsert_titelive_result_in_dict(
        self, titelive_search_result: TiteliveSearchResultType, products_by_ean: dict[str, offers_models.Product]
    ) -> dict[str, offers_models.Product]:
        raise NotImplementedError()

    def update_product_thumbnails(
        self,
        products: list[offers_models.Product],
        titelive_page: TiteliveProductSearchResponse[TiteliveSearchResultType],
    ) -> list[offers_models.Product]:
        thumbnail_url_by_ean: dict[str, dict[offers_models.TiteliveImageType, str | None]] = {
            article.gencod: {
                offers_models.TiteliveImageType.RECTO: article.imagesUrl.recto,
                offers_models.TiteliveImageType.VERSO: article.imagesUrl.verso,
            }
            for result in titelive_page.result
            for article in result.article
            if article.image != "0"
        }

        for product in products:
            assert product.extraData, "product %s initialized without extra data" % product.id

            ean = product.extraData.get("ean")
            assert ean, "product %s initialized without ean" % product.id

            new_thumbnail_urls = thumbnail_url_by_ean.get(ean)
            if not new_thumbnail_urls:
                logger.warning("No thumbnail for product ean %s", ean)
                continue
            try:
                self.remove_product_mediation(product)
                for image_type in offers_models.TiteliveImageType:
                    new_thumbnail_url = new_thumbnail_urls.get(image_type)
                    if new_thumbnail_url is not None:
                        image_id = str(uuid.uuid4())
                        mediation = offers_models.ProductMediation(
                            productId=product.id,
                            lastProvider=self.provider,
                            imageType=image_type,
                            url=f"{settings.OBJECT_STORAGE_URL}/{settings.THUMBS_FOLDER_NAME}/{image_id}",
                        )
                        db.session.add(mediation)

                        image_bytes = titelive.download_titelive_image(new_thumbnail_url)
                        thumb_storage.create_thumb(
                            product,
                            image_bytes,
                            storage_id_suffix_str="",
                            keep_ratio=True,
                            object_id=image_id,
                        )
                db.session.commit()
            except (requests.ExternalAPIException, PIL.UnidentifiedImageError) as e:
                db.session.rollback()
                print("Error while downloading Titelive imageÔ")
                logger.error(
                    "Error while downloading Titelive image",
                    extra={
                        "exception": e,
                        "url_recto": new_thumbnail_urls.get(offers_models.TiteliveImageType.RECTO),
                        "url_verso": new_thumbnail_urls.get(offers_models.TiteliveImageType.VERSO),
                        "request_type": "image",
                    },
                )
                continue

        return products

    def remove_product_mediation(self, product: offers_models.Product) -> None:
        """
        warning this function does not automatically commit the transaction
        """
        product_mediations = offers_models.ProductMediation.query.filter(
            offers_models.ProductMediation.productId == product.id,
            offers_models.ProductMediation.lastProvider == self.provider,  # pylint: disable=comparison-with-callable
        )
        for product_mediation in product_mediations:
            db.session.delete(product_mediation)


class TiteliveDatabaseNotInitializedException(Exception):
    pass
