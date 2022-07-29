import logging

from flask_login import current_user
from flask_login import login_required

from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.routes.serialization import collective_stock_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize_or_raise
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.workers.update_all_offers_active_status_job import update_all_collective_offers_active_status_job

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/collective/offers", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.ListCollectiveOffersResponseModel,
    api=blueprint.pro_private_schema,
)
def get_collective_offers(
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

    print("goo")
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
    dehumanized_id = dehumanize_or_raise(offer_id)
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(dehumanized_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    else:
        check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        offer = educational_repository.get_collective_offer_by_id(dehumanized_id)
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors(
            errors={
                "global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"],
            },
            status_code=404,
        )
    return collective_offers_serialize.GetCollectiveOfferResponseModel.from_orm(offer)


@private_api.route("/collective/offers-template/<offer_id>", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.GetCollectiveOfferTemplateResponseModel,
    api=blueprint.pro_private_schema,
)
def get_collective_offer_template(offer_id: str) -> collective_offers_serialize.GetCollectiveOfferTemplateResponseModel:
    dehumanized_id = dehumanize_or_raise(offer_id)
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_template_id(dehumanized_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    else:
        check_user_has_access_to_offerer(current_user, offerer.id)
    try:
        offer = educational_repository.get_collective_offer_template_by_id(dehumanized_id)
    except educational_exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors(
            errors={
                "global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"],
            },
            status_code=404,
        )
    return collective_offers_serialize.GetCollectiveOfferTemplateResponseModel.from_orm(offer)


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
    except offerers_exceptions.CannotFindOffererSiren:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    except educational_exceptions.CulturalPartnerNotFoundException:
        logger.info(
            "Could not create offer: This offerer has not been found in Adage", extra={"offerer_id": body.offerer_id}
        )
        raise ApiErrors({"offerer": "not found in adage"}, 403)
    except educational_exceptions.AdageException:
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
    except educational_exceptions.EducationalDomainsNotFound as error:
        logger.info(
            "Could not create offer: educational domains not found.",
            extra={"offer_name": body.name, "venue_id": body.venue_id, "domains": body.domains},
        )
        raise ApiErrors(
            {"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"},
            status_code=404,
        )

    return collective_offers_serialize.CollectiveOfferResponseIdModel.from_orm(offer)


@private_api.route("/collective/offers/<offer_id>", methods=["PATCH"])
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.GetCollectiveOfferResponseModel,
    api=blueprint.pro_private_schema,
)
def edit_collective_offer(
    offer_id: str, body: collective_offers_serialize.PatchCollectiveOfferBodyModel
) -> collective_offers_serialize.GetCollectiveOfferResponseModel:
    dehumanized_id = dehumanize_or_raise(offer_id)
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(dehumanized_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    else:
        check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        offers_api.update_collective_offer(
            offer_id=dehumanized_id, is_offer_showcase=False, new_values=body.dict(exclude_unset=True)
        )
    except offers_exceptions.SubcategoryNotEligibleForEducationalOffer:
        raise ApiErrors({"subcategoryId": "this subcategory is not educational"}, 400)
    except educational_exceptions.EducationalDomainsNotFound:
        logger.info(
            "Could not update offer: educational domains not found.",
            extra={"collective_offer_id": offer_id, "domains": body.domains},
        )
        raise ApiErrors(
            {"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"},
            status_code=404,
        )
    else:
        offer = educational_api.get_collective_offer_by_id(dehumanized_id)
        return collective_offers_serialize.GetCollectiveOfferResponseModel.from_orm(offer)


@private_api.route("/collective/offers-template/<offer_id>/", methods=["POST"])
@login_required
@spectree_serialize(
    on_success_status=201,
    on_error_statuses=[400, 403, 404],
    api=blueprint.pro_private_schema,
    response_model=collective_offers_serialize.CollectiveOfferTemplateResponseIdModel,
)
def create_collective_offer_template_from_collective_offer(
    offer_id: str, body: collective_offers_serialize.CollectiveOfferTemplateBodyModel
) -> collective_offers_serialize.CollectiveOfferTemplateResponseIdModel:
    dehumanized_offer_id = dehumanize_or_raise(offer_id)
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(dehumanized_offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    else:
        check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        collective_offer_template = educational_api.create_collective_offer_template_from_collective_offer(
            price_detail=body.price_detail, user=current_user, offer_id=dehumanized_offer_id
        )
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors(
            {"code": "COLLECTIVE_OFFER_NOT_FOUND"},
            status_code=404,
        )
    except educational_exceptions.EducationalStockAlreadyExists:
        raise ApiErrors(
            {"code": "EDUCATIONAL_STOCK_ALREADY_EXISTS"},
            status_code=400,
        )

    return collective_offers_serialize.CollectiveOfferTemplateResponseIdModel.from_orm(collective_offer_template)


@private_api.route("/collective/offers-template/<offer_id>", methods=["PATCH"])
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.GetCollectiveOfferTemplateResponseModel,
    api=blueprint.pro_private_schema,
)
def edit_collective_offer_template(
    offer_id: str, body: collective_offers_serialize.PatchCollectiveOfferTemplateBodyModel
) -> collective_offers_serialize.GetCollectiveOfferTemplateResponseModel:
    dehumanized_id = dehumanize_or_raise(offer_id)
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_template_id(dehumanized_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    else:
        check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        offers_api.update_collective_offer(
            offer_id=dehumanized_id, is_offer_showcase=True, new_values=body.dict(exclude_unset=True)
        )
    except offers_exceptions.SubcategoryNotEligibleForEducationalOffer:
        raise ApiErrors({"subcategoryId": "this subcategory is not educational"}, 400)
    except educational_exceptions.EducationalDomainsNotFound:
        logger.info(
            "Could not update offer: educational domains not found.",
            extra={"collective_offer_id": offer_id, "domains": body.domains},
        )
        raise ApiErrors(
            {"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"},
            status_code=404,
        )
    else:
        offer = educational_api.get_collective_offer_template_by_id(dehumanized_id)
        return collective_offers_serialize.GetCollectiveOfferTemplateResponseModel.from_orm(offer)


@private_api.route("/collective/offers-template/<offer_id>/to-collective-offer", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=201,
    response_model=collective_offers_serialize.CollectiveOfferFromTemplateResponseModel,
    api=blueprint.pro_private_schema,
)
def transform_collective_offer_template_into_collective_offer(
    offer_id: str, body: collective_stock_serialize.CollectiveStockCreationBodyModel
) -> collective_offers_serialize.CollectiveOfferFromTemplateResponseModel:
    dehumanized_offer_id = dehumanize_or_raise(offer_id)
    if not int(body.offer_id) == dehumanized_offer_id:
        ApiErrors(
            {"offer": ["L'id de l'offre fournie en argument et celui du stock doivent être les mêmes"]}, status_code=403
        )
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_template_id(dehumanized_offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    offer = educational_api.transform_collective_offer_template_into_collective_offer(user=current_user, body=body)

    return collective_offers_serialize.CollectiveOfferFromTemplateResponseModel.from_orm(offer)


@private_api.route("/collective/offers/all-active-status", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def patch_all_collective_offers_active_status(
    body: collective_offers_serialize.PatchAllCollectiveOffersActiveStatusBodyModel,
) -> None:
    filters = {
        "user_id": current_user.id,
        "is_user_admin": current_user.has_admin_role,
        "offerer_id": body.offerer_id,
        "status": body.status,
        "venue_id": body.venue_id,
        "category_id": body.category_id,
        "name_or_isbn": body.name_or_isbn,
        "creation_mode": body.creation_mode,
        "period_beginning_date": body.period_beginning_date,
        "period_ending_date": body.period_ending_date,
    }
    update_all_collective_offers_active_status_job.delay(filters, body.is_active)


@private_api.route("/collective/offers/active-status", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def patch_collective_offers_active_status(
    body: collective_offers_serialize.PatchCollectiveOfferActiveStatusBodyModel,
) -> None:
    collective_query = educational_api.get_query_for_collective_offers_by_ids_for_user(current_user, body.ids)
    offers_api.batch_update_collective_offers(collective_query, {"isActive": body.is_active})


@private_api.route("/collective/offers-template/active-status", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def patch_collective_offers_template_active_status(
    body: collective_offers_serialize.PatchCollectiveOfferActiveStatusBodyModel,
) -> None:
    collective_template_query = educational_api.get_query_for_collective_offers_template_by_ids_for_user(
        current_user, body.ids
    )
    offers_api.batch_update_collective_offers_template(collective_template_query, {"isActive": body.is_active})


@private_api.route("/collective/offers/<offer_id>/educational_institution", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=200,
    on_error_statuses=[403, 404],
    api=blueprint.pro_private_schema,
    response_model=collective_offers_serialize.GetCollectiveOfferResponseModel,
)
def patch_collective_offers_educational_institution(
    offer_id: str, body: collective_offers_serialize.PatchCollectiveOfferEducationalInstitution
) -> collective_offers_serialize.GetCollectiveOfferResponseModel:
    dehumanized_id = dehumanize_or_raise(offer_id)
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(dehumanized_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    else:
        check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        offer = educational_api.update_collective_offer_educational_institution(
            offer_id=dehumanized_id,
            educational_institution_id=body.educational_institution_id,
            is_creating_offer=body.is_creating_offer,
            user=current_user,
        )
    except educational_exceptions.EducationalInstitutionNotFound:
        raise ApiErrors({"educationalInstitution": ["Aucune institution trouvée à partir de cet id"]}, status_code=404)

    except educational_exceptions.CollectiveOfferNotEditable:
        raise ApiErrors({"offer": ["L'offre n'est plus modifiable"]}, status_code=403)

    return collective_offers_serialize.GetCollectiveOfferResponseModel.from_orm(offer)
