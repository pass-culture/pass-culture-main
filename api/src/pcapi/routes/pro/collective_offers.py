import logging

from flask_login import current_user
from flask_login import login_required

from pcapi.connectors.api_adage import AdageException
from pcapi.connectors.api_adage import CulturalPartnerNotFoundException
from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/collective/offers", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.ListCollectiveOffersResponseModel,
    api=blueprint.pro_private_schema,
)
def list_collective_offers(
    query: collective_offers_serialize.ListCollectiveOffersQueryModel,
) -> collective_offers_serialize.ListCollectiveOffersResponseModel:
    capped_offers = educational_api.list_collective_offers_for_pro_user(
        user_id=current_user.id,
        user_is_admin=current_user.has_admin_role,
        category_id=query.categoryId,
        offerer_id=query.offerer_id,
        venue_id=query.venue_id,
        name_keywords=query.nameOrIsbn,
        status=query.status,
        period_beginning_date=query.period_beginning_date,
        period_ending_date=query.period_ending_date,
    )

    return collective_offers_serialize.ListCollectiveOffersResponseModel(
        __root__=collective_offers_serialize.serialize_collective_offers_capped(capped_offers)
    )


@private_api.route("/collective/offers/<offer_id>", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.GetCollectiveOfferResponseModel,
    api=blueprint.pro_private_schema,
)
def get_collective_offer(offer_id: str) -> collective_offers_serialize.GetCollectiveOfferResponseModel:
    try:
        offer = educational_repository.get_offer_by_id(dehumanize(offer_id))  # type: ignore [arg-type]
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors(
            errors={
                "global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"],
            },
            status_code=404,
        )
    return collective_offers_serialize.GetCollectiveOfferResponseModel.from_orm(offer)


@private_api.route("/collective/offers", methods=["POST"])
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.CollectiveOfferResponseIdModel,
    on_success_status=201,
    api=blueprint.pro_private_schema,
)
def create_collective_offer(
    body: collective_offers_serialize.PostCollectiveOfferBodyModel,
) -> collective_offers_serialize.CollectiveOfferResponseIdModel:
    try:
        offer = educational_api.create_collective_offer(offer_data=body, user=current_user)
    except CulturalPartnerNotFoundException:
        logger.info(
            "Could not create offer: This offerer has not been found in Adage", extra={"offerer_id": body.offerer_id}
        )
        raise ApiErrors({"offerer": "not found in adage"}, 403)
    except AdageException:
        logger.info("Could not create offer: Adage api call failed", extra={"offerer_id": body.offerer_id})
        raise ApiErrors({"adage_api": "error"}, 500)
    except offers_exceptions.UnknownOfferSubCategory as error:
        logger.info(
            "Could not create offer: selected subcategory is unknown.",
            extra={"offer_name": body.name, "venue_id": body.venue_id},
        )
        raise ApiErrors(
            error.errors,
            status_code=400,
        )
    except offers_exceptions.SubCategoryIsInactive as error:
        logger.info(
            "Could not create offer: subcategory cannot be selected.",
            extra={"offer_name": body.name, "venue_id": body.venue_id},
        )
        raise ApiErrors(
            error.errors,
            status_code=400,
        )
    except offers_exceptions.SubcategoryNotEligibleForEducationalOffer as error:
        logger.info(
            "Could not create offer: subcategory is not eligible for educational offer.",
            extra={"offer_name": body.name, "venue_id": body.venue_id},
        )
        raise ApiErrors(
            error.errors,
            status_code=400,
        )

    return collective_offers_serialize.CollectiveOfferResponseIdModel.from_orm(offer)
