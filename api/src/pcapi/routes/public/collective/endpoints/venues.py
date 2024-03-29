from pcapi.core.offerers import api as offerers_api
from pcapi.core.providers import repository as providers_repository
from pcapi.routes.public import blueprints
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.routes.public.collective.serialization import venues as serialization
import pcapi.routes.public.serialization.venues as venues_serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key


@blueprints.v2_prefixed_public_api.route("/collective/venues", methods=["GET"])
@spectree_serialize(
    api=blueprints.v2_prefixed_public_api_schema,
    tags=["API offres collectives"],
    resp=SpectreeResponse(
        HTTP_200=(
            serialization.CollectiveOffersListVenuesResponseModel,
            "La liste des lieux ou vous pouvez créer une offre.",
        ),
        HTTP_401=(
            offers_serialization.AuthErrorResponseModel,
            "Authentification nécessaire",
        ),
    ),
)
@api_key_required
def list_venues() -> serialization.CollectiveOffersListVenuesResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste des lieux associés au fournisseur authentifiée par le jeton d'API.

    Tous les lieux enregistrés, sont listés ici avec leurs coordonnées.
    """
    venues = providers_repository.get_providers_venues(current_api_key.providerId)

    return serialization.CollectiveOffersListVenuesResponseModel(
        __root__=[venues_serialization.VenueResponse.build_model(venue) for venue in venues]
    )


@blueprints.v2_prefixed_public_api.route("/collective/offerer_venues", methods=["GET"])
@spectree_serialize(
    api=blueprints.v2_prefixed_public_api_schema,
    tags=["API offres collectives"],
    resp=SpectreeResponse(
        HTTP_200=(
            venues_serialization.GetOfferersVenuesResponse,
            "La liste des lieux, groupés par structures",
        ),
        HTTP_401=(
            offers_serialization.AuthErrorResponseModel,
            "Authentification nécessaire",
        ),
    ),
)
@api_key_required
def get_offerer_venues(
    query: venues_serialization.GetOfferersVenuesQuery,
) -> venues_serialization.GetOfferersVenuesResponse:
    # in French, to be used by Swagger for the API documentation
    """Récupération des lieux associés au fournisseur authentifié
    par le jeton d'API; groupés par structures.

    Tous les lieux enregistrés, sont listés ici avec leurs coordonnées.
    """
    rows = offerers_api.get_providers_offerer_and_venues(current_api_key.provider, query.siren)
    return venues_serialization.GetOfferersVenuesResponse.serialize_offerers_venues(rows)
