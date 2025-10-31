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
from pcapi.connectors.big_query.queries.product import BigQueryProductModel
from pcapi.connectors.big_query.queries.product import ProductsToSyncQuery
from pcapi.connectors.titelive import TiteliveBase
from pcapi.core.categories.subcategories import LIVRE_PAPIER
from pcapi.core.object_storage.backends.base import FileNotFound
from pcapi.core.object_storage.backends.gcp import GCPBackend
from pcapi.core.object_storage.backends.gcp import GCPData
from pcapi.core.providers import constants
from pcapi.core.providers.models import LocalProviderEventType
from pcapi.core.providers.titelive_api import activate_newly_eligible_product_and_offers
from pcapi.core.providers.titelive_book_search import get_book_format
from pcapi.core.providers.titelive_book_search import get_gtl_id
from pcapi.core.providers.titelive_book_search import get_ineligibility_reasons
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.chunks import get_chunks
from pcapi.utils.repository import transaction


logger = logging.getLogger(__name__)


class BigQueryProductSync:
    titelive_base = TiteliveBase.BOOK

    def __init__(self) -> None:
        # The product whitelist currently contains only a small number of EANs,
        # so we can safely load and check them all in a single query.
        # If the table grows too large in the future, we may need to perform
        # individual checks instead of loading everything at once.
        self.product_whitelist_eans = {ean for (ean,) in db.session.query(fraud_models.ProductWhitelist.ean).all()}
        logger.info("Loaded %d EANs from the whitelist.", len(self.product_whitelist_eans))

        self.provider = providers_repository.get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)
        self.gcp_data = GCPData()
        self.gcp_backend = GCPBackend()

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

    def _remove_existing_mediations(self, product: offers_models.Product) -> None:
        (
            db.session.query(offers_models.ProductMediation)
            .filter(offers_models.ProductMediation.productId == product.id)
            .delete(synchronize_session=False)
        )

    def _copy_image_from_data_bucket_to_backend_bucket(self, source_uuid: str) -> str | None:
        if not self.gcp_data or not self.gcp_backend:
            logger.error("GCS backends not initialized, cannot copy image %s", source_uuid)
            return None

        if not source_uuid:
            return None
        try:
            if self.gcp_backend.object_exists(settings.THUMBS_FOLDER_NAME, source_uuid):
                return source_uuid

            if not self.gcp_data.object_exists(settings.DATA_TITELIVE_THUMBS_FOLDER_NAME, source_uuid):
                logger.warning(
                    "Image %s not found in source bucket %s. Cannot copy.",
                    source_uuid,
                    self.gcp_data.bucket_name,
                )
                return None

            logger.info(
                "Copying image %s from %s to %s...",
                source_uuid,
                self.gcp_data.bucket_name,
                self.gcp_backend.bucket_name,
            )

            self.gcp_data.copy_object_to(
                source_folder=settings.DATA_TITELIVE_THUMBS_FOLDER_NAME,
                source_object_id=source_uuid,
                destination_backend=self.gcp_backend,
                destination_folder=settings.THUMBS_FOLDER_NAME,
                destination_object_id=source_uuid,
            )
            return source_uuid
        except FileNotFound:
            return None

        except Exception as err:
            logger.error(
                "Failed to copy image %s from bucket %s to %s: %s",
                source_uuid,
                self.gcp_data.bucket_name,
                self.gcp_backend.bucket_name,
                err,
            )
            return None

    def _update_product_images(self, product: offers_models.Product, bq_product: BigQueryProductModel) -> None:
        if not bq_product.has_image:
            return

        if bq_product.recto_uuid:
            current_recto = next(
                (m for m in product.productMediations if m.imageType == offers_models.ImageType.RECTO), None
            )
            if current_recto and current_recto.uuid == bq_product.recto_uuid:
                pass
            else:
                source_uuid = self._copy_image_from_data_bucket_to_backend_bucket(bq_product.recto_uuid)
                if not source_uuid:
                    logger.warning(
                        "Skipping RECTO mediation for EAN %s (UUID %s) due to GCS copy failure.",
                        product.ean,
                        bq_product.recto_uuid,
                    )
                else:
                    if current_recto:
                        db.session.delete(current_recto)

                    recto_mediation = offers_models.ProductMediation(
                        productId=product.id,
                        uuid=bq_product.recto_uuid,
                        imageType=offers_models.ImageType.RECTO,
                        lastProvider=self.provider,
                    )
                    db.session.add(recto_mediation)

        if bq_product.has_verso_image and bq_product.verso_uuid:
            current_verso = next(
                (m for m in product.productMediations if m.imageType == offers_models.ImageType.VERSO), None
            )
            if current_verso and current_verso.uuid == bq_product.verso_uuid:
                pass
            else:
                source_uuid = self._copy_image_from_data_bucket_to_backend_bucket(bq_product.verso_uuid)
                if not source_uuid:
                    logger.warning(
                        "Skipping VERSO mediation for EAN %s (UUID %s) due to GCS copy failure.",
                        product.ean,
                        bq_product.recto_uuid,
                    )
                else:
                    if current_verso:
                        db.session.delete(current_verso)

                    verso_mediation = offers_models.ProductMediation(
                        productId=product.id,
                        uuid=bq_product.verso_uuid,
                        imageType=offers_models.ImageType.VERSO,
                        lastProvider=self.provider,
                    )
                    db.session.add(verso_mediation)

    def run_synchronization(self, batch_size: int) -> None:
        logger.info("Starting product synchronization")

        total_products_upserted = 0
        ineligible_eans = []

        products_iterator = ProductsToSyncQuery().execute()

        for bq_product_batch in get_chunks(products_iterator, batch_size):
            logger.info("Processing batch of %d products...", len(bq_product_batch))

            valid_bq_products_in_batch = []

            for bq_product in bq_product_batch:
                reasons = get_ineligibility_reasons(bq_product, bq_product.titre)

                if reasons:
                    if bq_product.ean in self.product_whitelist_eans:
                        logger.info(
                            "Skipping ineligibility for EAN %s (reasons: %s): product is whitelisted.",
                            bq_product.ean,
                            reasons,
                        )
                    else:
                        ineligible_eans.append(bq_product.ean)
                        logger.info("Rejecting product EAN %s for reason(s): %s.", bq_product.ean, reasons)
                        continue

                valid_bq_products_in_batch.append(bq_product)

            if not valid_bq_products_in_batch:
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
                    logger.debug("Flushing session to get new product IDs...")
                    db.session.flush()

                    for product, bq_product in image_updates_to_run:
                        if not product.id:
                            logger.warning("Product EAN %s has no ID after flush, skipping images.", product.ean)
                            continue
                        self._update_product_images(product, bq_product)

                total_products_upserted += len(valid_bq_products_in_batch)
                logger.info("Successfully upserted batch of %d products.", len(valid_bq_products_in_batch))

            except Exception as exc:
                logger.warning(
                    "Batch upsert failed: %s. Retrying %d products one by one...", exc, len(valid_bq_products_in_batch)
                )
                db.session.rollback()

                individual_success_count = 0

                for bq_product in valid_bq_products_in_batch:
                    if self._process_one_product(bq_product):
                        individual_success_count += 1

                total_products_upserted += individual_success_count
                logger.info(
                    "Rescued %d products from failed batch. %d truly failed.",
                    individual_success_count,
                    len(valid_bq_products_in_batch) - individual_success_count,
                )

        if ineligible_eans:
            offers_api.reject_inappropriate_products(ineligible_eans, author=None)

        logger.info("Synchronization complete. Summary:")
        logger.info("  > %d products upserted.", total_products_upserted)
        logger.info("  > %d products rejected.", len(ineligible_eans))
        logger.info("  > %d products processed in total.", total_products_upserted + len(ineligible_eans))

    def _process_one_product(self, bq_product: BigQueryProductModel, log_failure: bool = True) -> bool:
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
            if log_failure:
                logger.error("Failed to upsert product with EAN %s during individual retry: %s", bq_product.ean, e)
            db.session.rollback()
            return False

    def synchronize_products(self, batch_size: int) -> None:
        try:
            with transaction():
                start_sync_event = self.log_sync_status(LocalProviderEventType.SyncStart)
                db.session.add(start_sync_event)

            self.run_synchronization(batch_size)

            with transaction():
                stop_sync_event = self.log_sync_status(LocalProviderEventType.SyncEnd)
                db.session.add(stop_sync_event)

        except Exception as e:
            with transaction():
                sync_error_event = self.log_sync_status(LocalProviderEventType.SyncError, e.__class__.__name__)
                db.session.add(sync_error_event)
            raise

    def create_or_update(
        self, bq_product: BigQueryProductModel, product: offers_models.Product | None
    ) -> offers_models.Product:
        is_update = product is not None
        if not is_update:
            logger.info("Create Product with ean %s", bq_product.ean)
            product = offers_models.Product(ean=bq_product.ean)
        else:
            logger.info("Update existing Product with ean %s", bq_product.ean)

        assert product  # helps mypy
        product.name = textwrap.shorten(
            bq_product.titre,
            width=constants.TITELIVE_PRODUCT_NAME_MAX_LENGTH,
            placeholder="…",
        )
        product.description = bq_product.resume
        product.lastProviderId = self.provider.id
        product.dateModifiedAtLastProvider = date_utils.get_naive_utc_now()
        product.subcategoryId = LIVRE_PAPIER.id

        if product.extraData is None:
            product.extraData = offers_models.OfferExtraData()
        product.extraData.update(self._build_product_extra_data(bq_product))

        if is_update:
            activate_newly_eligible_product_and_offers(product)

        return product

    def _build_product_extra_data(self, bq_product: BigQueryProductModel) -> offers_models.OfferExtraData:
        gtl_id = get_gtl_id(bq_product)

        return offers_models.OfferExtraData(
            author=", ".join(bq_product.auteurs_multi) if bq_product.auteurs_multi else None,
            bookFormat=get_book_format(bq_product.codesupport),
            date_parution=str(bq_product.dateparution) if bq_product.dateparution else None,
            editeur=bq_product.editeur,
            gtl_id=gtl_id,
            langueiso=bq_product.langueiso,
            prix_livre=bq_product.prix,
        )
