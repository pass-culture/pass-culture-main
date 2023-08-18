import abc
import datetime
import enum
import html
import logging
import typing

import pydantic
from urllib3 import exceptions as urllib3_exceptions

from pcapi import repository
from pcapi import settings
from pcapi.core import logging as core_logging
from pcapi.core.categories import subcategories
from pcapi.core.offers import exceptions as offers_exceptions
import pcapi.core.offers.models as offers_models
from pcapi.domain.music_types import MUSIC_SUB_TYPES_BY_SLUG
from pcapi.domain.music_types import MUSIC_TYPES_BY_SLUG
from pcapi.domain.music_types import OTHER_SHOW_TYPE_SLUG
from pcapi.domain.titelive import read_things_date
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils import requests
from pcapi.utils.cache import get_from_cache
from pcapi.utils.csr import get_closest_csr

from .serialization.titelive_serializers import GenreTitelive
from .serialization.titelive_serializers import TiteliveMusicArticle
from .serialization.titelive_serializers import TiteliveMusicOeuvre
from .serialization.titelive_serializers import TiteliveProductSearchResponse
from .serialization.titelive_serializers import TiteliveSearchResultType


logger = logging.getLogger(__name__)


def get_jwt_token() -> str:
    TITELIVE_JWT_CACHE_KEY = "api:titelive_jwt:cache"
    TITELIVE_JWT_CACHE_TIMEOUT = 5 * 60  # 5 minutes
    url = f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/{settings.TITELIVE_EPAGINE_API_USERNAME}/token"
    payload = {"password": settings.TITELIVE_EPAGINE_API_PASSWORD}

    def _get_new_jwt_token() -> str:
        try:
            response = requests.post(url, json=payload)
        except requests.exceptions.Timeout:
            raise
        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
            core_logging.log_for_supervision(
                logger,
                logging.ERROR,
                "Titelive get jwt: Network error",
                extra={
                    "exception": e,
                    "alert": "Titelive error",
                    "error_type": "network",
                    "request_type": "get-jwt",
                },
            )
            raise requests.ExternalAPIException(is_retryable=True) from e

        if not response.ok:
            if 400 <= response.status_code < 500:
                core_logging.log_for_supervision(
                    logger,
                    logging.ERROR,
                    "Titelive get jwt: External error: %s",
                    response.status_code,
                    extra={
                        "alert": "Titelive error",
                        "error_type": "http",
                        "status_code": response.status_code,
                        "request_type": "get-jwt",
                        "response_text": response.text,
                    },
                )
                raise requests.ExternalAPIException(True, {"status_code": response.status_code})

        return response.json()["token"]

    jwt_token = typing.cast(
        str,
        get_from_cache(
            key_template=TITELIVE_JWT_CACHE_KEY,
            retriever=_get_new_jwt_token,
            expire=TITELIVE_JWT_CACHE_TIMEOUT,
            return_type=str,
        ),
    )

    return jwt_token


def get_by_ean13(ean13: str) -> dict[str, typing.Any]:
    try:
        url = f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{ean13}"
        headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(get_jwt_token())}
        response = requests.get(url, headers=headers)
    except requests.exceptions.Timeout:
        raise
    except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
        core_logging.log_for_supervision(
            logger,
            logging.ERROR,
            "Titelive get by ean 13: Network error",
            extra={
                "exception": e,
                "alert": "Titelive error",
                "error_type": "network",
                "request_type": "get-by-ean13",
            },
        )
        raise requests.ExternalAPIException(is_retryable=True) from e

    if not response.ok:
        if response.status_code == 404:
            raise offers_exceptions.TiteLiveAPINotExistingEAN()
        if 400 <= response.status_code < 500:
            core_logging.log_for_supervision(
                logger,
                logging.WARNING if response.status_code == 404 else logging.ERROR,
                "Titelive get by ean 13: External error: %s",
                response.status_code,
                extra={
                    "alert": "Titelive error",
                    "error_type": "http",
                    "status_code": response.status_code,
                    "request_type": "get-by-ean13",
                    "response_text": response.text,
                },
            )
            raise requests.ExternalAPIException(True, {"status_code": response.status_code})

    return response.json()


class GtlIdError(Exception):
    """Exception when GTL is not found."""


