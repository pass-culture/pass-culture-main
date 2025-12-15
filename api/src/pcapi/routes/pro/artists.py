import logging

from flask_login import login_required

from pcapi.core.artist import repository as artist_repository
from pcapi.models import api_errors
from pcapi.models.feature import FeatureToggle
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import artist_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/artists", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=artist_serialize.ArtistsResponseModel,
    api=blueprint.pro_private_schema,
)
@atomic()
def get_artists(query: artist_serialize.ArtistQueryModel) -> artist_serialize.ArtistsResponseModel:
    if not FeatureToggle.WIP_OFFER_ARTISTS.is_active():
        raise api_errors.ApiErrors(errors={"global": "service not available"}, status_code=503)
    artists = [
        artist_serialize.ArtistResponseModel.model_validate(artist)
        for artist in artist_repository.get_filtered_artists_for_search(query.search)
    ]
    return artist_serialize.ArtistsResponseModel(artists)
