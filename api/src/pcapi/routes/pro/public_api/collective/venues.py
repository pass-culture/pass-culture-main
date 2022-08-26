from pcapi.core.offerers import repository as offerers_repository
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import public_api_collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key


@blueprint.pro_public_api_v2.route("/collective/venues", methods=["GET"])
@api_key_required
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
    tags=["API offres collectives"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    public_api_collective_offers_serialize.CollectiveOffersListVenuesResponseModel,
                    "La liste des lieux ou vous pouvez créer une offre.",
                ),
                "HTTP_401": (None, "Authentification nécessaire"),
            }
        )
    ),
)
def list_venues() -> public_api_collective_offers_serialize.CollectiveOffersListVenuesResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste des lieux associés à la structure authentifiée par le jeton d'API.

    Tous les lieux enregistrés, sont listés ici avec leurs coordonnées.
    """
    offerer_id = current_api_key.offererId  # type: ignore [attr-defined]
    venues = offerers_repository.get_all_venues_by_offerer_id(offerer_id)

    return public_api_collective_offers_serialize.CollectiveOffersListVenuesResponseModel(
        __root__=[
            public_api_collective_offers_serialize.CollectiveOffersVenueResponseModel.from_orm(venue)
            for venue in venues
        ]
    )
