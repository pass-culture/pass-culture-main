import datetime
import enum
import html
import logging
import typing

from urllib3 import exceptions as urllib3_exceptions

import pcapi.core.offers.models as offers_models
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.repository as providers_repository
from pcapi import settings
from pcapi.core.categories import subcategories
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.utils import date as date_utils
from pcapi.utils import requests
from pcapi.utils.cache import get_from_cache
from pcapi.utils.csr import get_closest_csr


logger = logging.getLogger(__name__)


def get_jwt_token() -> str:
    TITELIVE_JWT_CACHE_KEY = "api:titelive_jwt:cache"
    TITELIVE_JWT_CACHE_TIMEOUT = 145  # 2 minutes and 25 seconds
    url = f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/{settings.TITELIVE_EPAGINE_API_USERNAME}/token"
    payload = {"password": settings.TITELIVE_EPAGINE_API_PASSWORD}

    def _get_new_jwt_token() -> str:
        try:
            response = requests.post(url, json=payload)
        except requests.exceptions.Timeout:
            raise
        except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
            logger.error(
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
                logger.error(
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
        logger.error(
            "Titelive get by ean 13: Network error",
            extra={
                "exception": e,
                "ean": ean13,
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
            if response.status_code == 404:
                log_func = logger.warning
            else:
                log_func = logger.error
            log_func(
                "Titelive get by ean 13: External error: %s",
                response.status_code,
                extra={
                    "alert": "Titelive error",
                    "ean": ean13,
                    "error_type": "http",
                    "status_code": response.status_code,
                    "request_type": "get-by-ean13",
                    "response_text": response.text,
                },
            )
            raise requests.ExternalAPIException(True, {"status_code": response.status_code})

    return response.json()


def get_by_ean_list(ean_list: set[str]) -> dict[str, typing.Any]:
    try:
        query_params = "|".join(ean_list)
        url = f"{settings.TITELIVE_EPAGINE_API_URL}/ean?in=ean={query_params}"
        headers = {"Content-Type": "application", "Authorization": "Bearer {}".format(get_jwt_token())}
        response = requests.get(url, headers=headers)

    except requests.exceptions.Timeout:
        raise
    except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
        logger.error(
            "Titelive get by ean list: Network error",
            extra={
                "exception": e,
                "alert": "Titelive error",
                "error_type": "network",
                "request_type": "get-by-ean-list",
            },
        )
        raise requests.ExternalAPIException(is_retryable=True) from e

    if not response.ok:
        if response.status_code == 404:
            raise offers_exceptions.TiteLiveAPINotExistingEAN()
        if 400 <= response.status_code < 500:
            if response.status_code == 404:
                log_func = logger.warning
            else:
                log_func = logger.error
            log_func(
                "Titelive get by ean list: External error: %s",
                response.status_code,
                extra={
                    "alert": "Titelive error",
                    "eans": ean_list,
                    "error_type": "http",
                    "status_code": response.status_code,
                    "request_type": "get-by-ean-list",
                    "response_text": response.text,
                },
            )
            raise requests.ExternalAPIException(True, {"status_code": response.status_code})

    return response.json()


class GtlIdError(Exception):
    """Exception when GTL is not found."""


def get_new_product_from_ean13(ean: str) -> typing.Tuple[offers_models.Product, dict]:
    json = get_by_ean13(ean)
    oeuvre = json["oeuvre"]
    article = oeuvre["article"][0]
    gtl_id = None

    if article and "gtl" in article and "first" in article["gtl"]:
        # this will reverse the position and take the highest gtl which is the most precise
        for key, gtl_from_api in sorted(list(article["gtl"]["first"].items()), reverse=True):
            gtl_id = gtl_from_api["code"].zfill(8)
            break

    if gtl_id is None:
        # EAN without GTL exist (DVD, ...), ex: 3597660004235
        logger.warning(
            "Titelive get_new_product_from_ean13: External error:",
            extra={
                "alert": "Titelive API no gtl_id",
                "error_type": "http",
                "ean": ean,
                "request_type": "get-new-product-from-ean13",
            },
        )
        raise GtlIdError(f"EAN {ean} does not have a titelive gtl_id")

    csr = get_closest_csr(gtl_id)

    provider = providers_repository.get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)

    product = offers_models.Product(
        lastProvider=provider,
        description=html.unescape(article["resume"]) if "resume" in article else None,
        name=html.unescape(oeuvre["titre"]) if len(oeuvre["titre"]) <= 140 else oeuvre["titre"][:139] + "…",
        ean=ean,
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        thumbCount=article.get("image", 0),  # 0 or 1
        extraData=offers_models.OfferExtraData(
            author=oeuvre.get("auteurs", ""),
            prix_livre=article["prix"],
            collection=article.get("collection"),
            comic_series=article.get("serie"),
            date_parution=(
                date_utils.parse_titelive_date_to_string(article.get("dateparution"))
                if "dateparution" in article
                else None
            ),
            distributeur=article["distributeur"],
            editeur=article["editeur"],
            num_in_collection=article.get("collection_no"),
            schoolbook=article["scolaire"] == "1",
            csr_id=csr["csr_id"] if csr else None,
            gtl_id=gtl_id,
            code_clil=article.get("code_clil"),
            # remove rayon when removing csr
            rayon=csr["label"] if csr else None,
        ),
    )

    return product, article


class TiteliveBase(enum.Enum):
    BOOK = "paper"
    MUSIC = "music"


MAX_RESULTS_PER_PAGE = 25


def search_products(titelive_base: TiteliveBase, modified_date: datetime.date, page_index: int) -> list[dict]:
    """
    Returns TiteLive works for which an article has been modified at modified_date.
    All the articles of an work are returned even if they have not been modified recently.

    Because TiteLive cannot query more than 20 000 articles, their pagination is only reliable if the search
    is done on a single day.
    """
    try:
        url = f"{settings.TITELIVE_EPAGINE_API_URL}/search"
        headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(get_jwt_token())}
        response = requests.get(
            url,
            headers=headers,
            params={
                "base": titelive_base.value,
                "nombre": MAX_RESULTS_PER_PAGE,
                "page": page_index,
                "tri": "datemodification",
                "tri_ordre": "asc",
                "dateminm": date_utils.format_date_to_french_locale(modified_date),
                "datemaxm": date_utils.format_date_to_french_locale(modified_date + datetime.timedelta(days=1)),
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

    products = response.json()["result"]
    return products


def download_titelive_image(image_url: str) -> bytes:
    try:
        response = requests.get(image_url)
    except (urllib3_exceptions.HTTPError, requests.exceptions.RequestException) as e:
        logger.error(
            "Titelive image: Network error",
            extra={"exception": e, "alert": "Titelive error", "error_type": "network", "request_type": "image"},
        )
        raise requests.ExternalAPIException(is_retryable=True) from e

    if not response.ok:
        logger.error(
            "Titelive image: External error %s",
            response.status_code,
            extra={
                "alert": "Titelive error",
                "error_type": "http",
                "status_code": response.status_code,
                "request_type": "image",
                "response_text": response.text,
            },
        )
        raise requests.ExternalAPIException(True, {"status_code": response.status_code})

    return response.content
