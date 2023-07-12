import html
import logging
import typing

from urllib3 import exceptions as urllib3_exceptions

from pcapi import settings
from pcapi.core import logging as core_logging
from pcapi.core.categories import subcategories
from pcapi.core.offers import exceptions as offers_exceptions
import pcapi.core.offers.models as offers_models
from pcapi.domain.titelive import read_things_date
from pcapi.utils import requests
from pcapi.utils.cache import get_from_cache
from pcapi.utils.csr import get_closest_csr


logger = logging.getLogger(__name__)


def get_jwt_token() -> str:
    TITELIVE_JWT_CACHE_KEY = "api:titelive_jwt:cache"
    TITELIVE_JWT_CACHE_TIMEOUT = 5 * 60  # 5 minutes
    url = f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/{settings.TITELIVE_EPAGINE_API_USERNAME}/token"
    payload = {"password": settings.TITELIVE_EPAGINE_API_PASSWORD}

    def _get_new_jwt_token() -> str:
        try:
            response = requests.post(url, json=payload)
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
    url = f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{ean13}"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer {}".format(get_jwt_token())}

    try:
        response = requests.get(url, headers=headers)
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
