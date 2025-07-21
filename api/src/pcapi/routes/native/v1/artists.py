import logging

from flask import abort

from pcapi.core.artist.api import get_artist_image_url
from pcapi.core.artist.models import Artist
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint
from .serialization import artists as serializers


logger = logging.getLogger(__name__)


@blueprint.native_route("/artists/<string:artist_id>", methods=["GET"])
@spectree_serialize(response_model=serializers.ArtistResponse, api=blueprint.api, on_error_statuses=[404])
@atomic()
def get_artist(artist_id: str) -> serializers.ArtistResponse:
    artist = db.session.query(Artist).filter(Artist.id == artist_id).one_or_none()
    if not artist:
        abort(404)

    return serializers.ArtistResponse(
        id=artist.id,
        name=artist.name,
        description=artist.description,
        image=get_artist_image_url(artist),
    )
