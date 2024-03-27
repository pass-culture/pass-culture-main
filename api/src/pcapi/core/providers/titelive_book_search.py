import logging
import typing

import pydantic.v1 as pydantic

from pcapi.connectors.serialization.titelive_serializers import TiteLiveBookArticle
from pcapi.connectors.serialization.titelive_serializers import TiteLiveBookOeuvre
from pcapi.connectors.serialization.titelive_serializers import TiteliveProductSearchResponse
from pcapi.connectors.titelive import TiteliveBase
import pcapi.core.fraud.models as fraud_models
from pcapi.core.offers import moedels as offers_models
from pcapi.core.providers import constants

from .titelive_api import TiteliveSearch


logger = logging.getLogger(__name__)


class TiteliveBookSearch(TiteliveSearch[TiteLiveBookOeuvre]):
    titelive_base = TiteliveBase.BOOK

    def __init__(self):
        self.product_whitelist_eans = {
            ean for ean, in fraud_models.ProductWhitelist.query.with_entities(fraud_models.ProductWhitelist.ean).all()
        }

    def deserialize_titelive_search_json(
        self, titelive_json_response: dict[str, typing.Any]
    ) -> TiteliveProductSearchResponse[TiteLiveBookOeuvre]:
        return pydantic.parse_obj_as(TiteliveProductSearchResponse[TiteLiveBookOeuvre], titelive_json_response)

    def filter_allowed_products(
        self, titelive_product_page: TiteliveProductSearchResponse[TiteLiveBookOeuvre]
    ) -> TiteliveProductSearchResponse[TiteLiveBookOeuvre]:
        for oeuvre in titelive_product_page.result:
            oeuvre.article = [
                article for article in oeuvre.article if self.is_book_article_allowed(article, oeuvre.titre)
            ]
        return titelive_product_page

    def get_not_allowed_eans(
        self, titelive_product_page: TiteliveProductSearchResponse[TiteLiveBookOeuvre]
    ) -> list[str]:
        not_cgu_compliant_eans = []
        for oeuvre in titelive_product_page.result:
            not_cgu_compliant_eans += [
                article.gencod for article in oeuvre.article if not self.is_book_article_allowed(article, oeuvre.titre)
            ]
        return not_cgu_compliant_eans

    def upsert_titelive_result_in_dict(
        self, titelive_search_result: TiteLiveBookOeuvre, products_by_ean: dict[str, offers_models.Product]
    ) -> dict[str, offers_models.Product]:
        for article in titelive_search_result.article:
            ean = article.gencod
            product = products_by_ean.get(ean)
            if product is None:
                products_by_ean[ean] = self.create_product(article)
            else:
                products_by_ean[ean] = self.update_product(article, product)

        return products_by_ean

    def create_product(
        self, article: TiteLiveBookArticle, common_article_fields: CommonMusicArticleFields
    ) -> offers_models.Product:
        return offers_models.Product(
            description=article.resume,
            extraData=build_music_extra_data(article, common_article_fields),
            idAtProviders=article.gencod,
            lastProvider=self.provider,
            name=common_article_fields["titre"],
            subcategoryId=parse_titelive_music_codesupport(article.codesupport).id,
        )

    def update_product(
        self,
        article: TiteLiveBookArticle,
        common_article_fields: CommonMusicArticleFields,
        product: offers_models.Product,
    ) -> offers_models.Product:
        product.description = article.resume
        if product.extraData is None:
            product.extraData = offers_models.OfferExtraData()
        product.extraData.update(build_music_extra_data(article, common_article_fields))
        product.idAtProviders = article.gencod
        product.name = common_article_fields["titre"]
        product.subcategoryId = parse_titelive_music_codesupport(article.codesupport).id

        return product

    def is_book_article_allowed(self, article: TiteLiveBookArticle, title: str) -> bool:
        ineligibility_reason = get_ineligibility_reason(article, title)

        if not ineligibility_reason:
            return True

        if article.gencod in self.product_whitelist_eans:
            logger.info(
                "Allowing ean=%s even if ineligible reason=%s as it is a whitelisted product",  # TODO called twice = logged twice
                article.gencod,
                ineligibility_reason,
            )
            return True

        logger.info("Rejecting ineligible ean=%s because reason=%s", article.gencod, ineligibility_reason)
        return False


def get_ineligibility_reason(article: TiteLiveBookArticle, title: str) -> str | None:
    # Ouvrage avec pierres ou encens, jeux de société ou escape game en coffrets,
    # marchandisage : jouets, goodies, peluches, posters, papeterie, etc...
    if article.code_tva == constants.BASE_VAT:
        return "vat-20"

    most_precise_genre = max(article.gtl.first.values(), key=lambda gtl: gtl.code)
    gtl_id = most_precise_genre
    gtl_level_01_code = gtl_id[:2]

    # ouvrage du rayon scolaire
    if gtl_level_01_code == constants.GTL_LEVEL_01_SCHOOL:
        return "school"

    # ouvrage du rayon parascolaire,
    # code de la route (méthode d'apprentissage + codes basiques), code nautique, code aviation, etc...
    if gtl_level_01_code == constants.GTL_LEVEL_01_EXTRACURRICULAR:
        return "extracurricular"

    if article.codesupport == constants.CALENDAR_SUPPORT_CODE:
        return "calendar"

    if article.codesupport == constants.POSTER_SUPPORT_CODE:
        return "poster"

    if article.codesupport == constants.PAPER_CONSUMABLE_SUPPORT_CODE:
        return "paper-consumable"

    # Coffrets (contenant un produit + un petit livret)
    if article.codesupport == constants.BOX_SUPPORT_CODE:
        return "box"

    # Oracles contenant des jeux de tarot
    if article.codesupport == constants.OBJECT_SUPPORT_CODE:
        return "object"

    # ouvrage "lectorat 18+" (Pornographie / ultra-violence)
    if article.id_lectorat == constants.LECTORAT_EIGHTEEN_ID:
        return "pornography-or-violence"

    # Petite jeunesse (livres pour le bains, peluches, puzzles, etc...)
    gtl_level_02_code = gtl_id[2:4]
    if gtl_level_01_code == constants.GTL_LEVEL_01_YOUNG and gtl_level_02_code in [
        constants.GTL_LEVEL_02_BEFORE_3,
        constants.GTL_LEVEL_02_AFTER_3_AND_BEFORE_6,
    ]:
        return "small-young"

    # Toeic or toefl
    if constants.TOEIC_TEXT in title or constants.TOEFL_TEXT in title:
        return "toeic-toefl"

    if article.code_tva == constants.PAPER_PRESS_VAT and article.codesupport == constants.PAPER_PRESS_SUPPORT_CODE:
        return "press"

    if not constants.TITELIVE_MUSIC_SUPPORTS_BY_CODE[article.codesupport].get("is_allowed"):
        return "uneligible-product-subcategory"

    return None


# def get_book_format(codesupport: str) -> str | None:
#     match codesupport:
#         case BD ->
def get_book_format(codesupport: str) -> offers_models.BookFormat | None:
    return constants.TITELIVE_MUSIC_SUPPORTS_BY_CODE[codesupport].get("book_format")
