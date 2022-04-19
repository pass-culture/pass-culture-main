import logging

from sqlalchemy.orm import exc as orm_exc

from pcapi.core.educational import api
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1.serialization import venue as venue_serialization
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

from . import blueprint


@blueprint.adage_v1.route("/venues/<string:venues_siret>", methods=["GET"])
@spectree_serialize(
    api=blueprint.api,
    response_model=venue_serialization.GetVenuesBySiretResponseModel,
    on_error_statuses=[404, 422],
    tags=("get venues",),
)
@adage_api_key_required
def get_venues_from_siret(venues_siret: str) -> venue_serialization.GetVenuesBySiretResponseModel:
    try:
        venues = api.get_venues_by_siret(venues_siret)
    except orm_exc.NoResultFound:
        raise ApiErrors({"code": "VENUES_NOT_FOUND"}, status_code=404)

    return venue_serialization.GetVenuesBySiretResponseModel(
        venues=[venue_serialization.VenueModelWithRequiredSiret.from_orm(venue) for venue in venues]
    )


@blueprint.adage_v1.route("/venues/name/<string:venues_name>", methods=["GET"])
@spectree_serialize(
    api=blueprint.api,
    response_model=venue_serialization.GetVenuesWithOptionalSiretResponseModel,
    on_error_statuses=[404, 422],
    tags=("get venues",),
)
@adage_api_key_required
def get_venues_from_name(venues_name: str) -> venue_serialization.GetVenuesWithOptionalSiretResponseModel:
    venues = api.get_venues_by_name(venues_name)
    if len(venues) == 0:
        raise ApiErrors({"code": "VENUES_NOT_FOUND"}, status_code=404)

    return venue_serialization.GetVenuesWithOptionalSiretResponseModel(
        venues=[venue_serialization.VenueModelWithOptionalSiret.from_orm(venue) for venue in venues]
    )


@blueprint.adage_v1.route("/venues", methods=["GET"])
@spectree_serialize(
    api=blueprint.api,
    response_model=venue_serialization.GetVenuesWithOptionalSiretResponseModel,
    on_error_statuses=[422],
    tags=("get all venues",),
)
@adage_api_key_required
def get_all_venues(
    query: venue_serialization.GetAllVenuesQueryModel,
) -> venue_serialization.GetVenuesWithOptionalSiretResponseModel:
    venues = api.get_all_venues(query.page, query.per_page)

    return venue_serialization.GetVenuesWithOptionalSiretResponseModel(
        venues=[venue_serialization.VenueModelWithOptionalSiret.from_orm(venue) for venue in venues]
    )
