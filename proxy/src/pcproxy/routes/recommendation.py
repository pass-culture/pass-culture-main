import asyncio
from typing import Annotated

import fastapi

from pcproxy.connectors.recommendation import RecommendationBackend
from pcproxy.connectors.recommendation import RecommendationException
from pcproxy.main import app
from pcproxy.serializers import recommendation as serializers
from pcproxy.serializers.error import SimpleError
from pcproxy.utils.jwt import JWTUserId


@app.get("/native/v1/recommendation/similar_offers/{offer_id}")
async def similar_offers(
    offer_id: int,
    query: Annotated[serializers.SimilarOffersRequestQuery, fastapi.Query()],
    user_id: Annotated[int | None, fastapi.Depends(JWTUserId)],
    response: fastapi.Response,
) -> serializers.SimilarOffersResponse | SimpleError:
    try:
        result = await RecommendationBackend().get_similar_offers(
            offer_id=offer_id,
            user_id=user_id,
            params=query.dict(),
        )
    except asyncio.TimeoutError:
        response.status_code = fastapi.status.HTTP_504_GATEWAY_TIMEOUT
        return SimpleError(code="RECOMMENDATION_API_TIMEOUT")
    except RecommendationException:
        response.status_code = fastapi.status.HTTP_502_BAD_GATEWAY
        return SimpleError(code="RECOMMENDATION_API_ERROR")
    return serializers.SimilarOffersResponse(**result)


@app.post("/native/v1/recommendation/playlist")
async def playlist(
    query: Annotated[serializers.PlaylistRequestQuery, fastapi.Query()],
    body: serializers.PlaylistRequestBody,
    user_id: Annotated[int | None, fastapi.Depends(JWTUserId)],
    response: fastapi.Response,
) -> serializers.PlaylistResponse | SimpleError:
    if not user_id:
        response.status_code = fastapi.status.HTTP_401_UNAUTHORIZED
        return SimpleError(code="BAD_JWT")
    try:
        result = await RecommendationBackend().get_playlist(
            user_id=user_id,
            params=query.dict(),
            body=body.dict(),
        )
    except asyncio.TimeoutError:
        response.status_code = fastapi.status.HTTP_504_GATEWAY_TIMEOUT
        return SimpleError(code="RECOMMENDATION_API_TIMEOUT")
    except RecommendationException:
        response.status_code = fastapi.status.HTTP_502_BAD_GATEWAY
        return SimpleError(code="RECOMMENDATION_API_ERROR")

    if not result:
        return serializers.PlaylistResponse(playlistRecommendedOffers=[], params=serializers.RecommendationApiParams())
    return serializers.PlaylistResponse(**result)
