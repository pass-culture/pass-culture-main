import pcapi.core.users.models as users_models

from . import models


class TestingBackend:
    def get_similar_offers(
        self,
        offer_id: int,
        user: users_models.User | None,
        params: dict,
    ) -> models.SimilarOffersResponse:
        offers = [i + 10 * offer_id + 100 * (user.id if user else 0) for i in range(3)]
        response = {
            "results": [str(id_) for id_ in offers],
            "params": {
                "reco_origin": "unknown",
                "model_origin": "default",
                "call_id": "956bd070-cbb1-42d3-bea4-89855bf3b11c",
            },
        }
        return models.SimilarOffersResponse.model_validate(response)

    def get_similar_artists(
        self,
        artist_id: str,
    ) -> models.SimilarArtistsResponse:
        response = {
            "similar_artists": [],
            "params": {
                "artist_id": artist_id,
                "call_id": "00000000-0000-0000-0000-000000000000",
            },
        }
        return models.SimilarArtistsResponse.model_validate(response)

    def get_playlist(
        self,
        user: users_models.User,
        params: dict,
        body: dict,
    ) -> models.PlaylistResponse:
        offers = [i + 100 * user.id for i in range(3)]
        response = {
            "playlist_recommended_offers": [str(id_) for id_ in offers],
            "params": {
                "reco_origin": "unknown",
                "model_origin": "default",
                "call_id": "1dc4c5f2-303c-4d8a-94c3-77c0085c0c70",
            },
        }
        return models.PlaylistResponse.model_validate(response)
