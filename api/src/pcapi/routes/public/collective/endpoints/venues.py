from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.providers import repository as providers_repository
from pcapi.models.feature import FeatureToggle
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
    if FeatureToggle.ENABLE_PROVIDER_AUTHENTIFICATION.is_active():
        venues = providers_repository.get_providers_venues(current_api_key.providerId)
    else:
        venues = offerers_repository.get_all_venues_by_offerer_id(current_api_key.offererId)

    return serialization.CollectiveOffersListVenuesResponseModel(
        __root__=[venues_serialization.VenueResponse.build_model(venue) for venue in venues]
    )
