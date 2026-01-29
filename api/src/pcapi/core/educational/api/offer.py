import dataclasses
import datetime
import logging
import typing
from functools import partial

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.core import search
from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.core.educational import repository
from pcapi.core.educational import schemas
from pcapi.core.educational import utils
from pcapi.core.educational import validation
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer_request
from pcapi.core.educational.api import adage as api_adage
from pcapi.core.educational.api import shared as api_shared
from pcapi.core.educational.serialization import collective_booking as collective_booking_serialize
from pcapi.core.educational.utils import get_image_from_url
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.object_storage import store_public_object
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offer_validation
from pcapi.core.search.models import IndexationReason
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models import feature
from pcapi.models import offer_mixin
from pcapi.models import validation_status_mixin
from pcapi.models.utils import get_or_404
from pcapi.routes.adage_iframe.serialization.offers import PostCollectiveRequestBodyModel
from pcapi.routes.public import utils as public_utils
from pcapi.routes.public.collective.serialization import offers as public_api_collective_offers_serialize
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.utils import date as date_utils
from pcapi.utils import image_conversion
from pcapi.utils import rest
from pcapi.utils.transaction_manager import is_managed_transaction
from pcapi.utils.transaction_manager import on_commit


logger = logging.getLogger(__name__)
OFFERS_RECAP_LIMIT = 101


AnyCollectiveOffer = models.CollectiveOffer | models.CollectiveOfferTemplate


def get_or_create_offerer_address_from_collective_offer_location(
    location_body: collective_offers_serialize.CollectiveOfferLocationModel | None,
    venue: offerers_models.Venue,
) -> offerers_models.OffererAddress | None:
    if not location_body or not location_body.location:
        return None

    address_body: offerers_schemas.LocationOnlyOnVenueModel | offerers_schemas.LocationModel
    if location_body.location.isVenueLocation:
        address_body = offerers_schemas.LocationOnlyOnVenueModel()
    else:
        address_body = offerers_schemas.LocationModel(**location_body.location.dict())

    if not address_body:
        return None

    return offers_api.get_or_create_offerer_address_from_address_body(
        address_body=address_body,
        venue=venue,
    )


def notify_educational_redactor_on_collective_offer_or_stock_edit(
    collective_offer_id: int,
    updated_fields: list[str],
) -> None:
    if len(updated_fields) == 0:
        return

    active_collective_bookings = repository.find_active_collective_booking_by_offer_id(collective_offer_id)
    if active_collective_bookings is None:
        return

    data = schemas.EducationalBookingEdition(
        **collective_booking_serialize.serialize_collective_booking(active_collective_bookings).dict(),
        updatedFields=updated_fields,
    )
    try:
        adage_client.notify_offer_or_stock_edition(data)
    except exceptions.AdageException as exception:
        logger.error(
            "Error while sending notification to Adage",
            extra={
                "adage_response_message": exception.message,
                "adage_response_status_code": exception.status_code,
                "adage_response_response_text": exception.response_text,
                "data": data.dict(),
            },
        )


def unindex_expired_or_archived_collective_offers_template(process_all_expired: bool = False) -> None:
    """Unindex collective offers template that have expired or are archived."""
    page = 0
    limit = settings.ALGOLIA_DELETING_COLLECTIVE_OFFERS_CHUNK_SIZE
    while collective_offer_template_ids := _get_expired_or_archived_collective_offer_template_ids(page, limit):
        logger.info(
            "[ALGOLIA] Found %d expired collective offers template to unindex",
            len(collective_offer_template_ids),
        )
        search.unindex_collective_offer_template_ids(collective_offer_template_ids)
        page += 1


def get_educational_domains_from_ids(educational_domain_ids: list[int] | None) -> list[models.EducationalDomain]:
    if educational_domain_ids is None:
        return []

    unique_educational_domain_ids = set(educational_domain_ids)
    educational_domains = repository.get_educational_domains_from_ids(unique_educational_domain_ids)

    if len(educational_domains) < len(unique_educational_domain_ids):
        raise exceptions.EducationalDomainsNotFound()

    return educational_domains


@dataclasses.dataclass
class CollectiveOfferLocation:
    location_type: models.CollectiveLocationType
    location_comment: str | None
    offerer_address: offerers_models.OffererAddress | None


def create_collective_offer_template(
    offer_data: collective_offers_serialize.PostCollectiveOfferTemplateBodyModel, user: User
) -> models.CollectiveOfferTemplate:
    venue = get_venue_and_check_access_for_offer_creation(offer_data, user)

    # check domains and national program
    educational_domains = get_educational_domains_from_ids(offer_data.domains)
    validation.validate_national_program(national_program_id=offer_data.nationalProgramId, domains=educational_domains)

    offerer_address = get_or_create_offerer_address_from_collective_offer_location(offer_data.location, venue)

    collective_offer_template = models.CollectiveOfferTemplate(
        venueId=venue.id,
        name=offer_data.name,
        description=offer_data.description,
        domains=educational_domains,
        nationalProgramId=offer_data.nationalProgramId,
        durationMinutes=offer_data.duration_minutes,
        students=offer_data.students,
        contactEmail=offer_data.contact_email,
        contactPhone=offer_data.contact_phone,
        contactUrl=offer_data.contact_url,
        contactForm=offer_data.contact_form,
        validation=offer_mixin.OfferValidationStatus.DRAFT,
        audioDisabilityCompliant=offer_data.audio_disability_compliant,
        mentalDisabilityCompliant=offer_data.mental_disability_compliant,
        motorDisabilityCompliant=offer_data.motor_disability_compliant,
        visualDisabilityCompliant=offer_data.visual_disability_compliant,
        interventionArea=offer_data.intervention_area or [],
        priceDetail=offer_data.price_detail,
        bookingEmails=offer_data.booking_emails,
        formats=offer_data.formats,
        author=user,
        locationType=offer_data.location.locationType if offer_data.location else None,
        locationComment=offer_data.location.locationComment if offer_data.location else None,
        offererAddressId=offerer_address.id if offerer_address else None,
    )

    validation.check_contact_request(offer=collective_offer_template, updates={})

    if offer_data.dates:
        # this is necessary to pass constraint template_dates_non_empty_daterange
        # currently this only happens when selecting time = 23h59
        collective_offer_template.dateRange = utils.get_non_empty_date_time_range(
            offer_data.dates.start, offer_data.dates.end
        )

    db.session.add(collective_offer_template)
    db.session.flush()

    logger.info(
        "Collective offer template has been created", extra={"collectiveOfferTemplate": collective_offer_template.id}
    )
    return collective_offer_template


