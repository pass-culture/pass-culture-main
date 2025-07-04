import logging
from datetime import datetime

from PIL import UnidentifiedImageError
from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import validation as educational_validation
from pcapi.core.educational.api import adage as educational_api_adage
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import validation as offers_validation
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import transaction
from pcapi.repository.session_management import atomic
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.routes.serialization import educational_redactors
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_offerer

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/collective/offers", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.ListCollectiveOffersResponseModel,
    api=blueprint.pro_private_schema,
    query_params_as_list=["status"],
)
def get_collective_offers(
    query: collective_offers_serialize.ListCollectiveOffersQueryModel,
) -> collective_offers_serialize.ListCollectiveOffersResponseModel:
    capped_offers = educational_api_offer.list_collective_offers_for_pro_user(
        user_id=current_user.id,
        user_is_admin=current_user.has_admin_role,
        offerer_id=query.offerer_id,
        venue_id=query.venue_id,
        name_keywords=query.nameOrIsbn,
        statuses=query.status,
        period_beginning_date=query.period_beginning_date,
        period_ending_date=query.period_ending_date,
        offer_type=query.collective_offer_type,
        #   The format should be a list but for now we cannot send a list in the get_collective_offers query params
        formats=[query.format] if query.format else None,
    )

    return collective_offers_serialize.ListCollectiveOffersResponseModel(
        __root__=collective_offers_serialize.serialize_collective_offers_capped(capped_offers)
    )


@private_api.route("/collective/offers/<int:offer_id>", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.GetCollectiveOfferResponseModel,
    api=blueprint.pro_private_schema,
)
def get_collective_offer(offer_id: int) -> collective_offers_serialize.GetCollectiveOfferResponseModel:
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        offer = educational_repository.get_collective_offer_by_id(offer_id)
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors(
            errors={"global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"]},
            status_code=404,
        )
    return collective_offers_serialize.GetCollectiveOfferResponseModel.from_orm(offer)


@private_api.route("/collective/offers-template/<int:offer_id>", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.GetCollectiveOfferTemplateResponseModel,
    api=blueprint.pro_private_schema,
)
def get_collective_offer_template(offer_id: int) -> collective_offers_serialize.GetCollectiveOfferTemplateResponseModel:
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_template_id(offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)
    try:
        offer = educational_repository.get_collective_offer_template_by_id(offer_id)
    except educational_exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors(
            errors={"global": ["Aucun objet ne correspond à cet identifiant dans notre base de données"]},
            status_code=404,
        )
    return collective_offers_serialize.GetCollectiveOfferTemplateResponseModel.from_orm(offer)


@private_api.route("/collective/offers-template/request/<int:request_id>", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.GetCollectiveOfferRequestResponseModel,
    api=blueprint.pro_private_schema,
)
def get_collective_offer_request(request_id: int) -> collective_offers_serialize.GetCollectiveOfferRequestResponseModel:
    try:
        collective_offer_request = educational_repository.get_collective_offer_request_by_id(request_id)
    except educational_exceptions.CollectiveOfferRequestNotFound:
        raise ApiErrors(errors={"global": ["Le formulaire demandé n'existe pas"]}, status_code=404)

    offerer_id = collective_offer_request.collectiveOfferTemplate.venue.managingOffererId
    check_user_has_access_to_offerer(current_user, offerer_id)

    institution = collective_offer_request.educationalInstitution
    return collective_offers_serialize.GetCollectiveOfferRequestResponseModel(
        redactor=collective_offers_serialize.CollectiveOfferRedactorModel(
            firstName=collective_offer_request.educationalRedactor.firstName,
            lastName=collective_offer_request.educationalRedactor.lastName,
            email=collective_offer_request.educationalRedactor.email,
        ),
        requestedDate=collective_offer_request.requestedDate,
        totalStudents=collective_offer_request.totalStudents,
        totalTeachers=collective_offer_request.totalTeachers,
        comment=collective_offer_request.comment,
        phoneNumber=collective_offer_request.phoneNumber,
        dateCreated=collective_offer_request.dateCreated,
        institution=collective_offers_serialize.CollectiveOfferInstitutionModel(
            institutionId=institution.institutionId,
            institutionType=institution.institutionType,
            name=institution.name,
            city=institution.city,
            postalCode=institution.postalCode,
        ),
    )


