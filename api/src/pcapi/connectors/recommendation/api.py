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
    params: models.SimilarOffersRequestQuery | None = None,
) -> models.SimilarOffersResponse:
    backend = _get_backend()
    if not params:
        query_params = models.SimilarOffersRequestQuery()
    else:
        query_params = params
    return backend.get_similar_offers(offer_id, user, query_params)


def get_similar_artists(
    artist_id: str,
) -> models.SimilarArtistsResponse:
    backend = _get_backend()
    return backend.get_similar_artists(artist_id)


def get_playlist(
    user: users_models.User,
    params: models.PlaylistRequestQuery | None = None,
    body: models.PlaylistRequestBody | None = None,
) -> models.PlaylistResponse:
    backend = _get_backend()
    if not params:
        query_params = models.PlaylistRequestQuery()
    else:
        query_params = params
    if not body:
        body_params = models.PlaylistRequestBody()
    else:
        body_params = body

    return backend.get_playlist(user, query_params, body_params)