def create_collective_offer(
    offer_data: collective_offers_serialize.PostCollectiveOfferBodyModel, user: User, offer_id: int | None = None
) -> models.CollectiveOffer:
    venue = get_venue_and_check_access_for_offer_creation(offer_data, user)

    if offer_data.template_id is not None:
        template = repository.get_collective_offer_template_by_id(offer_data.template_id)
        validation.check_collective_offer_template_action_is_allowed(
            template, models.CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER
        )

    # check domains and national program
    educational_domains = get_educational_domains_from_ids(offer_data.domains)
    national_program_id = offer_data.nationalProgramId
    try:
        validation.validate_national_program(national_program_id=national_program_id, domains=educational_domains)
    except (exceptions.InactiveNationalProgram, exceptions.IllegalNationalProgram):
        if offer_data.template_id is not None:
            # original offer template may have invalid national_program, in this case we set program to None
            national_program_id = None
        else:
            # if we are not creating from an offer template, we do not allow an invalid program
            raise

    offerer_address = get_or_create_offerer_address_from_collective_offer_location(offer_data.location, venue)

    collective_offer = models.CollectiveOffer(
        isActive=False,  # a DRAFT offer cannot be active
        venueId=venue.id,
        name=offer_data.name,
        description=offer_data.description,
        domains=educational_domains,
        nationalProgramId=national_program_id,
        durationMinutes=offer_data.duration_minutes,
        students=offer_data.students,
        contactEmail=offer_data.contact_email,
        contactPhone=offer_data.contact_phone,
        validation=offer_mixin.OfferValidationStatus.DRAFT,
        audioDisabilityCompliant=offer_data.audio_disability_compliant,
        mentalDisabilityCompliant=offer_data.mental_disability_compliant,
        motorDisabilityCompliant=offer_data.motor_disability_compliant,
        visualDisabilityCompliant=offer_data.visual_disability_compliant,
        interventionArea=offer_data.intervention_area or [],
        templateId=offer_data.template_id,
        bookingEmails=offer_data.booking_emails,
        formats=offer_data.formats,
        author=user,
        locationType=offer_data.location.locationType if offer_data.location else None,
        locationComment=offer_data.location.locationComment if offer_data.location else None,
        offererAddressId=offerer_address.id if offerer_address else None,
    )

    # we update pro email data in sendinblue
    for email in collective_offer.bookingEmails:
        update_external_pro(email)

    db.session.add(collective_offer)
    db.session.flush()

    logger.info(
        "Collective offer has been created",
        extra={"collectiveOffer": collective_offer.id, "offerId": offer_id},
    )
    return collective_offer


def get_venue_and_check_access_for_offer_creation(
    offer_data: collective_offers_serialize.PostCollectiveOfferBodyModel,
    user: User,
) -> offerers_models.Venue:
    if offer_data.template_id is not None:
        template = repository.get_collective_offer_template_by_id(offer_data.template_id)
        rest.check_user_has_access_to_offerer(user, offerer_id=template.venue.managingOffererId)
    venue: offerers_models.Venue = get_or_404(offerers_models.Venue, offer_data.venue_id)

    rest.check_user_has_access_to_offerer(user, offerer_id=venue.managingOffererId)
    if not offerers_api.can_offerer_create_educational_offer(venue.managingOffererId):
        raise exceptions.CulturalPartnerNotFoundException("No venue has been found for the selected siren")

    return venue


def update_collective_offer_educational_institution(
    offer_id: int, educational_institution_id: int, teacher_email: str | None
) -> models.CollectiveOffer:
    offer = repository.get_collective_offer_by_id(offer_id)

    validation.check_collective_offer_action_is_allowed(offer, models.CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION)

    new_institution = validation.check_institution_id_exists(educational_institution_id)
    if not new_institution.isActive:
        raise exceptions.EducationalInstitutionIsNotActive()

    offer.institution = new_institution
    offer.teacher = None

    if teacher_email:
        possible_teachers = api_adage.autocomplete_educational_redactor_for_uai(
            uai=offer.institution.institutionId,
            candidate=teacher_email,
            use_email=True,
        )
        for teacher in possible_teachers:
            if teacher["mail"] == teacher_email:
                redactor = repository.find_redactor_by_email(teacher["mail"])
                if not redactor:
                    redactor = models.EducationalRedactor(
                        email=teacher["mail"],
                        firstName=teacher["prenom"],
                        lastName=teacher["nom"],
                        civility=teacher["civilite"],
                    )
                offer.teacher = redactor
                break
        else:
            raise exceptions.EducationalRedactorNotFound()

    db.session.flush()

    if offer.validation == offer_mixin.OfferValidationStatus.APPROVED:
        on_commit(partial(adage_client.notify_institution_association, serialize_collective_offer(offer)))

    return offer