@private_api.route("/collective/offers", methods=["POST"])
@atomic()
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
        offer = educational_api_offer.create_collective_offer(offer_data=body, user=current_user)

    # venue / offerer errors
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    except educational_exceptions.VenueIdDontExist:
        logger.info(
            "Could not create offer: the venue id does not exist",
            extra={"venue_id": body.venue_id, "offer_venue": body.offer_venue},
        )
        raise ApiErrors({"venueId": "The venue does not exist."}, 404)

    # adage errors
    except educational_exceptions.CulturalPartnerNotFoundException:
        logger.info(
            "Could not create offer: This offerer has not been found in Adage", extra={"venue_id": body.venue_id}
        )
        raise ApiErrors({"offerer": "not found in adage"}, 403)
    except educational_exceptions.AdageException:
        logger.info("Could not create offer: Adage api call failed", extra={"venue_id": body.venue_id})
        raise ApiErrors({"adage_api": "error"}, 500)

    # domains / national_program errors
    except educational_exceptions.EducationalDomainsNotFound:
        logger.info(
            "Could not create offer: educational domains not found.",
            extra={"offer_name": body.name, "venue_id": body.venue_id, "domains": body.domains},
        )
        raise ApiErrors({"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}, status_code=404)
    except educational_exceptions.NationalProgramNotFound:
        logger.info(
            "Could not create offer: national program not found",
            extra={"offer_name": body.name, "nationalProgramId": body.nationalProgramId},
        )
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_NOT_FOUND"}, status_code=400)
    except educational_exceptions.IllegalNationalProgram:
        logger.info(
            "Could not create offer: invalid national program",
            extra={"offer_name": body.name, "nationalProgramId": body.nationalProgramId},
        )
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}, status_code=400)
    except educational_exceptions.InactiveNationalProgram:
        logger.info(
            "Could not create offer: inactive national program",
            extra={"offer_name": body.name, "nationalProgramId": body.nationalProgramId},
        )
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}, status_code=400)

    # creation error
    except educational_exceptions.CollectiveOfferTemplateForbiddenAction:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_TEMPLATE_FORBIDDEN_ACTION"}, status_code=403)
    except educational_exceptions.CollectiveOfferTemplateNotFound:
        logger.info(
            "Could not create offer: collective offer template not found.",
            extra={"offer_name": body.name, "venue_id": body.venue_id, "template_id": body.template_id},
        )
        raise ApiErrors({"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}, status_code=404)

    return collective_offers_serialize.CollectiveOfferResponseIdModel.from_orm(offer)


@private_api.route("/collective/offers/<int:offer_id>", methods=["PATCH"])
@atomic()
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.GetCollectiveOfferResponseModel,
    api=blueprint.pro_private_schema,
)
def edit_collective_offer(
    offer_id: int, body: collective_offers_serialize.PatchCollectiveOfferBodyModel
) -> collective_offers_serialize.GetCollectiveOfferResponseModel:
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    if not offerers_api.can_offerer_create_educational_offer(offerer.id):
        raise ApiErrors({"Partner": "User not in Adage can't edit the offer"}, status_code=403)

    try:
        educational_api_offer.update_collective_offer(offer_id=offer_id, body=body, user=current_user)

    # venue change errors
    except offers_exceptions.ForbiddenDestinationVenue:
        raise ApiErrors({"venueId": ["Ce partenaire culturel n'est pas éligible au transfert de l'offre"]}, 400)
    except offers_exceptions.OfferEventInThePast:
        raise ApiErrors({"offer": "This collective offer that has already started does not allow editing details"}, 403)
    except offers_exceptions.NoDestinationVenue:
        raise ApiErrors({"venueId": ["No venue with a pricing point found for the destination venue."]}, 400)

    # venue / offerer errors
    except educational_exceptions.OffererOfVenueDontMatchOfferer:
        raise ApiErrors({"venueId": "New venue needs to have the same offerer"}, 403)
    except educational_exceptions.VenueIdDontExist:
        raise ApiErrors({"venueId": "The venue does not exist."}, 404)

    # domains / national_program errors
    except educational_exceptions.NationalProgramNotFound:
        raise ApiErrors({"global": ["National program not found"]}, 400)
    except educational_exceptions.IllegalNationalProgram:
        logger.info(
            "Could not update offer: invalid national program",
            extra={"offer_name": body.name, "nationalProgramId": body.nationalProgramId},
        )
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}, status_code=400)
    except educational_exceptions.InactiveNationalProgram:
        logger.info(
            "Could not create offer: inactive national program",
            extra={"offer_name": body.name, "nationalProgramId": body.nationalProgramId},
        )
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}, status_code=400)
    except educational_exceptions.EducationalDomainsNotFound:
        logger.info(
            "Could not update offer: educational domains not found.",
            extra={"collective_offer_id": offer_id, "domains": body.domains},
        )
        raise ApiErrors({"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}, status_code=404)

    # edition errors
    except educational_exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors({"offer": "This collective offer status does not allow editing details"}, 403)
    except educational_exceptions.CollectiveOfferIsPublicApi:
        raise ApiErrors({"global": ["Collective offer created by public API is only editable via API."]}, 403)
    except (
        offers_exceptions.OfferException
    ) as error:  # (tcoudray-pass, 14/05/2025) TODO: Refactor, should not raise this kind of error
        raise ApiErrors(error.errors)

    offer = educational_repository.get_collective_offer_by_id(offer_id)
    return collective_offers_serialize.GetCollectiveOfferResponseModel.from_orm(offer)


@private_api.route("/collective/offers-template/<int:offer_id>", methods=["PATCH"])
@atomic()
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.GetCollectiveOfferTemplateResponseModel,
    api=blueprint.pro_private_schema,
)
def edit_collective_offer_template(
    offer_id: int, body: collective_offers_serialize.PatchCollectiveOfferTemplateBodyModel
) -> collective_offers_serialize.GetCollectiveOfferTemplateResponseModel:
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_template_id(offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    if not offerers_api.can_offerer_create_educational_offer(offerer.id):
        raise ApiErrors({"Partner": "User not in Adage can't edit the offer"}, status_code=403)

    try:
        educational_api_offer.update_collective_offer_template(offer_id=offer_id, body=body, user=current_user)

    # venue / offerer errors
    except educational_exceptions.VenueIdDontExist:
        raise ApiErrors({"venueId": "The venue does not exist."}, 404)
    except educational_exceptions.OffererOfVenueDontMatchOfferer:
        raise ApiErrors({"venueId": "New venue needs to have the same offerer"}, 403)

    # domains / national_program errors
    except educational_exceptions.NationalProgramNotFound:
        raise ApiErrors({"global": ["National program not found"]}, 400)
    except educational_exceptions.IllegalNationalProgram:
        logger.info(
            "Could not update offer: invalid national program",
            extra={"offer_name": body.name, "nationalProgramId": body.nationalProgramId},
        )
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}, status_code=400)
    except educational_exceptions.InactiveNationalProgram:
        logger.info(
            "Could not create offer: inactive national program",
            extra={"offer_name": body.name, "nationalProgramId": body.nationalProgramId},
        )
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}, status_code=400)
    except educational_exceptions.EducationalDomainsNotFound:
        logger.info(
            "Could not update offer: educational domains not found.",
            extra={"collective_offer_id": offer_id, "domains": body.domains},
        )
        raise ApiErrors({"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}, status_code=404)

    # edition errors
    except (
        offers_exceptions.OfferException
    ) as error:  # (tcoudray-pass, 14/05/2025) TODO: Refactor, should not raise this kind of error
        raise ApiErrors(error.errors)
    except educational_exceptions.CollectiveOfferTemplateForbiddenAction:
        raise ApiErrors({"global": ["Cette action n'est pas autorisée sur cette offre"]}, 403)
    except educational_exceptions.UpdateCollectiveOfferTemplateError as err:
        raise ApiErrors({err.field: err.msg}, 400)
    except offers_exceptions.CollectiveOfferContactRequestError as err:
        raise ApiErrors({f"contact[{err.fields}]": err.msg}, status_code=400)

    offer = educational_repository.get_collective_offer_template_by_id(offer_id)
    return collective_offers_serialize.GetCollectiveOfferTemplateResponseModel.from_orm(offer)


@private_api.route("/collective/offers/archive", methods=["PATCH"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def patch_collective_offers_archive(
    body: collective_offers_serialize.PatchCollectiveOfferArchiveBodyModel,
) -> None:
    collective_offers = educational_repository.get_query_for_collective_offers_by_ids_for_user(
        current_user, body.ids
    ).all()

    try:
        educational_api_offer.archive_collective_offers(offers=collective_offers, date_archived=datetime.utcnow())
    except educational_exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors({"global": ["Cette action n'est pas autorisée sur cette offre"]}, status_code=403)


@private_api.route("/collective/offers-template/active-status", methods=["PATCH"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def patch_collective_offers_template_active_status(
    body: collective_offers_serialize.PatchCollectiveOfferActiveStatusBodyModel,
) -> None:
    if body.is_active:
        offerers_ids = educational_repository.get_offerer_ids_from_collective_offers_template_ids(body.ids)
        for offerer_id in offerers_ids:
            if not offerers_api.can_offerer_create_educational_offer(offerer_id):
                raise ApiErrors({"Partner": ["User not in Adage can't edit the offer"]}, status_code=403)

    collective_offer_templates = educational_repository.get_query_for_collective_offers_template_by_ids_for_user(
        current_user, body.ids
    ).all()

    try:
        educational_api_offer.toggle_publish_collective_offers_template(
            collective_offers_templates=collective_offer_templates, is_active=body.is_active
        )
    except educational_exceptions.CollectiveOfferTemplateForbiddenAction:
        raise ApiErrors({"global": ["Cette action n'est pas autorisée sur cette offre"]}, status_code=403)


@private_api.route("/collective/offers-template/archive", methods=["PATCH"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def patch_collective_offers_template_archive(
    body: collective_offers_serialize.PatchCollectiveOfferArchiveBodyModel,
) -> None:
    collective_offer_templates = educational_repository.get_query_for_collective_offers_template_by_ids_for_user(
        current_user, body.ids
    ).all()

    try:
        educational_api_offer.archive_collective_offers_template(
            offers=collective_offer_templates, date_archived=datetime.utcnow()
        )
    except educational_exceptions.CollectiveOfferTemplateForbiddenAction:
        raise ApiErrors({"global": ["Cette action n'est pas autorisée sur cette offre"]}, status_code=403)


@private_api.route("/collective/offers/<int:offer_id>/educational_institution", methods=["PATCH"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=200,
    on_error_statuses=[403, 404],
    api=blueprint.pro_private_schema,
    response_model=collective_offers_serialize.GetCollectiveOfferResponseModel,
)
def patch_collective_offers_educational_institution(
    offer_id: int, body: collective_offers_serialize.PatchCollectiveOfferEducationalInstitution
) -> collective_offers_serialize.GetCollectiveOfferResponseModel:
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        offer = educational_api_offer.update_collective_offer_educational_institution(
            offer_id=offer_id,
            educational_institution_id=body.educational_institution_id,
            teacher_email=body.teacher_email,
        )
    except educational_exceptions.EducationalInstitutionNotFound:
        raise ApiErrors({"educationalInstitution": ["Aucune institution trouvée à partir de cet id"]}, status_code=404)
    except educational_exceptions.EducationalInstitutionIsNotActive:
        raise ApiErrors({"educationalInstitution": ["l'institution n'est pas active"]}, status_code=403)
    except educational_exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors({"offer": ["Cette action n'est pas autorisée sur cette offre"]}, status_code=403)
    except educational_exceptions.EducationalRedactorNotFound:
        raise ApiErrors({"teacherEmail": ["L'enseignant n'à pas été trouvé dans cet établissement."]}, status_code=404)

    return collective_offers_serialize.GetCollectiveOfferResponseModel.from_orm(offer)


@private_api.route("/collective/offers/<int:offer_id>/publish", methods=["PATCH"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=200,
    on_error_statuses=[403, 404],
    api=blueprint.pro_private_schema,
    response_model=collective_offers_serialize.GetCollectiveOfferResponseModel,
)
def patch_collective_offer_publication(offer_id: int) -> collective_offers_serialize.GetCollectiveOfferResponseModel:
    with transaction():
        with db.session.no_autoflush:
            offer = educational_repository.get_collective_offer_and_extra_data(offer_id)
            if offer is None:
                raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id"]}, status_code=404)

            check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

            offer = educational_api_offer.publish_collective_offer(offer=offer, user=current_user)

            return collective_offers_serialize.GetCollectiveOfferResponseModel.from_orm(offer)


@private_api.route("/collective/offers-template/<int:offer_id>/publish", methods=["PATCH"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=200,
    on_error_statuses=[403, 404],
    api=blueprint.pro_private_schema,
    response_model=collective_offers_serialize.GetCollectiveOfferTemplateResponseModel,
)
def patch_collective_offer_template_publication(
    offer_id: int,
) -> collective_offers_serialize.GetCollectiveOfferTemplateResponseModel:
    try:
        offer = educational_repository.get_collective_offer_template_by_id(offer_id)
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id"]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    offer = educational_api_offer.publish_collective_offer_template(offer_template=offer, user=current_user)

    return collective_offers_serialize.GetCollectiveOfferTemplateResponseModel.from_orm(offer)


@private_api.route("/collective/offers-template", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.CollectiveOfferResponseIdModel,
    on_success_status=201,
    api=blueprint.pro_private_schema,
)
def create_collective_offer_template(
    body: collective_offers_serialize.PostCollectiveOfferTemplateBodyModel,
) -> collective_offers_serialize.CollectiveOfferResponseIdModel:
    try:
        offer = educational_api_offer.create_collective_offer_template(offer_data=body, user=current_user)

    # venue / offerer errors
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    except educational_exceptions.VenueIdDontExist:
        logger.info(
            "Could not create offer: the venue id does not exist",
            extra={"venue_id": body.venue_id, "offer_venue": body.offer_venue},
        )
        raise ApiErrors({"venueId": "The venue does not exist."}, 404)

    # adage errors
    except educational_exceptions.CulturalPartnerNotFoundException:
        logger.info(
            "Could not create offer: This offerer has not been found in Adage", extra={"venue_id": body.venue_id}
        )
        raise ApiErrors({"offerer": "not found in adage"}, 403)
    except educational_exceptions.AdageException:
        logger.info("Could not create offer: Adage api call failed", extra={"venue_id": body.venue_id})
        raise ApiErrors({"adage_api": "error"}, 500)

    # domains / national_program errors
    except educational_exceptions.EducationalDomainsNotFound:
        logger.info(
            "Could not create offer: educational domains not found.",
            extra={"offer_name": body.name, "venue_id": body.venue_id, "domains": body.domains},
        )
        raise ApiErrors({"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}, status_code=404)
    except educational_exceptions.NationalProgramNotFound:
        logger.info(
            "Could not create offer: national program not found",
            extra={"offer_name": body.name, "nationalProgramId": body.nationalProgramId},
        )
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_NOT_FOUND"}, status_code=400)
    except educational_exceptions.IllegalNationalProgram:
        logger.info(
            "Could not create offer: invalid national program",
            extra={"offer_name": body.name, "nationalProgramId": body.nationalProgramId},
        )
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}, status_code=400)
    except educational_exceptions.InactiveNationalProgram:
        logger.info(
            "Could not create offer: inactive national program",
            extra={"offer_name": body.name, "nationalProgramId": body.nationalProgramId},
        )
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}, status_code=400)

    # creation errors
    except offers_exceptions.CollectiveOfferContactRequestError as err:
        raise ApiErrors({f"contact[{err.fields}]": err.msg}, status_code=400)

    return collective_offers_serialize.CollectiveOfferResponseIdModel.from_orm(offer)


def _check_image(image_as_bytes: bytes) -> None:
    try:
        offers_validation.check_image(
            image_as_bytes,
            accepted_types=offers_validation.ACCEPTED_THUMBNAIL_FORMATS,
            min_width=offers_validation.STANDARD_THUMBNAIL_WIDTH,
            min_height=offers_validation.STANDARD_THUMBNAIL_HEIGHT,
        )
    except offers_exceptions.UnacceptedFileType:
        raise ApiErrors(
            errors={
                "imageFile": [f"Les formats acceptés sont:  {', '.join(offers_validation.ACCEPTED_THUMBNAIL_FORMATS)}"]
            }
        )
    except offers_exceptions.ImageTooSmall:
        raise ApiErrors(
            errors={
                "imageFile": [
                    f"L'image doit faire au moins {offers_validation.STANDARD_THUMBNAIL_WIDTH} x "
                    f"{offers_validation.STANDARD_THUMBNAIL_HEIGHT} pixels"
                ]
            }
        )


@private_api.route("/collective/offers/<int:offer_id>/image", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=200,
    response_model=collective_offers_serialize.AttachImageResponseModel,
    api=blueprint.pro_private_schema,
)
def attach_offer_image(
    offer_id: int, form: collective_offers_serialize.AttachImageFormModel
) -> collective_offers_serialize.AttachImageResponseModel:
    try:
        offer = educational_repository.get_collective_offer_by_id(offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    try:
        educational_validation.check_collective_offer_action_is_allowed(
            offer, educational_models.CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
        )
    except educational_exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors({"global": ["Cette action n'est pas autorisée sur cette offre"]}, status_code=403)

    image_as_bytes = form.get_image_as_bytes(request)

    _check_image(image_as_bytes)

    try:
        educational_api_offer.attach_image(
            obj=offer,
            image=image_as_bytes,
            crop_params=form.crop_params,
            credit=form.credit,
        )
    except UnidentifiedImageError:
        raise ApiErrors({"image": "Impossible d'identifier l'image"}, status_code=400)

    return collective_offers_serialize.AttachImageResponseModel.from_orm(offer)


@private_api.route("/collective/offers-template/<int:offer_id>/image", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=200,
    response_model=collective_offers_serialize.AttachImageResponseModel,
    api=blueprint.pro_private_schema,
)
def attach_offer_template_image(
    offer_id: int, form: collective_offers_serialize.AttachImageFormModel
) -> collective_offers_serialize.AttachImageResponseModel:
    try:
        offer = educational_repository.get_collective_offer_template_by_id(offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    image_as_bytes = form.get_image_as_bytes(request)

    _check_image(image_as_bytes)

    try:
        educational_api_offer.attach_image(
            obj=offer,
            image=image_as_bytes,
            crop_params=form.crop_params,
            credit=form.credit,
        )
    except UnidentifiedImageError:
        raise ApiErrors({"image": "Impossible d'identifier l'image"}, status_code=400)

    return collective_offers_serialize.AttachImageResponseModel.from_orm(offer)


@private_api.route("/collective/offers/<int:offer_id>/image", methods=["DELETE"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def delete_offer_image(offer_id: int) -> None:
    try:
        offer = educational_repository.get_collective_offer_by_id(offer_id)
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    try:
        educational_validation.check_collective_offer_action_is_allowed(
            offer, educational_models.CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
        )
    except educational_exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors({"global": ["Cette action n'est pas autorisée sur cette offre"]}, status_code=403)

    educational_api_offer.delete_image(obj=offer)


@private_api.route("/collective/offers-template/<int:offer_id>/image", methods=["DELETE"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def delete_offer_template_image(offer_id: int) -> None:
    try:
        offer = educational_repository.get_collective_offer_template_by_id(offer_id)
    except educational_exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    educational_api_offer.delete_image(obj=offer)


@private_api.route("/collective/offers/redactors", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=educational_redactors.EducationalRedactors,
    api=blueprint.pro_private_schema,
)
def get_autocomplete_educational_redactors_for_uai(
    query: educational_redactors.EducationalRedactorQueryModel,
) -> educational_redactors.EducationalRedactors:
    try:
        redactors = educational_api_adage.autocomplete_educational_redactor_for_uai(
            uai=query.uai, candidate=query.candidate
        )
    except educational_exceptions.EducationalRedactorNotFound:
        raise ApiErrors({"UAI": ["UAI non trouvé."]}, status_code=404)

    return educational_redactors.EducationalRedactors(
        __root__=[
            educational_redactors.EducationalRedactor(
                name=redactor["nom"],
                surname=redactor["prenom"],
                gender=redactor.get("civilite"),
                email=redactor["mail"],
            )
            for redactor in redactors
        ]
    )


@private_api.route("/collective/offers/<int:offer_id>/duplicate", methods=["POST"])
@atomic()
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.GetCollectiveOfferResponseModel,
    on_success_status=201,
    api=blueprint.pro_private_schema,
)
def duplicate_collective_offer(
    offer_id: int,
) -> collective_offers_serialize.GetCollectiveOfferResponseModel:
    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        original_offer = educational_repository.get_collective_offer_by_id(offer_id)
    except educational_exceptions.CollectiveOfferNotFound:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id"]}, status_code=404)

    try:
        offer = educational_api_offer.duplicate_offer_and_stock(original_offer=original_offer)
    except educational_exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors({"validation": ["Cette action n'est pas autorisée sur cette offre"]}, status_code=403)
    except educational_exceptions.OffererNotAllowedToDuplicate:
        raise ApiErrors({"offerer": ["la structure n'est pas autorisée à dupliquer l'offre"]}, status_code=403)
    except educational_exceptions.CantGetImageFromUrl:
        raise ApiErrors({"image": ["l'image ne peut etre trouvé"]}, status_code=404)

    return collective_offers_serialize.GetCollectiveOfferResponseModel.from_orm(offer)
