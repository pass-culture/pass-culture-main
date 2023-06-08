import logging

from requests.exceptions import RequestException

from pcapi.core.providers.exceptions import ConnexionToProviderApiFailed
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class ProviderAPIException(Exception):
    status_code: int

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


REQUEST_TIMEOUT_FOR_PROVIDERS_IN_SECOND = 60


class ProviderAPI:
    def __init__(self, api_url: str, name: str, authentication_token: str = None):
        self.api_url = api_url
        self.name = name
        self.authentication_token = authentication_token

    def stocks(
        self, siret: str, last_processed_reference: str = "", modified_since: str = "", limit: int = 1000
    ) -> dict:
        api_url = self._build_local_provider_url(siret)
        params = self._build_local_provider_params(last_processed_reference, modified_since, limit)
        headers = {}

        if self.authentication_token is not None:
            headers = {"Authorization": f"Basic {self.authentication_token}"}

        response = requests.get(
            url=api_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT_FOR_PROVIDERS_IN_SECOND
        )

        if response.status_code != 200:
            raise ProviderAPIException(
                f"Error {response.status_code} when getting {self.name} stocks for SIRET: {siret}", response.status_code
            )

        if not response.content:
            return {}

        return response.json()

    def validated_stocks(
        self,
        siret: str,
        last_processed_reference: str = "",
        modified_since: str = "",
        limit: int = 1000,
    ) -> dict:
        api_responses = self.stocks(siret, last_processed_reference, modified_since, limit)
        stock_responses = api_responses.get("stocks", [])
        validated_stock_responses = []
        for stock_response in stock_responses:
            if "ref" not in stock_response:
                logger.error(
                    "[%s SYNC] missing ref key in response",
                    self.name,
                    extra={"stock": stock_response, "siret": siret},
                )
                continue

            stock_response_ref = stock_response["ref"]
            if "available" not in stock_response:
                logger.error(
                    "[%s SYNC] missing available key in response with ref %s",
                    self.name,
                    stock_response_ref,
                    extra={"stock": stock_response, "siret": siret},
                )
                continue

            if stock_response["available"] < 0:
                logger.error(
                    "[%s SYNC] invalid available value %s in response with ref %s",
                    self.name,
                    stock_response["available"],
                    stock_response_ref,
                    extra={"stock": stock_response, "siret": siret},
                )
                continue

            if stock_response.get("price", None) is None:
                logger.error(
                    "[%s SYNC] missing price in response with ref %s",
                    self.name,
                    stock_response_ref,
                    extra={"stock": stock_response, "siret": siret},
                )
                continue

            validated_stock_responses.append(stock_response)

        api_responses["stocks"] = validated_stock_responses
        batch_log_size = 1_000
        if not validated_stock_responses:
            logger.info("Got no stocks from Provider API", extra={"siret": siret})
        for i in range(0, len(validated_stock_responses), batch_log_size):
            log = f"Got stocks from Provider API (partial log: one log per batch of {batch_log_size})"
            logger.info(
                log,
                extra={
                    "stocks": validated_stock_responses[i : i + batch_log_size],
                    "siret": siret,
                },
            )
        return api_responses

    def is_siret_registered(self, siret: str) -> bool:
        api_url = self._build_local_provider_url(siret)
        headers = {}

        if self.authentication_token is not None:
            headers = {"Authorization": f"Basic {self.authentication_token}"}

        try:
            response = requests.get(url=api_url, headers=headers, timeout=REQUEST_TIMEOUT_FOR_PROVIDERS_IN_SECOND)
        except RequestException as error:
            extra_infos = {"siret": siret, "api_url": self.api_url, "error": str(error)}
            logger.exception("[PROVIDER] request failed", extra=extra_infos)
            raise ConnexionToProviderApiFailed

        return response.status_code == 200

    def _build_local_provider_url(self, siret: str) -> str:
        return f"{self.api_url}/{siret}"

    def _build_local_provider_params(self, last_processed_isbn: str, modified_since: str, limit: int) -> dict:
        params = {"limit": str(limit)}

        if last_processed_isbn:
            params["after"] = last_processed_isbn
        if modified_since:
            params["modifiedSince"] = modified_since

        return params
