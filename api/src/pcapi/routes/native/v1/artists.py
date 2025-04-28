import logging

from pcapi.core.artist.models import Artist
from pcapi.repository.session_management import atomic
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint
from .serialization import artists as serializers


logger = logging.getLogger(__name__)


@blueprint.native_route("/artists/<string:artist_id>", methods=["GET"])
@spectree_serialize(response_model=serializers.ArtistResponse, api=blueprint.api, on_error_statuses=[404])
@atomic()
def get_artist(artist_id: str) -> serializers.ArtistResponse:

    artist = Artist.query.get_or_404(artist_id)

    return serializers.ArtistResponse.from_orm(artist)