def get_new_product_from_ean13(ean: str) -> offers_models.Product:
    json = get_by_ean13(ean)
    oeuvre = json["oeuvre"]
    article = oeuvre["article"][0]
    gtl_id = None

    if article and "gtl" in article and "first" in article["gtl"]:
        # this will reverse the position and take the highest gtl which is the most precise
        for key, gtl_from_api in sorted(  # pylint:disable=unused-variable
            list(article["gtl"]["first"].items()), reverse=True
        ):
            gtl_id = gtl_from_api["code"].zfill(8)
            break

    if gtl_id is None:
        # EAN without GTL exist (DVD, ...), ex: 3597660004235
        core_logging.log_for_supervision(
            logger,
            logging.ERROR,
            "Titelive get_new_product_from_ean13: External error: %s",
            extra={
                "alert": "Titelive API no gtl_id",
                "error_type": "http",
                "ean": ean,
                "request_type": "get-new-product-from-ean13",
            },
        )
        raise GtlIdError(f"EAN {ean} does not have a titelive gtl_id")

    csr = get_closest_csr(gtl_id)

    return offers_models.Product(
        idAtProviders=ean,
        description=html.unescape(article["resume"]),
        name=html.unescape(oeuvre["titre"]),
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        thumbCount=article["image"],  # 0 or 1
        extraData=offers_models.OfferExtraData(
            author=oeuvre["auteurs"],
            ean=ean,
            prix_livre=article["prix"],
            collection=article["collection"] if "collection" in article else None,
            comic_series=article["serie"],
            date_parution=read_things_date(article["dateparution"]) if "dateparution" in article else None,
            distributeur=article["distributeur"],
            editeur=article["editeur"],
            num_in_collection=article["collection_no"] if "collection_no" in article else None,
            schoolbook=article["scolaire"] == "1",
            csr_id=csr["csr_id"] if csr else None,
            gtl_id=gtl_id,
            code_clil=article["code_clil"] if "code_clil" in article else None,
            # remove rayon when removing csr
            rayon=csr["label"] if csr else None,
        ),
    )


class TiteliveBase(enum.Enum):
    BOOK = "paper"
    MUSIC = "music"


class TiteliveSearch(abc.ABC, typing.Generic[TiteliveSearchResultType]):
    max_results_per_page = 25
    titelive_base: TiteliveBase

    def synchronize_products(self, from_date: datetime.date) -> None:
        products_to_update_pages = self.get_updated_titelive_pages(from_date)
        for titelive_page in products_to_update_pages:
            with repository.transaction():
                updated_products = self.upsert_titelive_page(titelive_page)
                db.session.add_all(updated_products)

    def get_updated_titelive_pages(
        self,
        from_date: datetime.date,
    ) -> typing.Iterator[TiteliveProductSearchResponse[TiteliveSearchResultType]]:
        page_index = 1
        titelive_product_page = None
        while titelive_product_page is None or len(titelive_product_page.result) == self.max_results_per_page:
            titelive_json_response = self.get_titelive_search_json(from_date, page_index)
            titelive_product_page = self.deserialize_titelive_search_json(titelive_json_response)
            allowed_product_page = self.filter_allowed_products(titelive_product_page)
            yield allowed_product_page
            page_index += 1

    def get_titelive_search_json(self, from_date: datetime.date, page_index: int) -> dict[str, typing.Any]:
        try:
            url = f"{settings.TITELIVE_EPAGINE_API_URL}/search"
            headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(get_jwt_token())}
            response = requests.get(
                url,
                headers=headers,
                params={
                    "base": self.titelive_base.value,
                    "nombre": self.max_results_per_page,
                    "page": page_index,
                    "tri": "datemodification",
                    "tri_ordre": "asc",
                    "dateminm": date_utils.format_date_to_french_locale(from_date),
                },
            )
        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
            logger.error(
                "Titelive search: Network error",
                extra={
                    "exception": e,
                    "alert": "Titelive error",
                    "error_type": "network",
                    "request_type": "search",
                },
            )
            raise requests.ExternalAPIException(is_retryable=True) from e

        if not response.ok:
            logger.error(
                "Titelive search: External error %s",
                response.status_code,
                extra={
                    "alert": "Titelive error",
                    "error_type": "http",
                    "status_code": response.status_code,
                    "request_type": "search",
                    "response_text": response.text,
                },
            )
            raise requests.ExternalAPIException(True, {"status_code": response.status_code})

        return response.json()

    @abc.abstractmethod
    def deserialize_titelive_search_json(
        self, titelive_json_response: dict[str, typing.Any]
    ) -> TiteliveProductSearchResponse[TiteliveSearchResultType]:
        raise NotImplementedError()

    def filter_allowed_products(
        self,
        titelive_product_page: TiteliveProductSearchResponse[TiteliveSearchResultType],
    ) -> TiteliveProductSearchResponse[TiteliveSearchResultType]:
        return titelive_product_page

    def upsert_titelive_page(
        self,
        titelive_page: TiteliveProductSearchResponse[TiteliveSearchResultType],
    ) -> list[offers_models.Product]:
        titelive_results = titelive_page.result
        titelive_eans = [article.gencod for result in titelive_results for article in result.article]

        products = offers_models.Product.query.filter(
            offers_models.Product.extraData["ean"].astext.in_(titelive_eans)
        ).all()
        products_by_ean: dict[str, offers_models.Product] = {p.extraData["ean"]: p for p in products}
        for titelive_search_result in titelive_results:
            products_by_ean = self.upsert_titelive_result_in_dict(titelive_search_result, products_by_ean)

        return list(products_by_ean.values())

    @abc.abstractmethod
    def upsert_titelive_result_in_dict(
        self, titelive_search_result: TiteliveSearchResultType, products_by_ean: dict[str, offers_models.Product]
    ) -> dict[str, offers_models.Product]:
        raise NotImplementedError()


