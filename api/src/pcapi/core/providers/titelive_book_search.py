import logging

import pydantic.v1 as pydantic

import pcapi.core.fraud.models as fraud_models
from pcapi.connectors.serialization.titelive_serializers import GenreTitelive
from pcapi.connectors.serialization.titelive_serializers import TiteLiveBookArticle
from pcapi.connectors.serialization.titelive_serializers import TiteLiveBookWork
from pcapi.connectors.titelive import TiteliveBase
from pcapi.connectors.titelive import get_by_ean_list
from pcapi.core.categories.subcategories import LIVRE_PAPIER
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import constants
from pcapi.models import db
from pcapi.utils.csr import get_closest_csr

from .titelive_api import TiteliveSearchTemplate
from .titelive_api import activate_newly_eligible_product_and_offers


logger = logging.getLogger(__name__)


class TiteliveBookSearch(TiteliveSearchTemplate[TiteLiveBookWork]):
    titelive_base = TiteliveBase.BOOK

    def __init__(self) -> None:
        super().__init__()
        self.product_whitelist_eans = {
            ean
            for (ean,) in db.session.query(fraud_models.ProductWhitelist)
            .with_entities(fraud_models.ProductWhitelist.ean)
            .all()
        }

    def deserialize_titelive_product(self, titelive_work: dict) -> TiteLiveBookWork:
        return pydantic.parse_obj_as(TiteLiveBookWork, titelive_work)

    def partition_allowed_products(
        self, titelive_product_page: list[TiteLiveBookWork]
    ) -> tuple[list[TiteLiveBookWork], list[str]]:
        non_allowed_eans = set()
        for work in titelive_product_page:
            article_ok = []
            for article in work.article:
                if self.is_book_article_allowed(article, work.titre):
                    article_ok.append(article)
                else:
                    non_allowed_eans.add(article.gencod)
            work.article = article_ok

        return titelive_product_page, list(non_allowed_eans)

    def upsert_titelive_result_in_dict(
        self, titelive_search_result: TiteLiveBookWork, products_by_ean: dict[str, offers_models.Product]
    ) -> dict[str, offers_models.Product]:
        title = self.truncate_string(titelive_search_result.titre)
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
            ean=article.gencod,
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
        product.ean = ean
        product.name = title
        product.subcategoryId = LIVRE_PAPIER.id

        activate_newly_eligible_product_and_offers(product)

        return product

    def is_book_article_allowed(self, article: TiteLiveBookArticle, title: str) -> bool:
        ineligibility_reasons = get_ineligibility_reasons(article, title)

        if not ineligibility_reasons:
            return True

        if article.gencod in self.product_whitelist_eans:
            logger.info(
                "Allowing ean=%s even if ineligible reason=%s as it is a whitelisted product",  # TODO called twice = logged twice
                article.gencod,
                ineligibility_reasons,
            )
            return True

        logger.info("Rejecting ineligible ean=%s because reason=%s", article.gencod, ineligibility_reasons)
        return False

    def get_product_info_from_search_response(self, titelive_json_response: list[dict]) -> list[TiteLiveBookWork]:
        eans_to_update = extract_eans_from_titelive_response(titelive_json_response)
        if not eans_to_update:
            return []
        return self.get_product_info_from_eans(eans_to_update)

    def get_product_info_from_eans(self, eans: set[str]) -> list[TiteLiveBookWork]:
        response = get_by_ean_list(eans)
        if "result" in response:
            result = response["result"]
        elif "oeuvre" in response:
            result = [response["oeuvre"]]
        else:
            return []

        works = []
        for work in result.values() if isinstance(result, dict) else result:
            try:
                works.append(self.deserialize_titelive_product(work))
            except pydantic.ValidationError as e:
                logger.error("failed to deserialize titelive response", extra={"work": work, "exc": e})
                continue

        return works


def extract_eans_from_titelive_response(json_response: list[dict]) -> set[str]:
    eans = set()
    for work in json_response:
        for article in work["article"].values():
            eans.add(article["gencod"])

    return eans


EMPTY_GTL = GenreTitelive(code="".zfill(8), libelle="Empty GTL")


def get_gtl_id(article: TiteLiveBookArticle) -> str:
    if not article.gtl:
        return EMPTY_GTL.code
    most_precise_genre = max(article.gtl.first.values(), key=lambda gtl: gtl.code)
    gtl_id = most_precise_genre
    return gtl_id.code


def get_ineligibility_reasons(article: TiteLiveBookArticle, title: str) -> list[str] | None:
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

    # ouvrage "lectorat 18+" (Pornographie / ultra-violence)
    if article.id_lectorat == constants.LECTORAT_EIGHTEEN_ID:
        reasons.append("pornography-or-violence")

    # Toeic or toefl
    if constants.TOEIC_TEXT in title or constants.TOEFL_TEXT in title:
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
    if gtl_level_01_code == constants.GTL_LEVEL_01_EXTRACURRICULAR:
        reasons.append("extracurricular")

    # Petite jeunesse (livres pour le bains, peluches, puzzles, etc...)
    gtl_level_02_code = gtl_id[2:4]
    if gtl_level_01_code == constants.GTL_LEVEL_01_YOUNG and gtl_level_02_code in [
        constants.GTL_LEVEL_02_BEFORE_3,
        constants.GTL_LEVEL_02_AFTER_3_AND_BEFORE_6,
    ]:
        reasons.append("small-young")

    # --- Default categorization ---
    if article.codesupport not in constants.TITELIVE_BOOK_SUPPORTS_BY_CODE:
        # If we find no known support code, the product is deemed ineligible
        reasons.append("no-known-codesupport")

    if article.codesupport and not constants.TITELIVE_BOOK_SUPPORTS_BY_CODE[article.codesupport]["is_allowed"]:
        reasons.append("uneligible-product-subcategory")

    return reasons


def get_book_format(codesupport: str | None) -> str | None:
    if codesupport is None:
        return None
    book_format = constants.TITELIVE_BOOK_SUPPORTS_BY_CODE[codesupport]["book_format"]
    return book_format.name if book_format else None


def build_book_extra_data(article: TiteLiveBookArticle, authors: list) -> offers_models.OfferExtraData:
    gtl_id = get_gtl_id(article)

    rayon = None
    csr_id = None
    if gtl_id != EMPTY_GTL.code:
        csr_label = get_closest_csr(gtl_id)
        if csr_label is not None:
            rayon = csr_label.get("label")
            csr_id = csr_label.get("csr_id")

    result = offers_models.OfferExtraData(
        author=", ".join(authors) if authors else None,
        bookFormat=get_book_format(article.codesupport),
        code_clil=article.code_clil,
        collection=article.collection,
        comment=article.commentaire,
        csr_id=csr_id,
        date_parution=str(article.dateparution) if article.dateparution else None,
        dispo_label=article.libelledispo,
        dispo=article.dispo,
        distributeur=article.distributeur,
        editeur=article.editeur,
        gtl_id=gtl_id,
        langue=article.langue,
        langueiso=article.langueiso,
        nb_pages=article.pages,
        num_in_collection=article.collection_no,
        prix_livre=article.prix,
        rayon=rayon,
        schoolbook=int(article.scolaire or 0) != 0,  # can be None
    )

    return result
