from collections import defaultdict

from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
from pcapi.routes.public import spectree_schemas
from pcapi.routes.public.collective.blueprint import collective_offers_blueprint
from pcapi.routes.public.collective.serialization import offers as offers_serialization
from pcapi.routes.public.documentation_constants import tags
from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendResponse as SpectreeResponse
from pcapi.validation.routes.users_authentifications import api_key_required


@collective_offers_blueprint.route("/collective/categories", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    deprecated=True,
    tags=[tags.COLLECTIVE_CATEGORIES],
    resp=SpectreeResponse(
        HTTP_200=(
            offers_serialization.CollectiveOffersListCategoriesResponseModel,
            "La liste des catégories éligibles existantes.",
        ),
        HTTP_401=(
            offers_serialization.AuthErrorResponseModel,
            "Authentification nécessaire",
        ),
    ),
)
@api_key_required
def list_categories() -> offers_serialization.CollectiveOffersListCategoriesResponseModel:
    # in French, to be used by Swagger for the API documentation
    """
    Récupération de la liste des catégories d'offres proposées.
    """
    return offers_serialization.CollectiveOffersListCategoriesResponseModel(
        __root__=[
            offers_serialization.CollectiveOffersCategoryResponseModel(id=category.id, name=category.pro_label)
            for category in categories.ALL_CATEGORIES
            if category.is_selectable
        ]
    )


@collective_offers_blueprint.route("/collective/subcategories", methods=["GET"])
@spectree_serialize(
    api=spectree_schemas.public_api_schema,
    deprecated=True,
    tags=[tags.COLLECTIVE_CATEGORIES],
    resp=SpectreeResponse(
        HTTP_200=(
            offers_serialization.CollectiveOffersListSubCategoriesResponseModel,
            "La liste des sous-catégories éligibles existantes.",
        ),
        HTTP_401=(
            offers_serialization.AuthErrorResponseModel,
            "Authentification nécessaire",
        ),
    ),
)
@api_key_required
def list_subcategories() -> offers_serialization.CollectiveOffersListSubCategoriesResponseModel:
    # in French, to be used by Swagger for the API documentation
    """Récupération de la liste des sous-catégories d'offres proposées a un public collectif."""
    result_dict = defaultdict(list)
    for _, subcategory in subcategories_v2.COLLECTIVE_SUBCATEGORIES.items():
        if not subcategory.is_selectable:
            continue
        result_dict[subcategory.category.pro_label].append(
            offers_serialization.CollectiveOffersSubCategoryResponseModel.from_orm(subcategory)
        )

    sorted_list = []
    for category in sorted(result_dict.keys()):
        sorted_list.extend(sorted(result_dict[category], key=lambda x: x.label))

    return offers_serialization.CollectiveOffersListSubCategoriesResponseModel(__root__=sorted_list)
