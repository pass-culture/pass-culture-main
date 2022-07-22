import logging

from sqlalchemy.orm import exc as orm_exc

from pcapi.core.educational import api as educational_api
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import offers as serializers
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


@blueprint.adage_iframe.route("/offers/categories", methods=["GET"])
@adage_jwt_required
@spectree_serialize(response_model=serializers.CategoriesResponseModel, api=blueprint.api)
def get_educational_offers_categories(
    authenticated_information: AuthenticatedInformation,
) -> serializers.CategoriesResponseModel:
    educational_categories = educational_api.get_educational_categories()

    return serializers.CategoriesResponseModel(
        categories=[
            serializers.CategoryResponseModel.from_orm(category) for category in educational_categories["categories"]
        ],
        subcategories=[
            serializers.SubcategoryResponseModel.from_orm(subcategory)
            for subcategory in educational_categories["subcategories"]
        ],
    )


@blueprint.adage_iframe.route("/collective/offers/<int:offer_id>", methods=["GET"])
@adage_jwt_required
@spectree_serialize(response_model=serializers.CollectiveOfferResponseModel, api=blueprint.api, on_error_statuses=[404])
def get_collective_offer(
    authenticated_information: AuthenticatedInformation, offer_id: int
) -> serializers.CollectiveOfferResponseModel:
    try:
        offer = educational_api.get_collective_offer_by_id_for_adage(offer_id)
    except orm_exc.NoResultFound:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NOT_FOUND"}, status_code=404)

    return serializers.CollectiveOfferResponseModel.from_orm(offer)


@blueprint.adage_iframe.route("/collective/offers-template/<int:offer_id>", methods=["GET"])
@adage_jwt_required
@spectree_serialize(
    response_model=serializers.CollectiveOfferTemplateResponseModel, api=blueprint.api, on_error_statuses=[404]
)
def get_collective_offer_template(
    authenticated_information: AuthenticatedInformation, offer_id: int
) -> serializers.CollectiveOfferTemplateResponseModel:
    try:
        offer = educational_api.get_collective_offer_template_by_id_for_adage(offer_id)
    except orm_exc.NoResultFound:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}, status_code=404)

    return serializers.CollectiveOfferTemplateResponseModel.from_orm(offer)
