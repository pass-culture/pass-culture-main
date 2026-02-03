from PIL import UnidentifiedImageError
from flask import request
from flask_login import current_user
from flask_login import login_required

from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.educational import schemas
from pcapi.core.educational import validation
from pcapi.core.educational.api import adage as api_adage
from pcapi.core.educational.api import export as api_export
from pcapi.core.educational.api import offer as api_offer
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import validation as offers_validation
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.routes.serialization import educational_redactors
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import date as date_utils
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.transaction_manager import atomic

from . import blueprint


def _get_filters_from_query(
    query: collective_offers_serialize.ListCollectiveOffersQueryModel,
) -> schemas.CollectiveOffersFilter:
    return schemas.CollectiveOffersFilter(
        user_id=current_user.id,
        offerer_id=query.offerer_id,
        venue_id=query.venue_id,
        name_keywords=query.name,
        statuses=query.status,
        period_beginning_date=query.period_beginning_date,
        period_ending_date=query.period_ending_date,
        formats=[query.format] if query.format else None,
        location_type=query.location_type,
        offerer_address_id=query.offerer_address_id,
    )


@private_api.route("/collective/bookable-offers", methods=["GET"])
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
    filters = _get_filters_from_query(query)
    offers = repository.list_collective_offers(filters=filters, offers_limit=api_offer.OFFERS_RECAP_LIMIT)
    offers.sort(key=lambda offer: offer.get_sort_criterion(), reverse=True)

    return collective_offers_serialize.ListCollectiveOffersResponseModel(
        __root__=[collective_offers_serialize.CollectiveOfferResponseModel.build(offer) for offer in offers]
    )


@private_api.route("/collective/offers-template", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=collective_offers_serialize.ListCollectiveOfferTemplatesResponseModel,
    api=blueprint.pro_private_schema,
    query_params_as_list=["status"],
)
def get_collective_offer_templates(
    query: collective_offers_serialize.ListCollectiveOffersQueryModel,
) -> collective_offers_serialize.ListCollectiveOfferTemplatesResponseModel:
    filters = _get_filters_from_query(query)
    offers = repository.list_collective_offer_templates(filters=filters, offers_limit=api_offer.OFFERS_RECAP_LIMIT)

    return collective_offers_serialize.ListCollectiveOfferTemplatesResponseModel(
        __root__=[collective_offers_serialize.CollectiveOfferTemplateResponseModel.build(offer) for offer in offers]
    )


@private_api.route("/collective/offers/csv", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "text/csv; charset=utf-8-sig;",
        "Content-Disposition": "attachment; filename=offres_collectives_reservables_pass_culture.csv",
    },
    api=blueprint.pro_private_schema,
)
def get_collective_offers_csv(
    query: collective_offers_serialize.ListCollectiveOffersQueryModel,
) -> bytes:
    return _get_collective_offers_export(query, models.CollectiveOfferExportType.CSV)


@private_api.route("/collective/offers/excel", methods=["GET"])
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "application/vnd.ms-excel",
        "Content-Disposition": "attachment; filename=offres_collectives_reservables_pass_culture.xlsx",
    },
    api=blueprint.pro_private_schema,
)
@atomic()
def get_collective_offers_excel(
    query: collective_offers_serialize.ListCollectiveOffersQueryModel,
) -> bytes:
    return _get_collective_offers_export(query, models.CollectiveOfferExportType.EXCEL)