def _get_location_from_public_model(
    location_body: public_api_collective_offers_serialize.CollectiveOfferLocation,
    venue: offerers_models.Venue,
) -> CollectiveOfferLocation:
    match location_body:
        case public_api_collective_offers_serialize.CollectiveOfferLocationSchoolModel():
            location = CollectiveOfferLocation(
                location_type=models.CollectiveLocationType.SCHOOL,
                location_comment=None,
                offerer_address=None,
            )

        case public_api_collective_offers_serialize.CollectiveOfferLocationToBeDefinedModel():
            location = CollectiveOfferLocation(
                location_type=models.CollectiveLocationType.TO_BE_DEFINED,
                location_comment=location_body.comment,
                offerer_address=None,
            )

        case public_api_collective_offers_serialize.CollectiveOfferLocationAddressVenueModel():
            offerer_address = offerers_api.get_or_create_offer_location(
                offerer_id=venue.managingOffererId,
                address_id=venue.offererAddress.addressId,
                label=venue.common_name,
            )
            location = CollectiveOfferLocation(
                location_type=models.CollectiveLocationType.ADDRESS,
                location_comment=None,
                offerer_address=offerer_address,
            )

        case public_api_collective_offers_serialize.CollectiveOfferLocationAddressModel():
            address = public_utils.get_address_or_raise_404(location_body.addressId)
            offerer_address = offerers_api.get_or_create_offer_location(
                offerer_id=venue.managingOffererId,
                address_id=address.id,
                label=location_body.addressLabel,
            )

            location = CollectiveOfferLocation(
                location_type=models.CollectiveLocationType.ADDRESS,
                location_comment=None,
                offerer_address=offerer_address,
            )

        case _:
            raise ValueError("Unexpected location body")

    return location


def create_collective_offer_public(
    requested_id: int,
    body: public_api_collective_offers_serialize.PostCollectiveOfferBodyModel,
) -> models.CollectiveOffer:
    venue = repository.fetch_venue_for_new_offer(body.venue_id, requested_id)
    if not offerers_api.can_offerer_create_educational_offer(venue.managingOffererId):
        raise exceptions.CulturalPartnerNotFoundException("No venue has been found for the selected siren")

    # check domains and national program
    educational_domains = get_educational_domains_from_ids(body.domains)
    validation.validate_national_program(body.national_program_id, educational_domains)

    institution = repository.get_educational_institution_public(
        institution_id=body.educational_institution_id,
        uai=body.educational_institution,
    )
    if not institution:
        raise exceptions.EducationalInstitutionUnknown()
    if not institution.isActive:
        raise exceptions.EducationalInstitutionIsNotActive()

    end_datetime = body.end_datetime or body.start_datetime
    validation.check_start_and_end_dates_in_same_educational_year(body.start_datetime, end_datetime)

    location = _get_location_from_public_model(location_body=body.location, venue=venue)

    collective_offer = models.CollectiveOffer(
        venue=venue,
        name=body.name,
        description=body.description,
        contactEmail=body.contact_email,
        contactPhone=body.contact_phone,
        domains=educational_domains,
        durationMinutes=body.duration_minutes,
        students=typing.cast(  # type transformation done by the validator (and not detected by mypy)
            list[models.StudentLevels], body.students
        ),
        audioDisabilityCompliant=body.audio_disability_compliant,
        mentalDisabilityCompliant=body.mental_disability_compliant,
        motorDisabilityCompliant=body.motor_disability_compliant,
        visualDisabilityCompliant=body.visual_disability_compliant,
        interventionArea=[],
        institution=institution,
        providerId=requested_id,
        nationalProgramId=body.national_program_id,
        formats=body.formats,
        bookingEmails=body.booking_emails,
        locationType=location.location_type,
        locationComment=location.location_comment,
        offererAddressId=location.offerer_address.id if location.offerer_address else None,
    )

    collective_stock = models.CollectiveStock(
        collectiveOffer=collective_offer,
        startDatetime=body.start_datetime,
        endDatetime=end_datetime,
        bookingLimitDatetime=body.booking_limit_datetime,
        price=body.total_price,
        numberOfTickets=body.number_of_tickets,
        priceDetail=body.price_detail,
    )

    offers_api.update_offer_fraud_information(offer=collective_offer, user=None)

    db.session.add(collective_offer)
    db.session.add(collective_stock)
    db.session.flush()

    logger.info("Collective offer has been created", extra={"offerId": collective_offer.id})

    return collective_offer


