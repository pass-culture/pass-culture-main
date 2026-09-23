import logging
import warnings

from urllib3 import exceptions as urllib_execptions

from pcapi import settings
from pcapi.connectors.recommendation import models
from pcapi.connectors.recommendation.base import BaseRecommandationBackend
from pcapi.connectors.recommendation.exceptions import RecommendationApiException
from pcapi.connectors.recommendation.exceptions import RecommendationApiTimeoutException
from pcapi.core.users.models import User
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class HttpBackend(BaseRecommandationBackend):
    def _request(self, method: str, path: str, params: dict, body: dict | None = None) -> bytes:
        headers = {"X-API-Key": settings.RECOMMENDATION_API_AUTHENTICATION_TOKEN}
        url = "/".join((settings.RECOMMENDATION_API_URL.rstrip("/"), path.lstrip("/")))
        # Calls to recommendation api are made with `verify=False` because:
        # The certificates are google-managed and seen as self-signed.
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", urllib_execptions.InsecureRequestWarning)

                if method == "get":
                    response = requests.get(  # nosemgrep: python.requests.security.disabled-cert-validation.disabled-cert-validation
                        url,
                        params=params,
                        headers=headers,
                        disable_synchronous_retry=True,
                        verify=False,
                        log_info=False,
                    )
                elif method == "post":
                    response = requests.post(  # nosemgrep: python.requests.security.disabled-cert-validation.disabled-cert-validation
                        url,
                        params=params,
                        json=body,
                        headers=headers,
                        disable_synchronous_retry=True,
                        verify=False,
                        log_info=False,
                    )
                else:
                    raise ValueError(f"Unexpected method: {method}")

            response.raise_for_status()

        except requests.exceptions.Timeout:
            raise RecommendationApiTimeoutException()
        except requests.exceptions.RequestException as exc:
            logger.info("Got error from Recommendation API", extra={"exc": str(exc)}, exc_info=True)
            raise RecommendationApiException(str(exc)) from exc

        return response.content

    def get_similar_offers(
        self,
        offer_id: int,
        user: User | None,
        params: models.SimilarOffersRequestQuery,
    ) -> models.SimilarOffersResponse:
        path = f"/similar_offers/{offer_id}"
        params.user_id = str(user.id) if user else None
        raw = self._request("get", path, params=params.model_dump())

        return models.SimilarOffersResponse.model_validate(raw)

    def get_similar_artists(
        self,
        artist_id: str,
    ) -> models.SimilarArtistsResponse:
        path = f"/similar_artists/{artist_id}"
        raw = self._request("get", path, params={})

        return models.SimilarArtistsResponse.model_validate(raw)

    def get_playlist(
        self,
        user: User,
        params: models.PlaylistRequestQuery,
        body: models.PlaylistRequestBody,
    ) -> models.PlaylistResponse:
        path = f"/playlist_recommendation/{user.id}"
        raw = self._request("post", path, params=params.model_dump(), body=body.model_dump())

        return models.PlaylistResponse.model_validate(raw)