def _get_collective_offers_export(
    query: collective_offers_serialize.ListCollectiveOffersQueryModel,
    export_type: models.CollectiveOfferExportType,
) -> bytes:
    filters = _get_filters_from_query(query)
    offers_query = repository.get_collective_offers_by_filters(filters=filters)

    if export_type == models.CollectiveOfferExportType.CSV:
        return api_export.generate_csv_for_collective_offers(collective_offers_query=offers_query)

    return api_export.generate_excel_for_collective_offers(collective_offers_query=offers_query)


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
        offer = repository.get_collective_offer_by_id(offer_id)
    except exceptions.CollectiveOfferNotFound:
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
        offer = repository.get_collective_offer_template_by_id(offer_id)
    except exceptions.CollectiveOfferTemplateNotFound:
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
        collective_offer_request = repository.get_collective_offer_request_by_id(request_id)
    except exceptions.CollectiveOfferRequestNotFound:
        raise ApiErrors(errors={"global": ["Le formulaire demandé n'existe pas"]}, status_code=404)

    offerer_id = collective_offer_request.collectiveOfferTemplate.venue.managingOffererId
    check_user_has_access_to_offerer(current_user, offerer_id)

    return collective_offers_serialize.GetCollectiveOfferRequestResponseModel.model_validate(collective_offer_request)


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
        offer = api_offer.create_collective_offer(offer_data=body, user=current_user)

    # venue / offerer errors
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    except exceptions.VenueIdDoesNotExist:
        raise ApiErrors({"venueId": "The venue does not exist."}, 404)

    # adage errors
    except exceptions.CulturalPartnerNotFoundException:
        raise ApiErrors({"offerer": "not found in adage"}, 403)
    except exceptions.AdageException:
        raise ApiErrors({"adage_api": "error"}, 500)

    # domains / national_program errors
    except exceptions.EducationalDomainsNotFound:
        raise ApiErrors({"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}, status_code=404)
    except exceptions.NationalProgramNotFound:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_NOT_FOUND"}, status_code=400)
    except exceptions.IllegalNationalProgram:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}, status_code=400)
    except exceptions.InactiveNationalProgram:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}, status_code=400)

    # creation error
    except exceptions.CollectiveOfferTemplateForbiddenAction:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_TEMPLATE_FORBIDDEN_ACTION"}, status_code=403)
    except exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}, status_code=404)

    return collective_offers_serialize.CollectiveOfferResponseIdModel(id=offer.id)


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
        api_offer.update_collective_offer(offer_id=offer_id, body=body)

    # venue change errors
    except offers_exceptions.ForbiddenDestinationVenue:
        raise ApiErrors({"venueId": ["Ce partenaire culturel n'est pas éligible au transfert de l'offre"]}, 400)
    except offers_exceptions.OfferEventInThePast:
        raise ApiErrors({"offer": "This collective offer that has already started does not allow editing details"}, 403)
    except offers_exceptions.NoDestinationVenue:
        raise ApiErrors({"venueId": ["No venue with a pricing point found for the destination venue."]}, 400)

    # venue / offerer errors
    except exceptions.OffererOfVenueDontMatchOfferer:
        raise ApiErrors({"venueId": "New venue needs to have the same offerer"}, 403)
    except exceptions.VenueIdDoesNotExist:
        raise ApiErrors({"venueId": "The venue does not exist."}, 404)

    # domains / national_program errors
    except exceptions.NationalProgramNotFound:
        raise ApiErrors({"global": ["National program not found"]}, 400)
    except exceptions.IllegalNationalProgram:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}, status_code=400)
    except exceptions.InactiveNationalProgram:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}, status_code=400)
    except exceptions.EducationalDomainsNotFound:
        raise ApiErrors({"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}, status_code=404)

    # edition errors
    except exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors({"offer": "This collective offer status does not allow editing details"}, 403)
    except exceptions.CollectiveOfferIsPublicApi:
        raise ApiErrors({"global": ["Collective offer created by public API is only editable via API."]}, 403)
    except (
        offers_exceptions.OfferException
    ) as error:  # (tcoudray-pass, 14/05/2025) TODO: Refactor, should not raise this kind of error
        raise ApiErrors(error.errors)

    offer = repository.get_collective_offer_by_id(offer_id)
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
        api_offer.update_collective_offer_template(offer_id=offer_id, body=body)

    # venue / offerer errors
    except exceptions.VenueIdDoesNotExist:
        raise ApiErrors({"venueId": "The venue does not exist."}, 404)
    except exceptions.OffererOfVenueDontMatchOfferer:
        raise ApiErrors({"venueId": "New venue needs to have the same offerer"}, 403)

    # domains / national_program errors
    except exceptions.NationalProgramNotFound:
        raise ApiErrors({"global": ["National program not found"]}, 400)
    except exceptions.IllegalNationalProgram:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}, status_code=400)
    except exceptions.InactiveNationalProgram:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}, status_code=400)
    except exceptions.EducationalDomainsNotFound:
        raise ApiErrors({"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}, status_code=404)

    # edition errors
    except (
        offers_exceptions.OfferException
    ) as error:  # (tcoudray-pass, 14/05/2025) TODO: Refactor, should not raise this kind of error
        raise ApiErrors(error.errors)
    except exceptions.CollectiveOfferTemplateForbiddenAction:
        raise ApiErrors({"global": ["Cette action n'est pas autorisée sur cette offre"]}, 403)
    except exceptions.UpdateCollectiveOfferTemplateError as err:
        raise ApiErrors({err.field: err.msg}, 400)
    except exceptions.CollectiveOfferContactRequestError as err:
        raise ApiErrors({f"contact[{err.fields}]": err.msg}, status_code=400)

    offer = repository.get_collective_offer_template_by_id(offer_id)
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
    collective_offers = repository.get_query_for_collective_offers_by_ids_for_user(current_user, body.ids).all()

    try:
        api_offer.archive_collective_offers(offers=collective_offers, date_archived=date_utils.get_naive_utc_now())
    except exceptions.CollectiveOfferForbiddenAction:
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
        offerers_ids = repository.get_offerer_ids_from_collective_offers_template_ids(body.ids)
        for offerer_id in offerers_ids:
            if not offerers_api.can_offerer_create_educational_offer(offerer_id):
                raise ApiErrors({"Partner": ["User not in Adage can't edit the offer"]}, status_code=403)

    collective_offer_templates = repository.get_query_for_collective_offers_template_by_ids_for_user(
        current_user, body.ids
    ).all()

    try:
        api_offer.toggle_publish_collective_offers_template(
            collective_offers_templates=collective_offer_templates, is_active=body.is_active
        )
    except exceptions.CollectiveOfferTemplateForbiddenAction:
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
    collective_offer_templates = repository.get_query_for_collective_offers_template_by_ids_for_user(
        current_user, body.ids
    ).all()

    try:
        api_offer.archive_collective_offers_template(
            offers=collective_offer_templates, date_archived=date_utils.get_naive_utc_now()
        )
    except exceptions.CollectiveOfferTemplateForbiddenAction:
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
        offer = api_offer.update_collective_offer_educational_institution(
            offer_id=offer_id,
            educational_institution_id=body.educational_institution_id,
            teacher_email=body.teacher_email,
        )
    except exceptions.EducationalInstitutionNotFound:
        raise ApiErrors({"educationalInstitution": ["Aucune institution trouvée à partir de cet id"]}, status_code=404)
    except exceptions.EducationalInstitutionIsNotActive:
        raise ApiErrors({"educationalInstitution": ["l'institution n'est pas active"]}, status_code=403)
    except exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors({"offer": ["Cette action n'est pas autorisée sur cette offre"]}, status_code=403)
    except exceptions.EducationalRedactorNotFound:
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
    offer = repository.get_collective_offer_and_confidence_rules(offer_id)
    if offer is None:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id"]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    offer = api_offer.publish_collective_offer(offer=offer, user=current_user)

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
        offer = repository.get_collective_offer_template_by_id(offer_id)
    except exceptions.CollectiveOfferNotFound:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id"]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    offer = api_offer.publish_collective_offer_template(offer_template=offer, user=current_user)

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
        offer = api_offer.create_collective_offer_template(offer_data=body, user=current_user)

    # venue / offerer errors
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune structure trouvée à partir de cette offre"]}, status_code=404)
    except exceptions.VenueIdDoesNotExist:
        raise ApiErrors({"venueId": "The venue does not exist."}, 404)

    # adage errors
    except exceptions.CulturalPartnerNotFoundException:
        raise ApiErrors({"offerer": "not found in adage"}, 403)
    except exceptions.AdageException:
        raise ApiErrors({"adage_api": "error"}, 500)

    # domains / national_program errors
    except exceptions.EducationalDomainsNotFound:
        raise ApiErrors({"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}, status_code=404)
    except exceptions.NationalProgramNotFound:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_NOT_FOUND"}, status_code=400)
    except exceptions.IllegalNationalProgram:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}, status_code=400)
    except exceptions.InactiveNationalProgram:
        raise ApiErrors({"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}, status_code=400)

    # creation errors
    except exceptions.CollectiveOfferContactRequestError as err:
        raise ApiErrors({f"contact[{err.fields}]": err.msg}, status_code=400)

    return collective_offers_serialize.CollectiveOfferResponseIdModel(id=offer.id)


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
        offer = repository.get_collective_offer_by_id(offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    try:
        validation.check_collective_offer_action_is_allowed(offer, models.CollectiveOfferAllowedAction.CAN_EDIT_DETAILS)
    except exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors({"global": ["Cette action n'est pas autorisée sur cette offre"]}, status_code=403)

    image_as_bytes = form.get_image_as_bytes(request)

    _check_image(image_as_bytes)

    try:
        api_offer.attach_image(
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
        offer = repository.get_collective_offer_template_by_id(offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    image_as_bytes = form.get_image_as_bytes(request)

    _check_image(image_as_bytes)

    try:
        api_offer.attach_image(
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
        offer = repository.get_collective_offer_by_id(offer_id)
    except exceptions.CollectiveOfferNotFound:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    try:
        validation.check_collective_offer_action_is_allowed(offer, models.CollectiveOfferAllowedAction.CAN_EDIT_DETAILS)
    except exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors({"global": ["Cette action n'est pas autorisée sur cette offre"]}, status_code=403)

    api_offer.delete_image(obj=offer)


@private_api.route("/collective/offers-template/<int:offer_id>/image", methods=["DELETE"])
@atomic()
@login_required
@spectree_serialize(
    on_success_status=204,
    api=blueprint.pro_private_schema,
)
def delete_offer_template_image(offer_id: int) -> None:
    try:
        offer = repository.get_collective_offer_template_by_id(offer_id)
    except exceptions.CollectiveOfferTemplateNotFound:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id."]}, status_code=404)

    check_user_has_access_to_offerer(current_user, offer.venue.managingOffererId)

    api_offer.delete_image(obj=offer)


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
        redactors = api_adage.autocomplete_educational_redactor_for_uai(uai=query.uai, candidate=query.candidate)
    except exceptions.EducationalRedactorNotFound:
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
        original_offer = repository.get_collective_offer_by_id(offer_id)
    except exceptions.CollectiveOfferNotFound:
        raise ApiErrors({"offerer": ["Aucune offre trouvée pour cet id"]}, status_code=404)

    try:
        offer = api_offer.duplicate_offer_and_stock(original_offer=original_offer)
    except exceptions.CollectiveOfferForbiddenAction:
        raise ApiErrors({"validation": ["Cette action n'est pas autorisée sur cette offre"]}, status_code=403)
    except exceptions.OffererNotAllowedToDuplicate:
        raise ApiErrors({"offerer": ["la structure n'est pas autorisée à dupliquer l'offre"]}, status_code=403)
    except exceptions.CantGetImageFromUrl:
        raise ApiErrors({"image": ["l'image ne peut etre trouvé"]}, status_code=404)

    return collective_offers_serialize.GetCollectiveOfferResponseModel.from_orm(offer)