def edit_collective_offer_public(
    provider_id: int,
    new_values: dict,
    offer: models.CollectiveOffer,
    location_body: public_api_collective_offers_serialize.CollectiveOfferLocation | None,
) -> models.CollectiveOffer:
    if provider_id != offer.providerId:
        raise exceptions.CollectiveOfferNotEditable()

    offer_fields = {field for field in dir(models.CollectiveOffer) if not field.startswith("_")}
    stock_fields = {field for field in dir(models.CollectiveStock) if not field.startswith("_")}

    start_datetime = new_values.get("startDatetime")
    end_datetime = new_values.get("endDatetime")
    booking_limit_datetime = new_values.get("bookingLimitDatetime")

    # we need to compare the input dates with the current stock dates if we only receive some dates
    after_update_start_datetime = start_datetime or offer.collectiveStock.startDatetime
    after_update_end_datetime = end_datetime or offer.collectiveStock.endDatetime
    after_update_booking_limit_datetime = booking_limit_datetime or offer.collectiveStock.bookingLimitDatetime

    if start_datetime or end_datetime:
        validation.check_start_and_end_dates_in_same_educational_year(
            start_datetime=after_update_start_datetime, end_datetime=after_update_end_datetime
        )

        validation.check_start_is_before_end(
            start_datetime=after_update_start_datetime, end_datetime=after_update_end_datetime
        )

    if start_datetime or booking_limit_datetime:
        offer_validation.check_booking_limit_datetime(
            stock=offer.collectiveStock,
            beginning=after_update_start_datetime,
            booking_limit_datetime=after_update_booking_limit_datetime,
        )

    if location_body is not None:
        location = _get_location_from_public_model(location_body=location_body, venue=offer.venue)

        new_values["locationType"] = location.location_type
        new_values["locationComment"] = location.location_comment
        new_values["offererAddressId"] = location.offerer_address.id if location.offerer_address else None
        new_values.pop("location", None)

    # check domains and national program
    domains_to_check = offer.domains
    edit_domains = "domains" in new_values
    if edit_domains:
        domain_ids = new_values.pop("domains")
        new_values["domains"] = get_educational_domains_from_ids(domain_ids)
        domains_to_check = new_values["domains"]

    program_id_to_check = offer.nationalProgramId
    edit_national_program = "nationalProgramId" in new_values
    if edit_national_program:
        program_id_to_check = new_values["nationalProgramId"]

    if edit_domains or edit_national_program:
        validation.validate_national_program(national_program_id=program_id_to_check, domains=domains_to_check)

    # This variable is meant for Adage mailing
    updated_fields = []
    for key, value in new_values.items():
        updated_fields.append(key)

        if key in ("educationalInstitutionId", "educationalInstitution"):
            if value is None:
                continue

            institution = repository.get_educational_institution_public(
                institution_id=new_values.get("educationalInstitutionId"),
                uai=new_values.get("educationalInstitution"),
            )

            if not institution:
                raise exceptions.EducationalInstitutionUnknown()
            if not institution.isActive:
                raise exceptions.EducationalInstitutionIsNotActive()

            offer.institution = institution
        elif key == "bookingLimitDatetime" and value is None:
            offer.collectiveStock.bookingLimitDatetime = new_values.get(
                "startDatetime", offer.collectiveStock.startDatetime
            )
        elif key in stock_fields:
            setattr(offer.collectiveStock, key, value)
        elif key in offer_fields:
            setattr(offer, key, value)
        else:
            raise ValueError(f"unknown field {key}")

    current_booking = offer.collectiveStock.get_unique_non_cancelled_booking()
    api_shared.update_collective_stock_booking(
        stock=offer.collectiveStock,
        current_booking=current_booking,
        start_datetime_has_changed="startDatetime" in new_values,
    )

    db.session.flush()

    on_commit(
        partial(
            notify_educational_redactor_on_collective_offer_or_stock_edit,
            offer.id,
            updated_fields,
        )
    )
    return offer


PATCH_INSTITUTION_FIELDS_PUBLIC = ("educationalInstitutionId", "educationalInstitution")
PATCH_DATES_FIELDS_PUBLIC = ("startDatetime", "endDatetime", "bookingLimitDatetime")
PATCH_DISCOUNT_FIELDS_PUBLIC = ("numberOfTickets", "priceDetail")

# fields of public schema PatchCollectiveOfferBodyModel that correspond to CAN_EDIT_DETAILS
# i.e all the fields except the ones that correspond to other actions
# "price" can correspond to CAN_EDIT_DETAILS or CAN_EDIT_DISCOUNT an is processed separately
PATCH_DETAILS_FIELDS_PUBLIC = tuple(
    public_api_collective_offers_serialize.PatchCollectiveOfferBodyModel.__fields__.keys()
    - {
        *PATCH_INSTITUTION_FIELDS_PUBLIC,
        *PATCH_DATES_FIELDS_PUBLIC,
        *PATCH_DISCOUNT_FIELDS_PUBLIC,
        "price",
    }
)


def _check_allowed_action(
    *,
    offer: models.CollectiveOffer,
    edited_fields: typing.Iterable[str],
    action_fields: typing.Iterable[str],
    allowed_action: models.CollectiveOfferAllowedAction,
) -> None:
    is_editing_fields = any(field in edited_fields for field in action_fields)
    if is_editing_fields:
        validation.check_collective_offer_action_is_allowed(offer=offer, action=allowed_action, for_public_api=True)


