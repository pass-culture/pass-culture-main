import logging
from typing import Type

import sqlalchemy.exc as sa_exc

import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.repository as providers_repository
from pcapi.connectors.big_query.importer.base import AbstractImporter
from pcapi.connectors.big_query.queries import product as bq_product_queries
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import models as product_models
from pcapi.models import db
from pcapi.utils.repository import transaction


logger = logging.getLogger(__name__)


class ProductImporter(
    AbstractImporter[
        bq_product_queries.ProductModel,
        bq_product_queries.ProductDeltaModel,
        product_models.Product,
    ]
):
    def __init__(self) -> None:
        self.provider = providers_repository.get_provider_by_name(providers_constants.TITELIVE_ENRICHED_BY_DATA)

    def get_sqlalchemy_class(self) -> Type[product_models.Product]:
        return product_models.Product

    def get_full_import_query(self) -> BaseQuery:
        raise NotImplementedError("La réimportation complète des produits n'est pas supportée.")

    def get_delta_import_query(self) -> bq_product_queries.ProductDeltaQuery:
        return bq_product_queries.ProductDeltaQuery()

    def exists(
        self, model: bq_product_queries.ProductModel | bq_product_queries.ProductDeltaModel
    ) -> product_models.Product | None:
        if not model.ean:
            return None
        return db.session.query(product_models.Product).filter_by(ean=model.ean).one_or_none()

    def create(
        self, model: bq_product_queries.ProductModel | bq_product_queries.ProductDeltaModel
    ) -> product_models.Product:
        return product_models.Product(
            name=model.name,
            description=model.description,
            ean=model.ean,
            lastProviderId=self.provider.id,
            subcategoryId=model.subcategoryId,
            extraData=model.extraData or offers_models.OfferExtraData(),
        )

    def update(self, sqlalchemy_obj: product_models.Product, delta_model: bq_product_queries.ProductDeltaModel) -> None:
        sqlalchemy_obj.name = delta_model.name
        sqlalchemy_obj.description = delta_model.description
        sqlalchemy_obj.subcategoryId = delta_model.subcategoryId

        if delta_model.extraData:
            if sqlalchemy_obj.extraData is None:
                sqlalchemy_obj.extraData = offers_models.OfferExtraData()
            sqlalchemy_obj.extraData.update(delta_model.extraData)

    def _handle_removals(self, items_to_remove: list[product_models.Product]) -> None:
        if not items_to_remove:
            return

        class_name = self.get_sqlalchemy_class().__name__

        try:
            with transaction():
                for product in items_to_remove:
                    product.gcuCompatibilityType = product_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
                logger.info(f"Committing deactivation for a batch of {len(items_to_remove)} {class_name}.")
            logger.info(f"Successfully deactivated batch of {len(items_to_remove)} {class_name}.")

        except sa_exc.IntegrityError as exc:
            logger.warning(f"Batch deactivation failed for {class_name}: {exc}. Retrying one by one.")
            db.session.rollback()
            self._deactivate_one_by_one(items_to_remove)

    def _deactivate_one_by_one(self, items_to_remove: list[product_models.Product]) -> None:
        class_name = self.get_sqlalchemy_class().__name__
        for product in items_to_remove:
            try:
                with transaction():
                    product.gcuCompatibilityType = product_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
            except sa_exc.IntegrityError as exc:
                logger.error(f"Failed to deactivate individual {class_name} (id: {product.id}): {exc}")

    def _handle_updates(self, items: list[tuple[str, bq_product_queries.ProductDeltaModel]]) -> None:
        if not items:
            return

        class_name = self.get_sqlalchemy_class().__name__
        eans = [delta_item.ean for _, delta_item in items if delta_item.ean]
        try:
            with transaction():
                objects_map = {
                    obj.ean: obj
                    for obj in db.session.query(self.get_sqlalchemy_class()).filter(
                        self.get_sqlalchemy_class().ean.in_(eans)
                    )
                }

                for _, delta_item in items:
                    if delta_item.ean in objects_map:
                        self.update(objects_map[delta_item.ean], delta_item)

                logger.info(f"Committing a batch of {len(items)} updates for {class_name}.")
        except sa_exc.IntegrityError as exc:
            logger.warning(f"Batch update failed for {class_name}: {exc}. Retrying one by one.")
            db.session.rollback()
            self._update_one_by_one(items)

    def _update_one_by_one(self, items: list[tuple[str, bq_product_queries.ProductDeltaModel]]) -> None:
        class_name = self.get_sqlalchemy_class().__name__
        for _, delta_item in items:
            if not delta_item.ean:
                continue
            try:
                with transaction():
                    sqlalchemy_obj = self.exists(delta_item)
                    if sqlalchemy_obj:
                        self.update(sqlalchemy_obj, delta_item)
            except sa_exc.IntegrityError as exc:
                logger.error(f"Failed to update individual {class_name} (ean: {delta_item.ean}): {exc}")
