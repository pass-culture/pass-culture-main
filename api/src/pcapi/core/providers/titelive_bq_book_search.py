import logging

import pcapi.core.offers.models as offers_models
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.connectors.big_query.queries.product import BigQueryTiteliveBookProductDeltaQuery
from pcapi.connectors.big_query.queries.product import BigQueryTiteliveBookProductModel
from pcapi.connectors.big_query.queries.product import TiteLiveBookArticle
from pcapi.connectors.titelive import TiteliveBase
from pcapi.core.categories.subcategories import LIVRE_PAPIER
from pcapi.core.providers import constants
from pcapi.core.providers.titelive_bq_sync_base import EMPTY_GTL
from pcapi.core.providers.titelive_bq_sync_base import BigQuerySyncTemplate
from pcapi.core.providers.titelive_bq_sync_base import get_gtl_id


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


def get_ineligibility_reasons(
    article: TiteLiveBookArticle | BigQueryTiteliveBookProductModel, title: str
) -> list[str] | None:
    # Ouvrage avec pierres ou encens, jeux de société ou escape game en coffrets,
    # marchandisage : jouets, goodies, peluches, posters, papeterie, etc...
    reasons = []
    article_tva = float(article.taux_tva) if article.taux_tva else None
    if article_tva == float(constants.BASE_VAT):
        reasons.append("vat-20")

    if article_tva == float(constants.PAPER_PRESS_VAT) and article.codesupport == constants.PAPER_PRESS_SUPPORT_CODE:
        reasons.append("press")

    if article.codesupport == constants.CALENDAR_SUPPORT_CODE:
        reasons.append("calendar")

    if article.codesupport == constants.POSTER_SUPPORT_CODE:
        reasons.append("poster")

    if article.codesupport == constants.PAPER_CONSUMABLE_SUPPORT_CODE:
        reasons.append("paper-consumable")

    # Coffrets (contenant un produit + un petit livret)
    if article.codesupport == constants.BOX_SUPPORT_CODE:
        reasons.append("box")

    # Oracles contenant des jeux de tarot
    if article.codesupport == constants.OBJECT_SUPPORT_CODE:
        reasons.append("object")

    # Ouvrage "lectorat 18+" (Pornographie / ultra-violence)
    if article.id_lectorat == constants.LECTORAT_EIGHTEEN_ID:
        reasons.append("pornography-or-violence")

    # Toeic or toefl
    if constants.TOEIC_TEXT in title.lower() or constants.TOEFL_TEXT in title.lower():
        reasons.append("toeic-toefl")

    # --- GTL-based categorization ---
    gtl_id = get_gtl_id(article)
    if gtl_id == EMPTY_GTL.code:
        reasons.append("empty-gtl")

    gtl_level_01_code = gtl_id[:2]

    # ouvrage du rayon scolaire
    if gtl_level_01_code == constants.GTL_LEVEL_01_SCHOOL:
        reasons.append("school")

    # ouvrage du rayon parascolaire,
    # code de la route (méthode d'apprentissage + codes basiques), code nautique, code aviation, etc...
    if (
        gtl_level_01_code == constants.GTL_LEVEL_01_EXTRACURRICULAR
        or article.id_lectorat in constants.LEARNING_LECTORAT
    ):
        reasons.append("extracurricular")

    # Petite jeunesse (livres pour le bains, peluches, puzzles, etc...)
    gtl_level_02_code = gtl_id[2:4]
    if (
        gtl_level_01_code == constants.GTL_LEVEL_01_YOUNG
        and gtl_level_02_code
        in [
            constants.GTL_LEVEL_02_BEFORE_3,
            constants.GTL_LEVEL_02_AFTER_3_AND_BEFORE_6,
        ]
    ) or article.id_lectorat in constants.UNDER_SIX_LECTORAT:
        reasons.append("small-young")

    # --- Default categorization ---
    if article.codesupport not in constants.TITELIVE_BOOK_SUPPORTS_BY_CODE:
        # If we find no known support code, the product is deemed ineligible
        reasons.append("no-known-codesupport")

    if article.codesupport:
        support_info = constants.TITELIVE_BOOK_SUPPORTS_BY_CODE.get(article.codesupport)
        if not support_info:
            logger.error(
                "Unknown Titelive support code found", extra={"codesupport": article.codesupport, "ean": article.gencod}
            )
            reasons.append("unknown-codesupport")
        elif not support_info["is_allowed"]:
            reasons.append("uneligible-product-subcategory")

    return reasons


def get_book_format(codesupport: str | None) -> str | None:
    if codesupport is None:
        return None
    book_format = constants.TITELIVE_BOOK_SUPPORTS_BY_CODE[codesupport]["book_format"]
    return book_format.name if book_format else None
