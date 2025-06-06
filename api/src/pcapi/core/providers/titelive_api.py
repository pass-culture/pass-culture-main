import abc
import datetime
import functools
import logging
import typing
import uuid

import PIL
import pydantic.v1 as pydantic

import pcapi.core.offers.api as offers_api
import pcapi.core.offers.exceptions as offers_exceptions
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi import repository
from pcapi.connectors import thumb_storage
from pcapi.connectors import titelive
from pcapi.connectors.serialization.titelive_serializers import TiteliveWorkType
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.exceptions import NotUpdateProductOrOffers
from pcapi.models import db
from pcapi.utils import requests


logger = logging.getLogger(__name__)


def insert_local_provider_event_on_error(method: typing.Callable) -> typing.Callable:
    @functools.wraps(method)
    def method_with_local_provider_event(
        self: "TiteliveSearchTemplate", *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Any:
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


class TiteliveSearchTemplate(abc.ABC, typing.Generic[TiteliveWorkType]):
    titelive_base: titelive.TiteliveBase

    def __init__(self) -> None:
        self.provider = providers_repository.get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)

    @insert_local_provider_event_on_error
    def synchronize_products(
        self, from_date: datetime.date | None = None, to_date: datetime.date | None = None, from_page: int = 1
    ) -> None:
        if from_date is None:
            from_date = self.get_last_sync_date() - datetime.timedelta(days=1)

        if to_date is None:
            to_date = datetime.date.today() - datetime.timedelta(days=1)

        with repository.transaction():
            start_sync_event = self.log_sync_status(providers_models.LocalProviderEventType.SyncStart)
            db.session.add(start_sync_event)

        products_to_update_pages = self.get_updated_titelive_pages(from_date, to_date, from_page)
        for titelive_page in products_to_update_pages:
            updated_products = self.upsert_titelive_page(titelive_page)
            failed_to_update_products = []
            # Saving the products one by one to avoid a rollback of the whole transaction if and when an error occurs
            for product in updated_products:
                try:
                    with repository.transaction():
                        db.session.add(product)
                except Exception as e:
                    ean = product.ean
                    logger.error(
                        "Error while saving product in db",
                        extra={"exception": e, "productId": product.id, "ean": ean},
                    )
                    failed_to_update_products.append(product)
            updated_products = [product for product in updated_products if product not in failed_to_update_products]

            with repository.transaction():
                updated_thumb_products = self.update_product_thumbnails(updated_products, titelive_page)
                db.session.add_all(updated_thumb_products)

        with repository.transaction():
            stop_sync_event = self.log_sync_status(providers_models.LocalProviderEventType.SyncEnd)
            db.session.add(stop_sync_event)

    def get_last_sync_date(self) -> datetime.date:
        last_sync_event = (
            db.session.query(providers_models.LocalProviderEvent)
            .filter(
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
        self, from_date: datetime.date, to_date: datetime.date, from_page: int
    ) -> typing.Iterator[list[TiteliveWorkType]]:
        page_index = from_page

        days = (to_date - from_date).days
        for day_offset in range(days + 1):
            updated_date = from_date + datetime.timedelta(days=day_offset)
            has_next_page = True
            while has_next_page:
                json_response = titelive.search_products(self.titelive_base, updated_date, page_index)
                product_page = self.get_product_info_from_search_response(json_response)
                recent_product_page = filter_recent_products(product_page, updated_date)
                allowed_product_page, not_allowed_eans = self.partition_allowed_products(recent_product_page)
                allowed_product_page = [work for work in allowed_product_page if work.article]
                offers_api.reject_inappropriate_products(not_allowed_eans, author=None)

                yield allowed_product_page

                # sometimes titelive returns a partially filled page while having a next page in store for us
                has_next_page = bool(product_page)
                page_index += 1

            page_index = 1

    def get_product_info_from_search_response(self, titelive_json_response: list[dict]) -> list[TiteliveWorkType]:
        return self.deserialize_titelive_products(titelive_json_response)

    def deserialize_titelive_products(self, titelive_json_response: list[dict]) -> list[TiteliveWorkType]:
        deserialized_works = []
        for work in titelive_json_response:
            try:
                deserialized_work = self.deserialize_titelive_product(work)
            except pydantic.ValidationError as e:
                title = work.get("titre")
                logger.error("%s %s could not be deserialized: %s", self.titelive_base.value, title, e)
            else:
                deserialized_works.append(deserialized_work)

        return deserialized_works

    @abc.abstractmethod
    def deserialize_titelive_product(self, titelive_work: dict) -> TiteliveWorkType:
        raise NotImplementedError()

    @abc.abstractmethod
    def partition_allowed_products(
        self, titelive_product_page: list[TiteliveWorkType]
    ) -> tuple[
        list[TiteliveWorkType],
        list[str],
    ]:
        raise NotImplementedError()

    def upsert_titelive_page(
        self,
        titelive_page: list[TiteliveWorkType],
    ) -> list[offers_models.Product]:
        titelive_eans = [article.gencod for work in titelive_page for article in work.article]

        products = (
            db.session.query(offers_models.Product)
            .filter(
                offers_models.Product.ean.in_(titelive_eans),
                offers_models.Product.lastProviderId.is_not(None),
            )
            .all()
        )

        products_by_ean: dict[str, offers_models.Product] = {p.ean: p for p in products}
        for titelive_search_result in titelive_page:
            products_by_ean = self.upsert_titelive_result_in_dict(titelive_search_result, products_by_ean)

        return list(products_by_ean.values())

    @abc.abstractmethod
    def upsert_titelive_result_in_dict(
        self, titelive_search_result: TiteliveWorkType, products_by_ean: dict[str, offers_models.Product]
    ) -> dict[str, offers_models.Product]:
        raise NotImplementedError()

    def update_product_thumbnails(
        self,
        products: list[offers_models.Product],
        titelive_page: list[TiteliveWorkType],
    ) -> list[offers_models.Product]:
        thumbnail_url_by_ean: dict[str, dict[offers_models.ImageType, str]] = {}

        for work in titelive_page:
            for article in work.article:
                thumbnail_url_by_ean[article.gencod] = {}
                if not article.imagesUrl:
                    continue
                if article.has_image:
                    thumbnail_url_by_ean[article.gencod][offers_models.ImageType.RECTO] = article.imagesUrl.recto
                if article.has_verso_image:
                    thumbnail_url_by_ean[article.gencod][offers_models.ImageType.VERSO] = article.imagesUrl.verso

        for product in products:
            assert product.extraData, "product %s initialized without extra data" % product.id

            ean = product.ean
            assert ean, "product %s initialized without ean" % product.id

            new_thumbnail_urls = thumbnail_url_by_ean.get(ean)
            if not new_thumbnail_urls:
                logger.warning("No thumbnail for product ean %s", ean)
                continue
            try:
                self.remove_product_mediation(product)
                for image_type in offers_models.ImageType:
                    new_thumbnail_url = new_thumbnail_urls.get(image_type)
                    if new_thumbnail_url is not None:
                        image_id = str(uuid.uuid4())
                        mediation = offers_models.ProductMediation(
                            productId=product.id,
                            lastProvider=self.provider,
                            imageType=image_type,
                            uuid=image_id,
                        )
                        db.session.add(mediation)

                        image_bytes = titelive.download_titelive_image(new_thumbnail_url)
                        thumb_storage.create_thumb(
                            product,
                            image_bytes,
                            keep_ratio=True,
                            object_id=image_id,
                        )
                db.session.commit()
            except (
                requests.ExternalAPIException,
                PIL.UnidentifiedImageError,
                OSError,
                offers_exceptions.ImageValidationError,
            ) as e:
                db.session.rollback()
                logger.error(
                    "Error while downloading Titelive image",
                    extra={
                        "exception": e,
                        "url_recto": new_thumbnail_urls.get(offers_models.ImageType.RECTO),
                        "url_verso": new_thumbnail_urls.get(offers_models.ImageType.VERSO),
                        "request_type": "image",
                    },
                )
                continue

        return products

    def remove_product_mediation(self, product: offers_models.Product) -> None:
        """
        warning this function does not automatically commit the transaction
        """
        product_mediations = db.session.query(offers_models.ProductMediation).filter(
            offers_models.ProductMediation.productId == product.id,
            offers_models.ProductMediation.lastProvider == self.provider,
        )
        for product_mediation in product_mediations:
            db.session.delete(product_mediation)

    def truncate_string(self, s: str) -> str:
        max_length = 140
        if len(s) > max_length:
            return s[: max_length - 1] + "…"
        return s


def filter_recent_products(
    titelive_product_page: list[TiteliveWorkType],
    from_date: datetime.date,
) -> list[TiteliveWorkType]:
    """Filters out articles that were not updated since from_date."""
    for work in titelive_product_page:
        work.article = [
            article
            for article in work.article
            if article.datemodification is None or article.datemodification >= from_date
        ]
    return titelive_product_page


def activate_newly_eligible_product_and_offers(product: offers_models.Product) -> None:
    is_product_newly_eligible = product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
    ean = product.ean
    if ean is None:
        return
    if is_product_newly_eligible:
        try:
            offers_api.approves_provider_product_and_rejected_offers(ean)
        except NotUpdateProductOrOffers as exception:
            logger.error("Product with ean cannot be approved", extra={"ean": ean, "exc": str(exception)})


class TiteliveDatabaseNotInitializedException(Exception):
    pass
