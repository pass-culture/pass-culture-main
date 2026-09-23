from pcapi import settings
from pcapi.connectors.recommendation import models
from pcapi.core.users import models as users_models
from pcapi.utils import module_loading

from .base import BaseRecommandationBackend


def _get_backend() -> BaseRecommandationBackend:
    backend_class = module_loading.import_string(settings.RECOMMENDATION_BACKEND)
    return backend_class()


def get_similar_offers(
    offer_id: int,
    user: users_models.User | None = None,
    params: dict | None = None,
) -> models.SimilarOffersResponse:
    backend = _get_backend()
    if params:
        query_params = models.SimilarOffersRequestQuery.model_validate(params)
    else:
        query_params = models.SimilarOffersRequestQuery()
    return backend.get_similar_offers(offer_id, user, query_params)


def get_similar_artists(
    artist_id: str,
) -> models.SimilarArtistsResponse:
    backend = _get_backend()
    return backend.get_similar_artists(artist_id)


def get_playlist(
    user: users_models.User,
    params: dict | None = None,
    body: dict | None = None,
) -> models.PlaylistResponse:
    backend = _get_backend()
    if params:
        query_params = models.PlaylistRequestQuery.model_validate(params)
    else:
        query_params = models.PlaylistRequestQuery()

    if body:
        body_params = models.PlaylistRequestBody.model_validate(body)
    else:
        body_params = models.PlaylistRequestBody()

    return backend.get_playlist(user, query_params, body_params)
