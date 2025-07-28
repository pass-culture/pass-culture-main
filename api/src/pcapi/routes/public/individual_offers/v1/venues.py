import logging

import sqlalchemy.orm as sa_orm

from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.routes.public.serialization import venues as venues_serialization
from pcapi.routes.public.services import authorization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.utils.siren import SIRET_OR_RIDET_RE
from pcapi.utils.siren import is_siret_or_ridet
from pcapi.validation.routes.users_authentifications import current_api_key
from pcapi.validation.routes.users_authentifications import provider_api_key_required


logger = logging.getLogger(__name__)


@blueprints.public_api.route("/public/offers/v1/offerer_venues", methods=["GET"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.VENUES],
    response_model=venues_serialization.GetOfferersVenuesResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (venues_serialization.GetOfferersVenuesResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def get_offerer_venues(
    query: venues_serialization.GetOfferersVenuesQuery,
) -> venues_serialization.GetOfferersVenuesResponse:
    """
    Get Offerer Venues

    Return all the venues attached to the API key for given offerer.
    """
    rows = offerers_api.get_providers_offerer_and_venues(current_api_key.provider, query.siren)
    return venues_serialization.GetOfferersVenuesResponse.serialize_offerers_venues(rows)


@blueprints.public_api.route("/public/offers/v1/venues/<siret>", methods=["GET"])
@atomic()
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    tags=[tags.VENUES],
    response_model=venues_serialization.VenueResponse,
    resp=SpectreeResponse(
        **(
            {"HTTP_200": (venues_serialization.VenueResponse, http_responses.HTTP_200_MESSAGE)}
            # errors
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
            | http_responses.HTTP_404_VENUE_NOT_FOUND
        )
    ),
)
def get_venue_by_siret(
    siret: str,
) -> venues_serialization.VenueResponse:
    """
    Get Venue

    Return venue corresponding to the given [**SIRET number (Système d'identification du répertoire des établissements)**](https://www.economie.gouv.fr/cedef/numero-siret)
    """
    if not is_siret_or_ridet(siret):
        raise api_errors.ApiErrors({"siret": [f'string does not match regex "{SIRET_OR_RIDET_RE}"']})

    venue = (
        db.session.query(offerers_models.Venue)
        .options(
            sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(offerers_models.OffererAddress.address)
        )
        .filter(offerers_models.Venue.siret == siret)
        .one_or_none()
    )

    if not venue:
        raise api_errors.ResourceNotFoundError(errors={"global": "Venue cannot be found"})
    authorization.get_venue_provider_or_raise_404(venue_id=venue.id)  # check provider has access

    return venues_serialization.VenueResponse.build_model(venue)
