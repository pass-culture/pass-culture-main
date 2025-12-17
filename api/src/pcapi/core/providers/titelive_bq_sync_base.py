import abc
import itertools
import logging
import textwrap

import sqlalchemy.orm as sa_orm

import pcapi.core.fraud.models as fraud_models
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.connectors.big_query.queries.product import BigQueryTiteliveBookProductModel
from pcapi.connectors.big_query.queries.product import BigQueryTiteliveMusicProductModel
from pcapi.connectors.titelive import TiteliveBase
from pcapi.core.object_storage.backends.gcp import GCPBackend
from pcapi.core.object_storage.backends.gcp import GCPData
from pcapi.core.object_storage.backends.utils import copy_file_between_storage_backends
from pcapi.core.providers import constants
from pcapi.core.providers.models import LocalProviderEventType
from pcapi.core.providers.titelive_api import activate_newly_eligible_product_and_offers
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.repository import transaction


logger = logging.getLogger(__name__)


class BigQuerySyncTemplate[
    BigQueryTiteliveProductModelType: BigQueryTiteliveBookProductModel | BigQueryTiteliveMusicProductModel
](abc.ABC):
    def __init__(self) -> None:
        self.product_whitelist_eans = {ean for (ean,) in db.session.query(fraud_models.ProductWhitelist.ean).all()}
        logger.info("Loaded EANs from the whitelist.", extra={"count": len(self.product_whitelist_eans)})
        self.provider = providers_repository.get_provider_by_name(providers_constants.TITELIVE_ENRICHED_BY_DATA)
        self.gcp_data = GCPData()
        self.gcp_backend = GCPBackend()

    @property
    @abc.abstractmethod
    def titelive_base(self) -> TiteliveBase:
        """Returns the Titelive base enum (BOOK or MUSIC)."""
        pass

    @abc.abstractmethod
    def get_query(self) -> BaseQuery:
        """Returns the BigQuery query instance to execute."""
        pass

    @abc.abstractmethod
    def filter_batch(
        self, batch: tuple[BigQueryTiteliveProductModelType, ...]
    ) -> tuple[list[BigQueryTiteliveProductModelType], list[str]]:
        """
        Filters a batch of products based on specific rules (eligibility, whitelist).
        Returns:
            - A list of valid products to upsert.
            - A list of EANs that were rejected/ineligible.
        """
        pass

    @abc.abstractmethod
    def fill_product_specifics(
        self, product: offers_models.Product, bq_product: BigQueryTiteliveProductModelType
    ) -> None:
        """
        Populates specific fields of the product (subcategoryId, extraData) based on the BQ model.
        """
        pass

    def log_sync_status(
        self, event_type: LocalProviderEventType, message: str | None = None
    ) -> providers_models.LocalProviderEvent:
        message = f"{self.titelive_base.value} : {message}" if message else self.titelive_base.value
        return providers_models.LocalProviderEvent(
            date=date_utils.get_naive_utc_now(),
            payload=message,
            provider=self.provider,
            type=event_type,
        )

    def _sync_image_mediations(
        self, product: offers_models.Product, image_type: offers_models.ImageType, target_uuid: str
    ) -> None:
        mediations_by_uuid = {m.uuid: m for m in product.productMediations if m.imageType == image_type}
        if target_uuid not in mediations_by_uuid:
            source_uuid = copy_file_between_storage_backends(
                source_storage=self.gcp_data,
                destination_storage=self.gcp_backend,
                source_folder=settings.DATA_TITELIVE_THUMBS_FOLDER_NAME,
                destination_folder=settings.THUMBS_FOLDER_NAME,
                file_id=target_uuid,
            )
            if not source_uuid:
                logger.warning(
                    "Skipping mediation creation due to GCS copy failure",
                    extra={"ean": product.ean, "image_type": image_type.name, "uuid": target_uuid},
                )
                return

            new_mediation = offers_models.ProductMediation(
                productId=product.id,
                uuid=target_uuid,
                imageType=image_type,
                lastProvider=self.provider,
            )
            db.session.add(new_mediation)
            logger.info(
                "Created new mediation",
                extra={"product_id": product.id, "image_type": image_type.name, "uuid": target_uuid},
            )

        mediations_by_uuid.pop(target_uuid, None)
        for mediation in mediations_by_uuid.values():
            logger.info(
                "Deleting mediation",
                extra={"product_id": product.id, "image_type": image_type.name, "deleted_uuid": mediation.uuid},
            )
            db.session.delete(mediation)

    def _update_product_images(
        self, product: offers_models.Product, bq_product: BigQueryTiteliveProductModelType
    ) -> None:
        if not bq_product.has_image:
            return

        recto_uuid = bq_product.recto_uuid
        if recto_uuid:
            self._sync_image_mediations(product, offers_models.ImageType.RECTO, recto_uuid)

        if bq_product.has_verso_image:
            verso_uuid = bq_product.verso_uuid
            if verso_uuid:
                self._sync_image_mediations(product, offers_models.ImageType.VERSO, verso_uuid)

    def synchronize_products(self, batch_size: int) -> None:
        try:
            with transaction():
                db.session.add(self.log_sync_status(LocalProviderEventType.SyncStart))

            self.run_synchronization(batch_size)

            with transaction():
                db.session.add(self.log_sync_status(LocalProviderEventType.SyncEnd))
        except Exception as e:
            db.session.rollback()
            with transaction():
                db.session.add(self.log_sync_status(LocalProviderEventType.SyncError, e.__class__.__name__))
            raise

    def run_synchronization(self, batch_size: int) -> None:
        logger.info("Starting product synchronization", extra={"titelive_base": self.titelive_base.value})
        total_products_upserted = 0
        total_ineligible_count = 0

        products_iterator = self.get_query().execute()

        for batch_number, bq_product_batch in enumerate(itertools.batched(products_iterator, batch_size), start=1):
            logger.info("Processing batch...", extra={"batch_size": len(bq_product_batch)})

            valid_bq_products_in_batch, batch_ineligible_eans = self.filter_batch(bq_product_batch)

            if batch_ineligible_eans:
                try:
                    offers_api.reject_inappropriate_products(batch_ineligible_eans, author=None)
                    total_ineligible_count += len(batch_ineligible_eans)
                except Exception as e:
                    db.session.rollback()
                    logger.error(
                        "Failed to reject inappropriate products in batch",
                        extra={"error": e, "count": len(batch_ineligible_eans), "eans": batch_ineligible_eans},
                    )

            if not valid_bq_products_in_batch:
                logger.info(
                    "Batch processed (only rejections).",
                    extra={
                        "batch_number": batch_number,
                        "total_processed_so_far": total_products_upserted + total_ineligible_count,
                        "total_upserted_so_far": total_products_upserted,
                        "total_rejected_so_far": total_ineligible_count,
                    },
                )
                continue

            try:
                with transaction():
                    batch_eans = {bq.ean for bq in valid_bq_products_in_batch}
                    existing_products = (
                        db.session.query(offers_models.Product)
                        .filter(offers_models.Product.ean.in_(batch_eans))
                        .options(sa_orm.selectinload(offers_models.Product.productMediations))
                        .all()
                    )
                    existing_products_map = {p.ean: p for p in existing_products}

                    products_to_upsert = []
                    image_updates_to_run = []

                    for bq_product in valid_bq_products_in_batch:
                        existing_product = existing_products_map.get(bq_product.ean)
                        product = self.create_or_update(bq_product, existing_product)
                        products_to_upsert.append(product)
                        image_updates_to_run.append((product, bq_product))

                    db.session.add_all(products_to_upsert)
                    db.session.flush()

                    for product, bq_product in image_updates_to_run:
                        self._update_product_images(product, bq_product)

                total_products_upserted += len(valid_bq_products_in_batch)
                logger.info("Successfully upserted batch.", extra={"count": len(valid_bq_products_in_batch)})

            except Exception as exc:
                logger.warning(
                    "Batch upsert failed. Retrying one by one...",
                    extra={"error": exc, "retry_count": len(valid_bq_products_in_batch)},
                )
                db.session.rollback()

                for bq_product in valid_bq_products_in_batch:
                    if self._process_one_product(bq_product):
                        total_products_upserted += 1

            logger.info(
                "Synchronization progress update",
                extra={
                    "batch_number": batch_number,
                    "total_processed_so_far": total_products_upserted + total_ineligible_count,
                    "total_upserted_so_far": total_products_upserted,
                    "total_rejected_so_far": total_ineligible_count,
                },
            )

        logger.info(
            "Synchronization complete.",
            extra={
                "upserted": total_products_upserted,
                "rejected": total_ineligible_count,
                "total_processed": total_products_upserted + total_ineligible_count,
            },
        )

    def _process_one_product(self, bq_product: BigQueryTiteliveProductModelType) -> bool:
        try:
            with transaction():
                existing_product = (
                    db.session.query(offers_models.Product)
                    .filter_by(ean=bq_product.ean)
                    .options(sa_orm.selectinload(offers_models.Product.productMediations))
                    .one_or_none()
                )
                product = self.create_or_update(bq_product, existing_product)
                db.session.add(product)
                db.session.flush()
                self._update_product_images(product, bq_product)
            return True
        except Exception as e:
            logger.error("Failed individual upsert", extra={"ean": bq_product.ean, "error": e})
            db.session.rollback()
            return False

    def create_or_update(
        self, bq_product: BigQueryTiteliveProductModelType, product: offers_models.Product | None
    ) -> offers_models.Product:
        is_update = product is not None
        if not product:
            logger.info("Creating new product.", extra={"ean": bq_product.ean})
            product = offers_models.Product(ean=bq_product.ean)
        else:
            logger.info("Updating existing product.", extra={"ean": bq_product.ean})

        product.name = textwrap.shorten(
            bq_product.titre,
            width=constants.TITELIVE_PRODUCT_NAME_MAX_LENGTH,
            placeholder="…",
        )
        product.description = bq_product.resume
        product.lastProviderId = self.provider.id
        product.dateModifiedAtLastProvider = date_utils.get_naive_utc_now()

        self.fill_product_specifics(product, bq_product)

        if is_update:
            activate_newly_eligible_product_and_offers(product)

        return product
