from collections import defaultdict
from typing import cast

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
from pcapi.routes.pro import blueprint
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import public_api_collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


@blueprint.pro_public_api_v2.route("/collective/categories", methods=["GET"])
@api_key_required
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
    tags=["API offres collectives"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    public_api_collective_offers_serialize.CollectiveOffersListCategoriesResponseModel,
                    "La liste des catégories éligibles existantes.",
                ),
                "HTTP_401": (
                    cast(BaseModel, public_api_collective_offers_serialize.AuthErrorResponseModel),
                    "Authentification nécessaire",
                ),
            }
        )
    ),
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


@blueprint.pro_public_api_v2.route("/collective/subcategories", methods=["GET"])
@api_key_required
@spectree_serialize(
    api=blueprint.pro_public_schema_v2,
    tags=["API offres collectives"],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    public_api_collective_offers_serialize.CollectiveOffersListSubCategoriesResponseModel,
                    "La liste des sous-catégories éligibles existantes.",
                ),
                "HTTP_401": (
                    cast(BaseModel, public_api_collective_offers_serialize.AuthErrorResponseModel),
                    "Authentification nécessaire",
                ),
            }
        )
    ),
)
def list_subcategories() -> public_api_collective_offers_serialize.CollectiveOffersListSubCategoriesResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste des sous-catégories d'offres proposées a un public collectif."""
    result_dict = defaultdict(list)
    for _, subcategory in subcategories_v2.COLLECTIVE_SUBCATEGORIES.items():
        if not subcategory.is_selectable:
            continue
        result_dict[subcategory.category.pro_label].append(
            public_api_collective_offers_serialize.CollectiveOffersSubCategoryResponseModel.from_orm(subcategory)
        )

    sorted_list = []
    for category in sorted(result_dict.keys()):
        sorted_list.extend(sorted(result_dict[category], key=lambda x: x.label))

    return public_api_collective_offers_serialize.CollectiveOffersListSubCategoriesResponseModel(__root__=sorted_list)
