import logging

from pcapi.core.categories import categories
from pcapi.core.offerers import repository as offerers_repository
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import public_api_collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.users_authentifications import api_key_required
from pcapi.validation.routes.users_authentifications import current_api_key


logger = logging.getLogger(__name__)


@blueprint.pro_public_api_v2.route("/collective-offers/venues", methods=["GET"])
@api_key_required
@spectree_serialize(
    on_success_status=200,
    on_error_statuses=[401],
    response_model=public_api_collective_offers_serialize.CollectiveOffersListVenuesResponseModel,
    api=blueprint.pro_public_schema_v2,
)
def list_venues() -> public_api_collective_offers_serialize.CollectiveOffersListVenuesResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste des lieux associés à la structure authentifiée par le jeton d'API.

    Tous les lieux enregistrés, physiques ou virtuels, sont listés ici avec leurs coordonnées.
    """
    offerer_id = current_api_key.offererId  # type: ignore [attr-defined]
    venues = offerers_repository.get_all_venues_by_offerer_id(offerer_id)

    return public_api_collective_offers_serialize.CollectiveOffersListVenuesResponseModel(
        __root__=[
            public_api_collective_offers_serialize.CollectiveOffersVenueResponseModel.from_orm(venue)
            for venue in venues
        ]
    )


@blueprint.pro_public_api_v2.route("/collective-offers/categories", methods=["GET"])
@api_key_required
@spectree_serialize(
    on_success_status=200,
    on_error_statuses=[401],
    response_model=public_api_collective_offers_serialize.CollectiveOffersListCategoriesResponseModel,
    api=blueprint.pro_public_schema_v2,
)
def list_categories() -> public_api_collective_offers_serialize.CollectiveOffersListCategoriesResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste des catégories d'offres proposées."""
    return public_api_collective_offers_serialize.CollectiveOffersListCategoriesResponseModel(
        __root__=[
            public_api_collective_offers_serialize.CollectiveOffersCategoryResponseModel(
                id=category.id, name=category.pro_label
            )
            for category in categories.ALL_CATEGORIES
            if category.is_selectable
        ]
    )
