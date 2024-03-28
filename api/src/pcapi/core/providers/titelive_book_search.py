import logging
import typing

import pydantic.v1 as pydantic

from pcapi.connectors.serialization.titelive_serializers import TiteLiveBookArticle
from pcapi.connectors.serialization.titelive_serializers import TiteLiveBookOeuvre
from pcapi.connectors.serialization.titelive_serializers import TiteliveProductSearchResponse
from pcapi.connectors.titelive import TiteliveBase
from pcapi.core.categories.subcategories_v2 import LIVRE_PAPIER
import pcapi.core.fraud.models as fraud_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.exceptions import NotUpdateProductOrOffers
from pcapi.core.providers import constants
from pcapi.utils.csr import get_closest_csr

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
        title = titelive_search_result.titre
        authors = titelive_search_result.auteurs_multi
        for article in titelive_search_result.article:
            ean = article.gencod
            product = products_by_ean.get(ean)
            if product is None:
                products_by_ean[ean] = self.create_product(article, title, authors)
            else:
                products_by_ean[ean] = self.update_product(article, title, authors, product)
        return products_by_ean

    def create_product(self, article: TiteLiveBookArticle, title: str, authors: list[str]) -> offers_models.Product:
        return offers_models.Product(
            description=article.resume,
            extraData=build_book_extra_data(article, authors),
            idAtProviders=article.gencod,
            lastProvider=self.provider,
            name=title,
            subcategoryId=LIVRE_PAPIER.id,
        )

    def update_product(
        self,
        article: TiteLiveBookArticle,
        title: str,
        authors: list[str],
        product: offers_models.Product,
    ) -> offers_models.Product:
        ean = article.gencod
        product.description = article.resume
        if product.extraData is None:
            product.extraData = offers_models.OfferExtraData()
        product.extraData.update(build_book_extra_data(article, authors))
        product.idAtProviders = ean
        product.name = title
        product.subcategoryId = LIVRE_PAPIER.id

        # If the product is updated to eligible, it is because the offers must be approved to become ineligible due to gcu
        is_product_newly_eligible = not product.isGcuCompatible
        if is_product_newly_eligible:
            product.isGcuCompatible = True
            try:
                offers_api.approves_provider_product_and_rejected_offers(ean)
            except NotUpdateProductOrOffers as exception:
                logger.error("Product with ean cannot be approved", extra={"ean": ean, "exc": str(exception)})

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

        # 1=disponible chez l'éditeur, 2=à paraître, 3=En réimpression, 4=indisponible,
        # 5=changement de distributeur, 6=épuisé, 7=manque sans date, 8=à
        # reparaître, 9=abandon de parution
        # if article.dispo #TODO CHECK AVEC LE PRODUIT

        logger.info("Rejecting ineligible ean=%s because reason=%s", article.gencod, ineligibility_reason)
        return False


def get_gtl_id(article: TiteLiveBookArticle) -> str:
    most_precise_genre = max(article.gtl.first.values(), key=lambda gtl: gtl.code)
    gtl_id = most_precise_genre
    return gtl_id


def get_ineligibility_reason(article: TiteLiveBookArticle, title: str) -> str | None:
    # Ouvrage avec pierres ou encens, jeux de société ou escape game en coffrets,
    # marchandisage : jouets, goodies, peluches, posters, papeterie, etc...
    if article.code_tva == constants.BASE_VAT:
        return "vat-20"

    gtl_id = get_gtl_id(article)
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


# def get_extra_data_from_infos(infos: dict) -> offers_models.OfferExtraData:
#    extra_data = offers_models.OfferExtraData()
#    extra_data["author"] = infos[INFO_KEYS["AUTEURS"]]
#    extra_data["ean"] = infos[INFO_KEYS["EAN13"]]
#    if infos[INFO_KEYS["GTL_ID"]]:
#        csr_label = get_closest_csr(infos[INFO_KEYS["GTL_ID"]])
#        extra_data["gtl_id"] = infos[INFO_KEYS["GTL_ID"]].zfill(8)
#        if csr_label is not None:
#            extra_data["rayon"] = csr_label.get("label")
#            extra_data["csr_id"] = csr_label.get("csr_id")
#    if infos[INFO_KEYS["CODE_CLIL"]]:
#        extra_data["code_clil"] = infos[INFO_KEYS["CODE_CLIL"]]
#    if infos[INFO_KEYS["INDICE_DEWEY"]] != "":
#        extra_data["dewey"] = infos[INFO_KEYS["INDICE_DEWEY"]]
#    extra_data["titelive_regroup"] = infos[INFO_KEYS["CODE_REGROUPEMENT"]]
#    extra_data["prix_livre"] = infos[INFO_KEYS["PRIX"]].replace(",", ".")
#    if infos[INFO_KEYS["IS_SCOLAIRE"]] == "1":
#        extra_data["schoolbook"] = True
#    if infos[INFO_KEYS["CLASSEMENT_TOP"]] != "":
#        extra_data["top"] = infos[INFO_KEYS["CLASSEMENT_TOP"]]
#    if infos[INFO_KEYS["COLLECTION"]] != "":
#        extra_data["collection"] = infos[INFO_KEYS["COLLECTION"]]
#    if infos[INFO_KEYS["NUM_IN_COLLECTION"]] != "":
#        extra_data["num_in_collection"] = infos[INFO_KEYS["NUM_IN_COLLECTION"]]
#    if infos[INFO_KEYS["COMMENTAIRE"]] != "":
#        extra_data["comment"] = trim_with_ellipsis(infos[INFO_KEYS["COMMENTAIRE"]], 92)
#    if infos[INFO_KEYS["EDITEUR"]] != "":
#        extra_data["editeur"] = infos[INFO_KEYS["EDITEUR"]]
#    if infos[INFO_KEYS["DATE_PARUTION"]] != "":
#        extra_data["date_parution"] = infos[INFO_KEYS["DATE_PARUTION"]]
#    if infos[INFO_KEYS["DISTRIBUTEUR"]] != "":
#        extra_data["distributeur"] = infos[INFO_KEYS["DISTRIBUTEUR"]]
#    return extra_data


def build_book_extra_data(article: TiteLiveBookArticle, authors: str) -> offers_models.OfferExtraData:

    gtl_id = get_gtl_id(article)
    if gtl_id:
        csr_label = get_closest_csr(gtl_id)
        if csr_label is not None:
            rayon = csr_label.get("label")
            csr_id = csr_label.get("csr_id")

    # kwargs = {...}
    # kwargs = {k: v for k, v in kwargs.items() if not v}
    # return offers_models.OfferExtraData(**kwargs)

    return offers_models.OfferExtraData(
        bookFormat=get_book_format(article.codesupport),
        author=",".join(authors),
        ean=article.gencod,
        gtl_id=gtl_id,
        rayon=rayon if rayon else None,
        csr_id=csr_id if csr_id else None,
        code_clil=article.code_clil,
        # titelive_regroup=article.code_regroupement, # TODO code non trouvé dans l'article depuis l'API
        prix_livre=article.prix,
        schoolbook=int(article.scolaire) != 0,  # TODO deserialize 0 and "0" correctly
        # top : champ non trouvé dans l'api rest
        collection=article.collection if article.collection else None,
        num_in_collection=article.collection_no if article.collection_no else None,
        commentaire=article.commentaire if article.commentaire else None,
        editeur=article.editeur if article.editeur else None,
        date_parution=str(article.dateparution) if article.dateparution else None,
        distributeur=article.distributeur if article.distributeur else None,
    )
