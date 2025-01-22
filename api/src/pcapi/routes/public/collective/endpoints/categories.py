from collections import defaultdict

from pcapi.core.categories import pro_categories
from pcapi.core.categories import subcategories
from pcapi.routes.public import blueprints
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.routes.public.documentation_constants import http_responses
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import provider_api_key_required


@blueprints.deprecated_collective_public_api.route("/v2/collective/categories", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.deprecated_collective_public_api_schema,
    deprecated=True,
    tags=[tags.DEPRECATED_COLLECTIVE_CATEGORIES],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    offers_serialization.CollectiveOffersListCategoriesResponseModel,
                    http_responses.HTTP_200_MESSAGE,
                )
            }
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def list_categories() -> offers_serialization.CollectiveOffersListCategoriesResponseModel:
    """
    [LEGACY] Get collective offers categories

    Return categories for collective offers.
    """
    return offers_serialization.CollectiveOffersListCategoriesResponseModel(
        __root__=[
            offers_serialization.CollectiveOffersCategoryResponseModel(id=category.id, name=category.pro_label)
            for category in pro_categories.ALL_CATEGORIES
            if category.is_selectable
        ]
    )


@blueprints.deprecated_collective_public_api.route("/v2/collective/subcategories", methods=["GET"])
@provider_api_key_required
@spectree_serialize(
    api=spectree_schemas.deprecated_collective_public_api_schema,
    deprecated=True,
    tags=[tags.DEPRECATED_COLLECTIVE_CATEGORIES],
    resp=SpectreeResponse(
        **(
            {
                "HTTP_200": (
                    offers_serialization.CollectiveOffersListSubCategoriesResponseModel,
                    http_responses.HTTP_200_MESSAGE,
                ),
            }
            | http_responses.HTTP_40X_SHARED_BY_API_ENDPOINTS
        )
    ),
)
def list_subcategories() -> offers_serialization.CollectiveOffersListSubCategoriesResponseModel:
    """
    [LEGACY] Get collective offers subcatgories

    Return subcategories for collective offers.
    """
    result_dict = defaultdict(list)
    for _, subcategory in subcategories.COLLECTIVE_SUBCATEGORIES.items():
        if not subcategory.is_selectable:
            continue
        result_dict[subcategory.category.pro_label].append(
            offers_serialization.CollectiveOffersSubCategoryResponseModel.from_orm(subcategory)
        )

    sorted_list = []
    for category in sorted(result_dict.keys()):
        sorted_list.extend(sorted(result_dict[category], key=lambda x: x.label))

    return offers_serialization.CollectiveOffersListSubCategoriesResponseModel(__root__=sorted_list)