def check_edit_collective_offer_public_allowed_action(offer: models.CollectiveOffer, new_values: dict) -> None:
    edited_fields = new_values.keys()

    _check_allowed_action(
        offer=offer,
        edited_fields=edited_fields,
        action_fields=PATCH_INSTITUTION_FIELDS_PUBLIC,
        allowed_action=models.CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION,
    )

    _check_allowed_action(
        offer=offer,
        edited_fields=edited_fields,
        action_fields=PATCH_DATES_FIELDS_PUBLIC,
        allowed_action=models.CollectiveOfferAllowedAction.CAN_EDIT_DATES,
    )

    _check_allowed_action(
        offer=offer,
        edited_fields=edited_fields,
        action_fields=PATCH_DISCOUNT_FIELDS_PUBLIC,
        allowed_action=models.CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
    )

    _check_allowed_action(
        offer=offer,
        edited_fields=edited_fields,
        action_fields=PATCH_DETAILS_FIELDS_PUBLIC,
        allowed_action=models.CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
    )

    if "price" in new_values:
        price: float = new_values["price"]

        if price > offer.collectiveStock.price:
            validation.check_collective_offer_action_is_allowed(
                offer=offer,
                action=models.CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
                for_public_api=True,
            )
        else:
            validation.check_collective_offer_action_is_allowed(
                offer=offer,
                action=models.CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
                for_public_api=True,
            )


def publish_collective_offer(offer: models.CollectiveOffer, user: User) -> models.CollectiveOffer:
    if offer.validation == offer_mixin.OfferValidationStatus.DRAFT:
        offers_api.update_offer_fraud_information(offer, user)

    return offer


def publish_collective_offer_template(
    offer_template: models.CollectiveOfferTemplate, user: User
) -> models.CollectiveOfferTemplate:
    if offer_template.validation == offer_mixin.OfferValidationStatus.DRAFT:
        offers_api.update_offer_fraud_information(offer_template, user)

        on_commit(
            partial(
                search.async_index_collective_offer_template_ids,
                [offer_template.id],
                reason=IndexationReason.OFFER_PUBLICATION,
            )
        )

        db.session.flush()

    return offer_template


def delete_image(obj: models.HasImageMixin) -> None:
    obj.delete_image()
    db.session.flush()


def attach_image(
    obj: models.HasImageMixin,
    image: bytes,
    crop_params: image_conversion.CropParams,
    credit: str,
) -> None:
    obj.set_image(
        image=image,
        credit=credit,
        crop_params=crop_params,
        ratio=image_conversion.ImageRatio.PORTRAIT,
        keep_original=False,
    )

    db.session.flush()


def _get_expired_or_archived_collective_offer_template_ids(
    page: int,
    limit: int,
) -> list[int]:
    collective_offers_template = repository.get_expired_or_archived_collective_offers_template()
    collective_offers_template = collective_offers_template.offset(page * limit).limit(limit)
    return [offer_template.id for offer_template in collective_offers_template]


def duplicate_offer_and_stock(original_offer: models.CollectiveOffer) -> models.CollectiveOffer:
    validation.check_collective_offer_action_is_allowed(
        original_offer, models.CollectiveOfferAllowedAction.CAN_DUPLICATE
    )

    offerer = original_offer.venue.managingOfferer
    if offerer.validationStatus != validation_status_mixin.ValidationStatus.VALIDATED:
        raise exceptions.OffererNotAllowedToDuplicate()

    # original offer may have invalid national_program or domains, in this case we do not copy it
    national_program_id = original_offer.nationalProgramId
    try:
        validation.validate_national_program(national_program_id=national_program_id, domains=original_offer.domains)
    except (exceptions.MissingDomains, exceptions.InactiveNationalProgram, exceptions.IllegalNationalProgram):
        national_program_id = None

    offer = models.CollectiveOffer(
        isActive=False,  # a DRAFT offer cannot be active
        venue=original_offer.venue,
        name=original_offer.name,
        bookingEmails=original_offer.bookingEmails,
        description=original_offer.description,
        durationMinutes=original_offer.durationMinutes,
        students=original_offer.students,
        contactEmail=original_offer.contactEmail,
        contactPhone=original_offer.contactPhone,
        interventionArea=original_offer.interventionArea,
        domains=original_offer.domains,
        template=original_offer.template,
        lastValidationDate=None,
        lastValidationType=None,
        lastValidationAuthorUserId=None,
        validation=offer_mixin.OfferValidationStatus.DRAFT,
        audioDisabilityCompliant=original_offer.audioDisabilityCompliant,
        mentalDisabilityCompliant=original_offer.mentalDisabilityCompliant,
        motorDisabilityCompliant=original_offer.motorDisabilityCompliant,
        visualDisabilityCompliant=original_offer.visualDisabilityCompliant,
        imageCredit=original_offer.imageCredit,
        imageHasOriginal=original_offer.imageHasOriginal,
        institutionId=original_offer.institutionId,
        nationalProgramId=national_program_id,
        formats=original_offer.formats,
        locationType=original_offer.locationType,
        locationComment=original_offer.locationComment,
        offererAddressId=original_offer.offererAddressId,
    )

    if original_offer.collectiveStock is not None:
        models.CollectiveStock(
            startDatetime=original_offer.collectiveStock.startDatetime,
            endDatetime=original_offer.collectiveStock.endDatetime,
            collectiveOffer=offer,
            price=original_offer.collectiveStock.price,
            bookingLimitDatetime=original_offer.collectiveStock.bookingLimitDatetime,
            numberOfTickets=original_offer.collectiveStock.numberOfTickets,
            priceDetail=original_offer.collectiveStock.priceDetail,
        )

    db.session.add(offer)
    db.session.flush()

    if original_offer.imageUrl:
        image_file = get_image_from_url(original_offer.imageUrl)

        offer.imageId = offer._generate_new_image_id(old_id=None)

        store_public_object(
            folder=offer.FOLDER,
            object_id=offer._get_image_storage_id(),
            blob=image_file,
            content_type="image/jpeg",
        )

        db.session.flush()
    return offer


