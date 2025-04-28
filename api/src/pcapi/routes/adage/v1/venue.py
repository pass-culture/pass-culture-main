import logging

from sqlalchemy.orm import exc as orm_exc

from pcapi.core.educational.api import venue as educational_api_venue
from pcapi.core.offerers import repository as offerers_repository
from pcapi.models.api_errors import ApiErrors
from pcapi.repository.session_management import atomic
from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1.serialization import venue as venue_serialization
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

from . import blueprint


@blueprint.adage_v1.route("/venues/<string:venues_siret>", methods=["GET"])
@atomic()
@spectree_serialize(
    api=blueprint.api,
    response_model=venue_serialization.GetVenuesResponseModel,
    on_error_statuses=[404, 422],
    tags=("get venues",),
)
@adage_api_key_required
def get_venues_from_siret(
    venues_siret: str, query: venue_serialization.GetRelativeVenuesQueryModel
) -> venue_serialization.GetVenuesResponseModel:
    if query.getRelative:
        venues = educational_api_venue.get_relative_venues_by_siret(venues_siret)
    else:
        try:
            venues = educational_api_venue.get_venues_by_siret(venues_siret)
        except orm_exc.NoResultFound:
            venues = []
    if not venues:
        raise ApiErrors({"code": "VENUES_NOT_FOUND"}, status_code=404)
    return venue_serialization.GetVenuesResponseModel(
        venues=[venue_serialization.VenueModel.from_orm(venue) for venue in venues]
    )


@blueprint.adage_v1.route("/venues/name/<string:venues_name>", methods=["GET"])
@atomic()
@spectree_serialize(
    api=blueprint.api,
    response_model=venue_serialization.GetVenuesResponseModel,
    on_error_statuses=[404, 422],
    tags=("get venues",),
)
@adage_api_key_required
def get_venues_from_name(
    venues_name: str, query: venue_serialization.GetRelativeVenuesQueryModel
) -> venue_serialization.GetVenuesResponseModel:
    if query.getRelative:
        venues = educational_api_venue.get_relative_venues_by_name(venues_name)
    else:
        venues = educational_api_venue.get_venues_by_name(venues_name)
    if len(venues) == 0:
        raise ApiErrors({"code": "VENUES_NOT_FOUND"}, status_code=404)

    return venue_serialization.GetVenuesResponseModel(
        venues=[venue_serialization.VenueModel.from_orm(venue) for venue in venues]
    )


@blueprint.adage_v1.route("/venues", methods=["GET"])
@atomic()
@spectree_serialize(
    api=blueprint.api,
    response_model=venue_serialization.GetVenuesResponseModel,
    on_error_statuses=[422],
    tags=("get all venues",),
)
@adage_api_key_required
def get_all_venues(
    query: venue_serialization.GetAllVenuesQueryModel,
) -> venue_serialization.GetVenuesResponseModel:
    venues = educational_api_venue.get_all_venues(query.page, query.per_page)

    return venue_serialization.GetVenuesResponseModel(
        venues=[venue_serialization.VenueModel.from_orm(venue) for venue in venues]
    )


@blueprint.adage_v1.route("/venues/id/<int:venue_id>", methods=["GET"])
@atomic()
@spectree_serialize(
    api=blueprint.api,
    response_model=venue_serialization.VenueModel,
    on_error_statuses=[404, 422],
    tags=("get venue",),
)
@adage_api_key_required
def get_venue_by_id(venue_id: int) -> venue_serialization.VenueModel:
    venue = offerers_repository.find_venue_by_id(venue_id)
    if not venue:
        raise ApiErrors({"code": "VENUE_NOT_FOUND"}, status_code=404)
    return venue_serialization.VenueModel.from_orm(venue)


@blueprint.adage_v1.route("/venues/relative/id/<int:venue_id>", methods=["GET"])
@atomic()
@spectree_serialize(
    api=blueprint.api,
    response_model=venue_serialization.GetVenuesResponseModel,
    on_error_statuses=[404, 422],
    tags=("get venue",),
)
@adage_api_key_required
def get_relative_venues_by_id(venue_id: int) -> venue_serialization.GetVenuesResponseModel:
    venues = offerers_repository.find_relative_venue_by_id(venue_id)
    if not venues:
        raise ApiErrors({"code": "VENUE_NOT_FOUND"}, status_code=404)

    return venue_serialization.GetVenuesResponseModel(
        venues=[venue_serialization.VenueModel.from_orm(venue) for venue in venues]
    )
