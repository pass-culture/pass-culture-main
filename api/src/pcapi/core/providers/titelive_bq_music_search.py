import logging
import typing

import pcapi.core.offers.models as offers_models
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.connectors.big_query.queries.product import BigQueryTiteliveMusicProductDeltaQuery
from pcapi.connectors.big_query.queries.product import BigQueryTiteliveMusicProductModel
from pcapi.connectors.titelive import TiteliveBase
from pcapi.core.providers.titelive_book_search import get_gtl_id
from pcapi.core.providers.titelive_bq_sync_base import BigQuerySyncTemplate
from pcapi.core.providers.titelive_music_search import is_music_codesupport_allowed
from pcapi.core.providers.titelive_music_search import parse_titelive_music_codesupport
from pcapi.core.providers.titelive_music_search import parse_titelive_music_genre


logger = logging.getLogger(__name__)


class BigQueryTiteliveMusicProductSync(BigQuerySyncTemplate[BigQueryTiteliveMusicProductModel]):
    titelive_base = TiteliveBase.MUSIC

    def get_query(self) -> BaseQuery:
        return BigQueryTiteliveMusicProductDeltaQuery()

    def filter_batch(
        self, batch: tuple[BigQueryTiteliveMusicProductModel, ...]
    ) -> tuple[list[BigQueryTiteliveMusicProductModel], list[str]]:
        valid_products = []
        rejected_eans = []

        for bq_product in batch:
            if not is_music_codesupport_allowed(bq_product.codesupport):
                if bq_product.ean in self.product_whitelist_eans:
                    logger.info(
                        "Allowing whitelisted music product",
                        extra={"ean": bq_product.ean, "support": bq_product.codesupport},
                    )
                else:
                    rejected_eans.append(bq_product.ean)
                    logger.info(
                        "Rejecting ineligible music support",
                        extra={"ean": bq_product.ean, "support": bq_product.codesupport},
                    )
                    continue

            valid_products.append(bq_product)

        return valid_products, rejected_eans

    def fill_product_specifics(
        self, product: offers_models.Product, bq_product: BigQueryTiteliveMusicProductModel
    ) -> None:
        product.subcategoryId = parse_titelive_music_codesupport(bq_product.codesupport).id

        gtl_id = get_gtl_id(bq_product)
        music_type, music_subtype = parse_titelive_music_genre(gtl_id)

        extra_data = offers_models.OfferExtraData(
            artist=bq_product.artiste,
            author=bq_product.compositeur,
            comment=bq_product.commentaire,
            contenu_explicite=str(bq_product.contenu_explicite),
            date_parution=str(bq_product.dateparution) if bq_product.dateparution else None,
            dispo=bq_product.dispo,
            distributeur=bq_product.distributeur,
            editeur=bq_product.editeur,
            gtl_id=gtl_id,
            musicSubType=str(music_subtype.code),
            musicType=str(music_type.code),
            music_label=bq_product.label,
            nb_galettes=bq_product.nb_galettes,
            performer=bq_product.interprete,
            prix_musique=str(bq_product.prix) if bq_product.prix is not None else None,
        )

        clean_extra_data = {key: value for key, value in extra_data.items() if value is not None}

        product.extraData = product.extraData or offers_models.OfferExtraData()
        product.extraData.update(typing.cast(offers_models.OfferExtraData, clean_extra_data))