def create_offer_request(
    body: PostCollectiveRequestBodyModel,
    offer: models.CollectiveOfferTemplate,
    institution: models.EducationalInstitution,
    redactor: models.EducationalRedactor,
) -> models.CollectiveOfferRequest:
    request = models.CollectiveOfferRequest(
        phoneNumber=body.phone_number,
        requestedDate=body.requested_date,
        totalStudents=body.total_students,
        totalTeachers=body.total_teachers,
        comment=body.comment,
        collectiveOfferTemplateId=offer.id,
        educationalInstitutionId=institution.id,
        educationalRedactor=redactor,
    )

    db.session.add(request)
    db.session.flush()

    transactional_mails.send_new_request_made_by_redactor_to_pro(request)
    on_commit(
        partial(
            adage_client.notify_redactor_when_collective_request_is_made, serialize_collective_offer_request(request)
        )
    )

    return request


def archive_collective_offers(
    offers: list[models.CollectiveOffer],
    date_archived: datetime.datetime,
) -> None:
    for offer in offers:
        validation.check_collective_offer_action_is_allowed(offer, models.CollectiveOfferAllowedAction.CAN_ARCHIVE)

        offer.isActive = False
        offer.dateArchived = date_archived

    db.session.flush()


def archive_collective_offers_template(
    offers: list[models.CollectiveOfferTemplate],
    date_archived: datetime.datetime,
) -> None:
    for offer in offers:
        validation.check_collective_offer_template_action_is_allowed(
            offer, models.CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE
        )
        offer.isActive = False
        offer.dateArchived = date_archived

    db.session.flush()

    on_commit(
        partial(
            search.async_index_collective_offer_template_ids,
            [offer.id for offer in offers],
            reason=IndexationReason.OFFER_BATCH_UPDATE,
            log_extra={"changes": {"isActive", "dateArchived"}},
        )
    )


def batch_update_collective_offers(query: sa_orm.Query, update_fields: dict) -> None:
    allowed_validation_status = {offers_models.OfferValidationStatus.APPROVED}
    if "dateArchived" in update_fields:
        allowed_validation_status.update(
            (offers_models.OfferValidationStatus.DRAFT, offers_models.OfferValidationStatus.REJECTED)
        )

    collective_offer_ids_tuples = query.filter(
        models.CollectiveOffer.validation.in_(allowed_validation_status)
    ).with_entities(models.CollectiveOffer.id)

    collective_offer_ids = [offer_id for (offer_id,) in collective_offer_ids_tuples]
    number_of_collective_offers_to_update = len(collective_offer_ids)
    batch_size = 1000

    for current_start_index in range(0, number_of_collective_offers_to_update, batch_size):
        collective_offer_ids_batch = collective_offer_ids[
            current_start_index : min(current_start_index + batch_size, number_of_collective_offers_to_update)
        ]

        query_to_update = db.session.query(models.CollectiveOffer).filter(
            models.CollectiveOffer.id.in_(collective_offer_ids_batch)
        )
        query_to_update.update(update_fields, synchronize_session=False)

        if is_managed_transaction():
            db.session.flush()
        else:
            db.session.commit()


def batch_update_collective_offers_template(query: sa_orm.Query, update_fields: dict) -> None:
    allowed_validation_status = {offers_models.OfferValidationStatus.APPROVED}
    if "dateArchived" in update_fields:
        allowed_validation_status.update(
            (offers_models.OfferValidationStatus.DRAFT, offers_models.OfferValidationStatus.REJECTED)
        )

    collective_offer_ids_tuples = query.filter(
        models.CollectiveOfferTemplate.validation.in_(allowed_validation_status)
    ).with_entities(models.CollectiveOfferTemplate.id)

    collective_offer_template_ids = [offer_id for (offer_id,) in collective_offer_ids_tuples]
    number_of_collective_offers_template_to_update = len(collective_offer_template_ids)
    batch_size = 1000

    for current_start_index in range(0, number_of_collective_offers_template_to_update, batch_size):
        collective_offer_template_ids_batch = collective_offer_template_ids[
            current_start_index : min(current_start_index + batch_size, number_of_collective_offers_template_to_update)
        ]

        query_to_update = db.session.query(models.CollectiveOfferTemplate).filter(
            models.CollectiveOfferTemplate.id.in_(collective_offer_template_ids_batch)
        )
        query_to_update.update(update_fields, synchronize_session=False)

        if is_managed_transaction():
            db.session.flush()
        else:
            db.session.commit()

        on_commit(
            partial(
                search.async_index_collective_offer_template_ids,
                collective_offer_template_ids_batch,
                reason=IndexationReason.OFFER_BATCH_UPDATE,
                log_extra={"changes": set(update_fields.keys())},
            )
        )


