import json
import logging
import uuid

from flask import abort

from pcapi.connectors import recommendation as recommendation_connector
from pcapi.core.artist import repository as artist_repository
from pcapi.core.artist.models import Artist
from pcapi.models import db
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint
from .serialization import artists as serializers


logger = logging.getLogger(__name__)


@blueprint.native_route("/artists/<string:artist_id>", methods=["GET"])
@spectree_serialize(response_model=serializers.ArtistResponse, api=blueprint.api, on_error_statuses=[404])
def get_artist(artist_id: str) -> serializers.ArtistResponse:
    artist = db.session.query(Artist).filter(Artist.id == artist_id).one_or_none()
    if not artist or artist.is_blacklisted:
        abort(404)

    return serializers.ArtistResponse(
        id=artist.id,
        name=artist.name,
        description=artist.biography or artist.description,
        description_credit="© Contenu généré par IA \u2728" if artist.biography else None,
        description_source=artist.wikipedia_url if artist.biography else None,
        image=artist.thumbUrl,
    )


@blueprint.native_route("/artists/<string:artist_id>/similar", methods=["GET"])
@spectree_serialize(response_model=serializers.SimilarArtistsResponse, api=blueprint.api, on_error_statuses=[400])
def get_similar_artists(artist_id: str) -> serializers.SimilarArtistsResponse:
    try:
        uuid.UUID(artist_id)
    except ValueError:
        abort(400)

    try:
        raw = recommendation_connector.get_similar_artists(artist_id)
    except recommendation_connector.RecommendationApiTimeoutException:
        logger.warning("Recommendation API timeout for similar_artists", extra={"artist_id": artist_id})
        return serializers.SimilarArtistsResponse(artists=[])
    except recommendation_connector.RecommendationApiException:
        logger.warning("Recommendation API error for similar_artists", extra={"artist_id": artist_id})
        return serializers.SimilarArtistsResponse(artists=[])

    ds_response = json.loads(raw)
    artist_ids = [item["artist_id_match"] for item in ds_response.get("similar_artists", [])]

    if not artist_ids:
        return serializers.SimilarArtistsResponse(artists=[])

    artists_by_id = {artist.id: artist for artist in artist_repository.get_artists_by_ids(artist_ids)}

    return serializers.SimilarArtistsResponse(
        artists=[
            serializers.SimilarArtistItem(id=artist.id, name=artist.name, image=artist.thumbUrl)
            for aid in artist_ids
            if (artist := artists_by_id.get(aid))
        ]
    )
