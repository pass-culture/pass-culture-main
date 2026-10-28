import json

from flask_login import current_user

import pcapi.connectors.recommendation as recommendation_api
from pcapi.core.artist.repository import get_artists_by_ids
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.native import blueprint
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize

from .serialization import recommendation as serializers


@blueprint.native_route("/recommendation/similar_offers/<int:offer_id>", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.SimilarOffersResponse)
def similar_offers(
    offer_id: int,
    query: serializers.SimilarOffersRequestQuery,
) -> serializers.SimilarOffersResponse:
    user = current_user if not current_user.is_anonymous else None
    try:
        raw_response = recommendation_api.get_similar_offers(
            offer_id,
            user,
            params=query.model_dump(mode="json"),
        )
    except recommendation_api.RecommendationApiTimeoutException:
        raise ApiErrors({"code": "RECOMMENDATION_API_TIMEOUT"}, status_code=504)
    except recommendation_api.RecommendationApiException:
        raise ApiErrors({"code": "RECOMMENDATION_API_ERROR"}, status_code=502)
    if not raw_response:
        return serializers.SimilarOffersResponse(results=[], params=serializers.RecommendationApiParams())
    return serializers.SimilarOffersResponse.parse_raw(raw_response, content_type="application/json")


@blueprint.native_route("/recommendation/offer_page_playlists/<int:offer_id>", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.OfferPagePlaylistResponse)
def offer_page_playlists(
    offer_id: int,
    query: serializers.OfferPagePlaylistQuery,
) -> serializers.OfferPagePlaylistResponse:
    user = current_user if not current_user.is_anonymous else None
    try:
        raw_response = recommendation_api.get_offer_page_playlists(
            offer_id,
            user,
            params=query.model_dump(mode="json"),
        )
    except recommendation_api.RecommendationApiTimeoutException:
        raise ApiErrors({"code": "RECOMMENDATION_API_TIMEOUT"}, status_code=504)
    except recommendation_api.RecommendationApiException:
        raise ApiErrors({"code": "RECOMMENDATION_API_ERROR"}, status_code=502)
    if not raw_response:
        return serializers.OfferPagePlaylistResponse(offer_id=str(offer_id), playlists=[], from_cache=False)

    return serializers.OfferPagePlaylistResponse.parse_raw(raw_response, content_type="application/json")


@blueprint.native_route("/recommendation/playlist", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=serializers.PlaylistResponse)
@authenticated_and_active_user_required
def playlist(
    query: serializers.PlaylistRequestQuery,
    body: serializers.PlaylistRequestBody,
) -> serializers.PlaylistResponse:
    try:
        raw_response = recommendation_api.get_playlist(
            current_user,
            params=query.model_dump(),
            body=body.model_dump(),
        )
    except recommendation_api.RecommendationApiTimeoutException:
        raise ApiErrors({"code": "RECOMMENDATION_API_TIMEOUT"}, status_code=504)
    except recommendation_api.RecommendationApiException:
        raise ApiErrors({"code": "RECOMMENDATION_API_ERROR"}, status_code=502)

    if not raw_response:
        return serializers.PlaylistResponse(
            playlist_recommended_offers=[], params=serializers.RecommendationApiParams()
        )

    return serializers.PlaylistResponse.parse_raw(raw_response, content_type="application/json")


@blueprint.native_route("/recommendation/top_artists_playlist/<search_group_name>", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.TopArtistsPlaylistResponse)
def top_artists_playlist(search_group_name: str) -> serializers.TopArtistsPlaylistResponse:
    try:
        raw_response = recommendation_api.get_top_artists_playlist(search_group_name)
    except recommendation_api.RecommendationApiValidationException:
        raise ApiErrors({"code": "RECOMMENDATION_API_VALIDATION"}, status_code=400)
    except recommendation_api.RecommendationApiTimeoutException:
        raise ApiErrors({"code": "RECOMMENDATION_API_TIMEOUT"}, status_code=504)
    except recommendation_api.RecommendationApiException:
        raise ApiErrors({"code": "RECOMMENDATION_API_ERROR"}, status_code=502)

    if not raw_response:
        return serializers.TopArtistsPlaylistResponse(artists=[])

    ds_response = json.loads(raw_response)
    artist_ids = ds_response.get("playlist_artists", [])

    artists = {artist.id: artist for artist in get_artists_by_ids(artist_ids)}

    return serializers.TopArtistsPlaylistResponse(
        artists=[
            serializers.ArtistItem(id=artist.id, name=artist.name, image=artist.thumbUrl)
            for artist_id in artist_ids
            if (artist := artists.get(artist_id))  # ensures the artist order returned by recommendation API
        ]
    )
