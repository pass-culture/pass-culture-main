from abc import ABC
from abc import abstractmethod

from pcapi.connectors.recommendation import models
from pcapi.core.users.models import User


class BaseRecommandationBackend(ABC):
    @abstractmethod
    def get_similar_offers(
        self,
        offer_id: int,
        user: User | None,
        params: models.SimilarOffersRequestQuery,
    ) -> models.SimilarOffersResponse:
        raise NotImplementedError()

    @abstractmethod
    def get_similar_artists(
        self,
        artist_id: str,
    ) -> models.SimilarArtistsResponse:
        raise NotImplementedError()

    @abstractmethod
    def get_playlist(
        self,
        user: User,
        params: models.PlaylistRequestQuery,
        body: models.PlaylistRequestBody,
    ) -> models.PlaylistResponse:
        raise NotImplementedError()
