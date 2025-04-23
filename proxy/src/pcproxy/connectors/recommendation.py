import logging
from typing import Any
from urllib.parse import urljoin

import aiohttp

from pcproxy import settings


logger = logging.getLogger(__name__)


class RecommendationException(Exception):
    pass


class RecommendationBackend:
    async def _request(self, method: str, path: str, params: dict, body: dict | None = None) -> dict:
        if method.lower() not in ("get", "post"):
            raise ValueError(f"Unexpected method: {method}")
        url = urljoin(settings.RECOMMENDATION_API_URL, path)
        params["token"] = settings.RECOMMENDATION_API_AUTHENTICATION_TOKEN

        arguments: dict[str, Any] = {
            "method": method.upper(),
            "url": url,
            # remove empty parameters
            "params": {k: v for k, v in params.items() if v is not None},
            "timeout": 30,
            # Calls to recommendation api are made with `ssl=False` because:
            # The certificates are google-managed and seen as self-signed.
            "ssl": False,
        }
        if method == "post":
            arguments["json"] = body
        async with aiohttp.ClientSession() as session:
            async with session.request(**arguments) as response:
                if response.status == 200:
                    return await response.json()
                logger.info(
                    "Got error from Recommendation API",
                    extra={
                        "code": response.status,
                        "content": await response.text(),
                    },
                )
                raise RecommendationException()

    async def get_similar_offers(self, offer_id: int, user_id: int | None, params: dict) -> dict:
        path = f"/similar_offers/{offer_id}"
        params["userId"] = user_id

        # FIXME (jmontagnat, 2025-04-22) Remove this block of code once the frontend has fixed their call to the endpoint with the correct inputs
        if params.get("categories"):
            if params.get("search_group_names"):
                params["search_group_names"].extend(params["categories"])
            else:
                params["search_group_names"] = params["categories"]
            params["categories"] = None

        return await self._request("get", path, params=params)

    async def get_playlist(self, user_id: int, params: dict, body: dict) -> dict:
        path = f"/playlist_recommendation/{user_id}"
        return await self._request("post", path, params=params, body=body)