def check_can_move_collective_offer_venue(
    collective_offer: models.CollectiveOffer, with_restrictions: bool = True
) -> list[offerers_models.Venue]:
    if with_restrictions:
        count_started_stocks = (
            db.session.query(models.CollectiveStock)
            .with_entities(models.CollectiveStock.id)
            .filter(
                models.CollectiveStock.collectiveOfferId == collective_offer.id,
                models.CollectiveStock.startDatetime < date_utils.get_naive_utc_now(),
            )
            .count()
        )
        if count_started_stocks > 0:
            raise offers_exceptions.OfferEventInThePast(count_started_stocks)

        count_reimbursed_bookings = (
            db.session.query(models.CollectiveBooking)
            .with_entities(models.CollectiveBooking.id)
            .join(models.CollectiveBooking.collectiveStock)
            .filter(
                models.CollectiveStock.collectiveOfferId == collective_offer.id,
                models.CollectiveBooking.isReimbursed,
            )
            .count()
        )
        if count_reimbursed_bookings > 0:
            raise offers_exceptions.OfferHasReimbursedBookings(count_reimbursed_bookings)

    venues_choices = offerers_repository.get_offerers_venues_with_pricing_point(
        collective_offer.venue,
        include_without_pricing_points=not with_restrictions,
        only_similar_pricing_points=not with_restrictions,
        filter_same_bank_account=not with_restrictions,
    )
    if not venues_choices:
        raise offers_exceptions.NoDestinationVenue()
    return venues_choices


def create_new_location_if_offer_uses_origin_venue_location(
    collective_offer: models.CollectiveOffer, destination_venue: offerers_models.Venue
) -> None:
    # Use a different OA if the offer uses the venue's OA
    source_venue = collective_offer.venue
    if collective_offer.offererAddress and collective_offer.offererAddress == source_venue.offererAddress:
        destination_oa = offerers_api.get_or_create_offer_location(
            source_venue.managingOffererId, source_venue.offererAddress.addressId, source_venue.common_name
        )
        db.session.add(destination_oa)
        collective_offer.offererAddress = destination_oa


def move_collective_offer_for_regularization(
    collective_offer: models.CollectiveOffer, destination_venue: offerers_models.Venue
) -> None:
    if not feature.FeatureToggle.VENUE_REGULARIZATION.is_active():
        raise NotImplementedError("Activate VENUE_REGULARIZATION to use this feature")

    venue_choices = check_can_move_collective_offer_venue(collective_offer, with_restrictions=False)

    if destination_venue not in venue_choices:
        raise offers_exceptions.ForbiddenDestinationVenue()

    create_new_location_if_offer_uses_origin_venue_location(collective_offer, destination_venue)
    collective_offer.venue = destination_venue
    db.session.add(collective_offer)

    collective_bookings_subquery = (
        db.session.query(models.CollectiveBooking)
        .join(models.CollectiveBooking.collectiveStock)
        .filter(models.CollectiveStock.collectiveOfferId == collective_offer.id)
    )
    collective_bookings_to_update = db.session.query(models.CollectiveBooking).filter(
        models.CollectiveBooking.id.in_(collective_bookings_subquery.with_entities(models.CollectiveBooking.id))
    )

    collective_bookings_to_update.update({"venueId": destination_venue.id}, synchronize_session=False)
    db.session.add_all(collective_bookings_to_update)


def move_collective_offer_venue(
    collective_offer: models.CollectiveOffer,
    destination_venue: offerers_models.Venue,
) -> None:
    venue_choices = check_can_move_collective_offer_venue(collective_offer)

    if destination_venue not in venue_choices:
        raise offers_exceptions.ForbiddenDestinationVenue()

    destination_pricing_point_link = destination_venue.current_pricing_point_link
    assert destination_pricing_point_link  # for mypy - it would not be in venue_choices without link
    destination_pricing_point_id = destination_pricing_point_link.pricingPointId

    collective_bookings = (
        db.session.query(models.CollectiveBooking)
        .join(models.CollectiveBooking.collectiveStock)
        .outerjoin(
            # max 1 row joined thanks to idx_uniq_collective_booking_id
            finance_models.FinanceEvent,
            sa.and_(
                finance_models.FinanceEvent.collectiveBookingId == models.CollectiveBooking.id,
                finance_models.FinanceEvent.status.in_(
                    [finance_models.FinanceEventStatus.PENDING, finance_models.FinanceEventStatus.READY]
                ),
            ),
        )
        .outerjoin(
            # max 1 row joined thanks to idx_uniq_booking_id
            finance_models.Pricing,
            sa.and_(
                finance_models.Pricing.collectiveBookingId == models.CollectiveBooking.id,
                finance_models.Pricing.status != finance_models.PricingStatus.CANCELLED,
            ),
        )
        .options(
            sa_orm.load_only(models.CollectiveBooking.status),
            sa_orm.contains_eager(models.CollectiveBooking.finance_events).load_only(
                finance_models.FinanceEvent.status
            ),
            sa_orm.contains_eager(models.CollectiveBooking.pricings).load_only(
                finance_models.Pricing.pricingPointId, finance_models.Pricing.status
            ),
        )
        .filter(models.CollectiveStock.collectiveOfferId == collective_offer.id)
    )

    create_new_location_if_offer_uses_origin_venue_location(collective_offer, destination_venue)
    collective_offer.venue = destination_venue
    db.session.add(collective_offer)

    for collective_booking in collective_bookings.all():
        assert not collective_booking.isReimbursed
        collective_booking.venueId = destination_venue.id
        db.session.add(collective_booking)

        # when offer has priced bookings, pricing point for destination venue must be the same as pricing point
        # used for pricing (same as venue pricing point at the time pricing was processed)
        pricing = collective_booking.pricings[0] if collective_booking.pricings else None
        if pricing and pricing.pricingPointId != destination_pricing_point_id:
            raise offers_exceptions.BookingsHaveOtherPricingPoint()
        finance_event = collective_booking.finance_events[0] if collective_booking.finance_events else None
        if finance_event:
            finance_event.venueId = destination_venue.id
            finance_event.pricingPointId = destination_pricing_point_id
            if finance_event.status == finance_models.FinanceEventStatus.PENDING:
                finance_event.status = finance_models.FinanceEventStatus.READY
                finance_event.pricingOrderingDate = finance_api.get_pricing_ordering_date(collective_booking)
            db.session.add(finance_event)
    db.session.flush()


