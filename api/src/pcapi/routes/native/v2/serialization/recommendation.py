from pcapi.connectors.recommendation import models
from pcapi.core.offers import models as offer_models
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel


class RecommendationApiParams(models.RecommendationApiParams, HttpBodyModel): ...


class SimilarOffersRequestQuery(models.SimilarOffersRequestQuery, HttpQueryParamsModel): ...


class SimilarOffersResponse(HttpBodyModel):
    offers: list[offer_models.Offer]


class PlaylistRequestQuery(models.PlaylistRequestQuery, HttpQueryParamsModel): ...


class PlaylistRequestBody(models.PlaylistRequestBody, HttpBodyModel): ...


class PlaylistResponse(HttpBodyModel):
    offers: list[offer_models.Offer]
