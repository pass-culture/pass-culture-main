from sqlalchemy import func

from pcapi.connectors.recommendation import models
from pcapi.core.artist.models import Artist
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import User
from pcapi.models import db

from .base import BaseRecommandationBackend


class LocalBackend(BaseRecommandationBackend):
    """
    Recommandation emulation based on results in the database.

    Pick random 10 offer IDs from a given database to emulate recommandation
    without Algolia. For non-production development only.
    """

    def get_similar_offers(
        self,
        offer_id: int,
        user: User | None,
        params: models.SimilarOffersRequestQuery,
    ) -> models.SimilarOffersResponse:

        offers = db.session.query(Offer).order_by(func.random()).limit(10)

        return models.SimilarOffersResponse(
            results=[str(offer.id) for offer in offers],
        )

    def get_similar_artists(
        self,
        artist_id: str,
    ) -> models.SimilarArtistsResponse:
        offers = db.session.query(Artist).order_by(func.random()).limit(10)

        return models.SimilarArtistsResponse(
            similar_artists=[
                models.MatchedArtist(artist_id_match=str(offer.id), rank=index) for index, offer in enumerate(offers)
            ],
            params=models.SimilarArtistsParams(artist_id=artist_id),
        )

    def get_playlist(
        self,
        user: User,
        params: models.PlaylistRequestQuery,
        body: models.PlaylistRequestBody,
    ) -> models.PlaylistResponse:

        offers = db.session.query(Offer).order_by(func.random()).limit(10)

        return models.PlaylistResponse(
            playlist_recommended_offers=[str(offer.id) for offer in offers],
            params=models.RecommendationApiParams(),
        )