class TiteliveMusicSearch(TiteliveSearch[TiteliveMusicOeuvre]):
    titelive_base = TiteliveBase.MUSIC

    def deserialize_titelive_search_json(
        self, titelive_json_response: dict[str, typing.Any]
    ) -> TiteliveProductSearchResponse[TiteliveMusicOeuvre]:
        return pydantic.parse_obj_as(TiteliveProductSearchResponse[TiteliveMusicOeuvre], titelive_json_response)

    def upsert_titelive_result_in_dict(
        self, titelive_search_result: TiteliveMusicOeuvre, products_by_ean: dict[str, offers_models.Product]
    ) -> dict[str, offers_models.Product]:
        title = titelive_search_result.titre
        genre_titelive = self.get_genre_titelive(titelive_search_result)
        for article in titelive_search_result.article:
            ean = article.gencod
            product = products_by_ean.get(ean)
            if product is None:
                products_by_ean[ean] = self.create_product(article, title, genre_titelive)
            else:
                products_by_ean[ean] = self.update_product(article, title, genre_titelive, product)

        return products_by_ean

    def get_genre_titelive(self, titelive_search_result: TiteliveMusicOeuvre) -> GenreTitelive | None:
        titelive_gtl = next(
            (article.gtl for article in titelive_search_result.article if article.gtl is not None), None
        )
        if not titelive_gtl:
            logger.warning("Genre Titelive not found for music %s", titelive_search_result.titre)
            return None

        most_precise_genre = max(titelive_gtl.first.values(), key=lambda g: g.code)
        return most_precise_genre

    def create_product(
        self, article: TiteliveMusicArticle, title: str, genre: GenreTitelive | None
    ) -> offers_models.Product:
        return offers_models.Product(
            description=article.resume,
            extraData=self.build_music_extra_data(article, genre),
            idAtProviders=article.gencod,
            name=title,
            subcategoryId=self.parse_titelive_product_format(article.codesupport),
        )

    def update_product(
        self, article: TiteliveMusicArticle, title: str, genre: GenreTitelive | None, product: offers_models.Product
    ) -> offers_models.Product:
        product.description = article.resume
        if product.extraData is None:
            product.extraData = offers_models.OfferExtraData()
        product.extraData.update(self.build_music_extra_data(article, genre))
        product.idAtProviders = article.gencod
        product.name = title
        product.subcategoryId = self.parse_titelive_product_format(article.codesupport)

        return product

    def build_music_extra_data(
        self, article: TiteliveMusicArticle, genre: GenreTitelive | None
    ) -> offers_models.OfferExtraData:
        gtl_id = genre.code.zfill(8) if genre else None
        music_type_id, music_subtype_id = self.parse_titelive_music_genre(genre)

        return offers_models.OfferExtraData(
            artist=article.artiste,
            author=article.compositeur,
            comment=article.commentaire,
            date_parution=article.dateparution.isoformat() if article.dateparution else None,
            disponibility=article.libelledispo,
            distributeur=article.distributeur,
            ean=article.gencod,
            editeur=article.editeur,
            gtl_id=gtl_id,
            music_label=article.label,
            musicSubType=str(music_subtype_id),
            musicType=str(music_type_id),
            nb_galettes=article.nb_galettes,
            performer=article.interprete,
        )

    def parse_titelive_music_genre(self, genre: GenreTitelive | None) -> tuple[int, int]:
        return (
            MUSIC_TYPES_BY_SLUG[OTHER_SHOW_TYPE_SLUG].code,
            MUSIC_SUB_TYPES_BY_SLUG[OTHER_SHOW_TYPE_SLUG].code,
        )

    def parse_titelive_product_format(self, codesupport: str) -> str:
        return subcategories.SUPPORT_PHYSIQUE_MUSIQUE.id