def update_collective_offer(offer_id: int, body: "collective_offers_serialize.PatchCollectiveOfferBodyModel") -> None:
    new_values = body.dict(exclude_unset=True)

    offer_to_update = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer_id).one()

    validation.check_collective_offer_action_is_allowed(
        offer_to_update, models.CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
    )

    new_venue = None
    if "venueId" in new_values and new_values["venueId"] != offer_to_update.venueId:
        offerer = offerers_repository.get_by_collective_offer_id(offer_to_update.id)
        new_venue = offerers_api.get_venue_by_id(new_values["venueId"])
        if not new_venue:
            raise exceptions.VenueIdDoesNotExist()
        if new_venue.managingOffererId != offerer.id:
            raise exceptions.OffererOfVenueDontMatchOfferer()

    if new_venue:
        move_collective_offer_venue(offer_to_update, new_venue)

    updated_fields = _update_collective_offer(offer=offer_to_update, new_values=new_values, location_body=body.location)

    on_commit(
        partial(
            notify_educational_redactor_on_collective_offer_or_stock_edit,
            offer_to_update.id,
            updated_fields,
        )
    )


def update_collective_offer_template(
    offer_id: int, body: "collective_offers_serialize.PatchCollectiveOfferTemplateBodyModel"
) -> None:
    new_values = body.dict(exclude_unset=True)

    offer_to_update: models.CollectiveOfferTemplate = (
        db.session.query(models.CollectiveOfferTemplate).filter(models.CollectiveOfferTemplate.id == offer_id).one()
    )

    validation.check_collective_offer_template_action_is_allowed(
        offer_to_update, models.CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS
    )

    if "venueId" in new_values and new_values["venueId"] != offer_to_update.venueId:
        new_venue = offerers_api.get_venue_by_id(new_values["venueId"])

        if not new_venue:
            raise exceptions.VenueIdDoesNotExist()

        offerer = offerers_repository.get_by_collective_offer_template_id(offer_to_update.id)
        if new_venue.managingOffererId != offerer.id:
            raise exceptions.OffererOfVenueDontMatchOfferer()

        offer_to_update.venue = new_venue

    if "dates" in new_values:
        dates = new_values.pop("dates", None)
        if dates:
            start, end = dates["start"], dates["end"]
            if start.date() < offer_to_update.dateCreated.date():
                raise exceptions.StartsBeforeOfferCreation()

            # this is necessary to pass constraint template_dates_non_empty_daterange
            # currently this only happens when selecting time = 23h59
            offer_to_update.dateRange = utils.get_non_empty_date_time_range(start, end)
        else:
            offer_to_update.dateRange = None

    validation.check_contact_request(offer_to_update, new_values)
    _update_collective_offer(offer=offer_to_update, new_values=new_values, location_body=body.location)

    on_commit(
        partial(
            search.async_index_collective_offer_template_ids,
            [offer_to_update.id],
            reason=IndexationReason.OFFER_UPDATE,
        )
    )


def _update_collective_offer(
    offer: AnyCollectiveOffer,
    new_values: dict,
    location_body: "collective_offers_serialize.CollectiveOfferLocationModel | None",
) -> list[str]:
    validation.check_validation_status(offer)

    # check domains and national program
    domains_to_check = offer.domains
    edit_domains = "domains" in new_values
    if edit_domains:
        domain_ids = new_values.pop("domains")
        new_values["domains"] = get_educational_domains_from_ids(domain_ids)
        domains_to_check = new_values["domains"]

    program_id_to_check = offer.nationalProgramId
    edit_national_program = "nationalProgramId" in new_values
    if edit_national_program:
        program_id_to_check = new_values["nationalProgramId"]

    if edit_domains or edit_national_program:
        validation.validate_national_program(national_program_id=program_id_to_check, domains=domains_to_check)

    if "location" in new_values:
        # the schema checks that if location is present it cannot be null
        assert location_body is not None

        offerer_address = get_or_create_offerer_address_from_collective_offer_location(location_body, offer.venue)

        new_values["offererAddress"] = offerer_address
        new_values["locationType"] = location_body.locationType
        new_values["locationComment"] = location_body.locationComment

        new_values.pop("location", None)

    # This variable is meant for Adage mailing
    updated_fields = []
    for key, value in new_values.items():
        updated_fields.append(key)
        setattr(offer, key, value)

    db.session.add(offer)
    db.session.flush()

    return updated_fields


def toggle_publish_collective_offers_template(
    collective_offers_templates: list[models.CollectiveOfferTemplate], is_active: bool
) -> None:
    action = (
        models.CollectiveOfferTemplateAllowedAction.CAN_PUBLISH
        if is_active
        else models.CollectiveOfferTemplateAllowedAction.CAN_HIDE
    )
    for offer_template in collective_offers_templates:
        validation.check_collective_offer_template_action_is_allowed(offer_template, action)
        offer_template.isActive = is_active

    db.session.flush()

    on_commit(
        partial(
            search.async_index_collective_offer_template_ids,
            [offer.id for offer in collective_offers_templates],
            reason=IndexationReason.OFFER_BATCH_UPDATE,
            log_extra={"changes": {"isActive"}},
        )
    )
