from flask_login import login_required

from pcapi.core.categories import subcategories
from pcapi.flask_app import private_api
from pcapi.routes.serialization import offers_serialize
from pcapi.serialization.decorator import spectree_serialize


@private_api.route("/subcategories", methods=["GET"])
@login_required
@spectree_serialize(response_model=offers_serialize.SubcategoriesForWebappResponseModel)
def get_subcategories() -> offers_serialize.SubcategoriesForWebappResponseModel:
    return offers_serialize.SubcategoriesForWebappResponseModel(
        subcategories=[
            offers_serialize.SubcategoryResponseModel.from_orm(subcategory)
            for subcategory in subcategories.ALL_SUBCATEGORIES
        ],
        searchGroups=[
            offers_serialize.SearchGroupResponseModel.from_orm(search_group)
            for search_group in [s for s in subcategories.SearchGroupChoices if s.value]
        ],
    )
