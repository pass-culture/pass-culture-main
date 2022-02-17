import logging

from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload

from pcapi.core.educational import api as educational_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import offers as serializers
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


@blueprint.adage_iframe.route("/offer/<int:offer_id>", methods=["GET"])
@adage_jwt_required
@spectree_serialize(response_model=serializers.OfferResponse, api=blueprint.api, on_error_statuses=[404])
def get_offer(authenticated_information: AuthenticatedInformation, offer_id: int) -> serializers.OfferResponse:
    offer = (
        offers_models.Offer.query.filter(offers_models.Offer.id == offer_id)
        .join(offers_models.Stock)
        .filter(offers_models.Stock.isSoftDeleted.is_(False))
        .options(contains_eager(offers_models.Offer.stocks))
        .options(
            joinedload(offers_models.Offer.venue)
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(
                offerers_models.Offerer.name,
                offerers_models.Offerer.validationToken,
                offerers_models.Offerer.isActive,
            )
        )
        .first_or_404()
    )

    return serializers.OfferResponse.from_orm(offer)


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
