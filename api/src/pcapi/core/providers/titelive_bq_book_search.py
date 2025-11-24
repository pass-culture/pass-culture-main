import logging

import pcapi.core.offers.models as offers_models
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.connectors.big_query.queries.product import BigQueryTiteliveBookProductDeltaQuery
from pcapi.connectors.big_query.queries.product import BigQueryTiteliveBookProductModel
from pcapi.connectors.titelive import TiteliveBase
from pcapi.core.categories.subcategories import LIVRE_PAPIER
from pcapi.core.providers.titelive_book_search import get_book_format
from pcapi.core.providers.titelive_book_search import get_gtl_id
from pcapi.core.providers.titelive_book_search import get_ineligibility_reasons
from pcapi.core.providers.titelive_bq_sync_base import BigQuerySyncTemplate


logger = logging.getLogger(__name__)


class BigQueryTiteliveBookProductSync(BigQuerySyncTemplate[BigQueryTiteliveBookProductModel]):
    titelive_base = TiteliveBase.BOOK

    def get_query(self) -> BaseQuery:
        return BigQueryTiteliveBookProductDeltaQuery()

    def filter_batch(
        self, batch: tuple[BigQueryTiteliveBookProductModel, ...]
    ) -> tuple[list[BigQueryTiteliveBookProductModel], list[str]]:
        valid_products = []
        rejected_eans = []

        for bq_product in batch:
            reasons = get_ineligibility_reasons(bq_product, bq_product.titre)

            if reasons:
                if bq_product.ean in self.product_whitelist_eans:
                    logger.info(
                        "Skipping ineligibility: product is whitelisted.",
                        extra={"ean": bq_product.ean, "reasons": reasons},
                    )
                else:
                    rejected_eans.append(bq_product.ean)
                    logger.info("Rejecting product.", extra={"ean": bq_product.ean, "reasons": reasons})
                    continue

            valid_products.append(bq_product)

        return valid_products, rejected_eans

    def fill_product_specifics(
        self, product: offers_models.Product, bq_product: BigQueryTiteliveBookProductModel
    ) -> None:
        product.subcategoryId = LIVRE_PAPIER.id

        gtl_id = get_gtl_id(bq_product)
        extra_data = offers_models.OfferExtraData(
            author=", ".join(bq_product.auteurs_multi) if bq_product.auteurs_multi else None,
            bookFormat=get_book_format(bq_product.codesupport),
            date_parution=str(bq_product.dateparution) if bq_product.dateparution else None,
            editeur=bq_product.editeur,
            gtl_id=gtl_id,
            langueiso=bq_product.langueiso,
            prix_livre=str(bq_product.prix),
        )

        product.extraData = product.extraData or offers_models.OfferExtraData()
        product.extraData.update(extra_data)
