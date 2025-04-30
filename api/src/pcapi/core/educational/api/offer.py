import dataclasses
import datetime
from decimal import Decimal
from functools import partial
import logging
import typing

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.core import search
from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import utils as educational_utils
from pcapi.core.educational import validation
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer_request
from pcapi.core.educational.api import adage as educational_api_adage
from pcapi.core.educational.api import national_program as national_program_api
from pcapi.core.educational.api import shared as api_shared
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.educational.schemas import EducationalBookingEdition
from pcapi.core.educational.utils import get_image_from_url
from pcapi.core.external.attributes.api import update_external_pro
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.object_storage import store_public_object
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import validation as offer_validation
from pcapi.core.users import models as users_models
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models import feature
from pcapi.models import offer_mixin
from pcapi.models import validation_status_mixin
from pcapi.repository.session_management import is_managed_transaction
from pcapi.repository.session_management import on_commit
from pcapi.routes.adage.v1.serialization import prebooking
from pcapi.routes.adage_iframe.serialization.offers import PostCollectiveRequestBodyModel
from pcapi.routes.public.collective.serialization import offers as public_api_collective_offers_serialize
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.utils import image_conversion
from pcapi.utils import rest


logger = logging.getLogger(__name__)
OFFERS_RECAP_LIMIT = 101


AnyCollectiveOffer = educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate


def notify_educational_redactor_on_collective_offer_or_stock_edit(
    collective_offer_id: int,
    updated_fields: list[str],
) -> None:
    if len(updated_fields) == 0:
        return

    active_collective_bookings = educational_repository.find_active_collective_booking_by_offer_id(collective_offer_id)
    if active_collective_bookings is None:
        return

    data = EducationalBookingEdition(
        **prebooking.serialize_collective_booking(active_collective_bookings).dict(),
        updatedFields=updated_fields,
    )
    try:
        adage_client.notify_offer_or_stock_edition(data)
    except AdageException as exception:
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


def list_collective_offers_for_pro_user(
    *,
    user_id: int,
    user_is_admin: bool,
    offerer_id: int | None,
    venue_id: int | None = None,
    name_keywords: str | None = None,
    statuses: list[educational_models.CollectiveOfferDisplayedStatus] | None = None,
    period_beginning_date: datetime.date | None = None,
    period_ending_date: datetime.date | None = None,
    offer_type: collective_offers_serialize.CollectiveOfferType | None = None,
    formats: list[EacFormat] | None = None,
) -> list[educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate]:
    offers = []
    if offer_type != collective_offers_serialize.CollectiveOfferType.template:
        offers = educational_repository.get_collective_offers_for_filters(
            user_id=user_id,
            user_is_admin=user_is_admin,
            offers_limit=OFFERS_RECAP_LIMIT,
            offerer_id=offerer_id,
            statuses=statuses,
            venue_id=venue_id,
            name_keywords=name_keywords,
            period_beginning_date=period_beginning_date,
            period_ending_date=period_ending_date,
            formats=formats,
        )
        if offer_type is not None:
            return offers
    templates = []
    if offer_type != collective_offers_serialize.CollectiveOfferType.offer:
        templates = educational_repository.get_collective_offers_template_for_filters(
            user_id=user_id,
            user_is_admin=user_is_admin,
            offers_limit=OFFERS_RECAP_LIMIT,
            offerer_id=offerer_id,
            statuses=statuses,
            venue_id=venue_id,
            name_keywords=name_keywords,
            period_beginning_date=period_beginning_date,
            period_ending_date=period_ending_date,
            formats=formats,
        )
        if offer_type is not None:
            return templates

    merged_offers = offers + templates

    merged_offers.sort(key=lambda offer: offer.sort_criterion, reverse=True)

    return merged_offers[0:OFFERS_RECAP_LIMIT]


def list_public_collective_offers(
    *,
    required_id: int,
    venue_id: int | None = None,
    status: offer_mixin.CollectiveOfferStatus | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
    limit: int = 500,
) -> list[educational_models.CollectiveOffer]:
    return educational_repository.list_public_collective_offers(
        required_id=required_id,
        status=status,
        venue_id=venue_id,
        period_beginning_date=period_beginning_date,
        period_ending_date=period_ending_date,
        limit=limit,
    )


def get_educational_domains_from_ids(
    educational_domain_ids: list[int] | None,
) -> list[educational_models.EducationalDomain]:
    if educational_domain_ids is None:
        return []

    unique_educational_domain_ids = set(educational_domain_ids)
    educational_domains = educational_repository.get_educational_domains_from_ids(unique_educational_domain_ids)

    if len(educational_domains) < len(unique_educational_domain_ids):
        raise exceptions.EducationalDomainsNotFound()

    return educational_domains


@dataclasses.dataclass
class CollectiveOfferLocation:
    location_type: educational_models.CollectiveLocationType
    location_comment: str | None
    offerer_address: offerers_models.OffererAddress | None


def get_location_from_offer_venue(
    offer_venue: educational_models.OfferVenueDict, venue: offerers_models.Venue | None
) -> CollectiveOfferLocation:
    match offer_venue["addressType"]:
        case educational_models.OfferAddressType.OFFERER_VENUE:
            return CollectiveOfferLocation(
                location_type=educational_models.CollectiveLocationType.ADDRESS,
                location_comment=None,
                offerer_address=venue.offererAddress if venue else None,
            )

        case educational_models.OfferAddressType.SCHOOL:
            return CollectiveOfferLocation(
                location_type=educational_models.CollectiveLocationType.SCHOOL,
                location_comment=None,
                offerer_address=None,
            )

        case educational_models.OfferAddressType.OTHER:
            return CollectiveOfferLocation(
                location_type=educational_models.CollectiveLocationType.TO_BE_DEFINED,
                location_comment=offer_venue["otherAddress"],
                offerer_address=None,
            )

        case _:
            raise ValueError("Unexpected addressType received")


def check_venue_user_access(venue_id: int, user: User) -> None:
    location_venue = offerers_repository.get_venue_by_id(venue_id)
    if not location_venue:
        raise exceptions.VenueIdDontExist()
    rest.check_user_has_access_to_offerer(user, offerer_id=location_venue.managingOffererId)


def get_offer_venue_from_location(
    location_type: educational_models.CollectiveLocationType | None,
    location_comment: str | None,
    offerer_address: offerers_models.OffererAddress | None,
    is_venue_address: bool,
    venue_id: int,
) -> educational_models.OfferVenueDict:
    match location_type:
        case educational_models.CollectiveLocationType.SCHOOL:
            return {
                "addressType": educational_models.OfferAddressType.SCHOOL,
                "otherAddress": "",
                "venueId": None,
            }

        case educational_models.CollectiveLocationType.ADDRESS:
            if is_venue_address:
                return {
                    "addressType": educational_models.OfferAddressType.OFFERER_VENUE,
                    "otherAddress": "",
                    "venueId": venue_id,
                }

            if offerer_address is not None and offerer_address.address is not None:
                other_address = offerer_address.address.fullAddress
            else:
                other_address = ""

            return {
                "addressType": educational_models.OfferAddressType.OTHER,
                "otherAddress": other_address,
                "venueId": None,
            }

        case educational_models.CollectiveLocationType.TO_BE_DEFINED:
            return {
                "addressType": educational_models.OfferAddressType.OTHER,
                "otherAddress": location_comment or "",
                "venueId": None,
            }

        case _:
            raise ValueError("Invalid location_type received")


def get_location_values(
    offer_data: collective_offers_serialize.PostCollectiveOfferBodyModel,
    user: User,
    venue: offerers_models.Venue,
) -> tuple[offerers_models.OffererAddress | None, list[str], educational_models.OfferVenueDict]:
    """
    We can either receive offerVenue or location in offer_data
    When we receive the offerVenue field, in the "offererVenue" case we check venueId and force intervention_area to be empty
    When we receive location, we also write to offerVenue to keep the field up to date
    """
    address_body = offer_data.location.address if offer_data.location is not None else None
    offerer_address = offers_api.get_offerer_address_from_address_body(address_body=address_body, venue=venue)
    intervention_area = offer_data.intervention_area or []

    offer_venue: educational_models.OfferVenueDict
    if offer_data.offer_venue is not None:
        offer_venue = typing.cast(educational_models.OfferVenueDict, offer_data.offer_venue.dict())
        if offer_venue["addressType"] == educational_models.OfferAddressType.OFFERER_VENUE:
            venue_id = offer_venue["venueId"]
            if venue_id is None:
                raise exceptions.VenueIdDontExist()

            check_venue_user_access(venue_id=venue_id, user=user)
            intervention_area = []

    elif offer_data.location is not None:
        offer_venue = get_offer_venue_from_location(
            location_type=offer_data.location.locationType,
            location_comment=offer_data.location.locationComment,
            offerer_address=offerer_address,
            is_venue_address=address_body.isVenueAddress if address_body is not None else False,
            venue_id=venue.id,
        )

    else:  # the model validation should not allow this case
        raise ValueError("Should either receive offerVenue or location")

    return offerer_address, intervention_area, offer_venue


def create_collective_offer_template(
    offer_data: collective_offers_serialize.PostCollectiveOfferTemplateBodyModel, user: User
) -> educational_models.CollectiveOfferTemplate:
    venue = get_venue_and_check_access_for_offer_creation(offer_data, user)
    educational_domains = get_educational_domains_from_ids(offer_data.domains)

    # TODO: move this to validation and see if that can be merged with check_contact_request
    if not any((offer_data.contact_email, offer_data.contact_phone, offer_data.contact_url, offer_data.contact_form)):
        raise offers_exceptions.AllNullContactRequestDataError()
    if offer_data.contact_url and offer_data.contact_form:
        raise offers_exceptions.UrlandFormBothSetError()

    offerer_address, intervention_area, offer_venue = get_location_values(offer_data=offer_data, user=user, venue=venue)

    collective_offer_template = educational_models.CollectiveOfferTemplate(
        venueId=venue.id,
        name=offer_data.name,
        description=offer_data.description,
        domains=educational_domains,
        durationMinutes=offer_data.duration_minutes,
        students=offer_data.students,
        contactEmail=offer_data.contact_email,
        contactPhone=offer_data.contact_phone,
        contactUrl=offer_data.contact_url,
        contactForm=offer_data.contact_form,
        offerVenue={**offer_venue, "addressType": offer_venue["addressType"].value},
        validation=offer_mixin.OfferValidationStatus.DRAFT,
        audioDisabilityCompliant=offer_data.audio_disability_compliant,
        mentalDisabilityCompliant=offer_data.mental_disability_compliant,
        motorDisabilityCompliant=offer_data.motor_disability_compliant,
        visualDisabilityCompliant=offer_data.visual_disability_compliant,
        interventionArea=intervention_area,
        priceDetail=offer_data.price_detail,
        bookingEmails=offer_data.booking_emails,  # type: ignore[arg-type]
        formats=offer_data.formats,  # type: ignore[arg-type]
        author=user,
        locationType=offer_data.location.locationType if offer_data.location else None,
        locationComment=offer_data.location.locationComment if offer_data.location else None,
        offererAddressId=offerer_address.id if offerer_address else None,
    )

    if offer_data.dates:
        # this is necessary to pass constraint template_dates_non_empty_daterange
        # currently this only happens when selecting time = 23h59
        collective_offer_template.dateRange = educational_utils.get_non_empty_date_time_range(
            offer_data.dates.start, offer_data.dates.end
        )

    db.session.add(collective_offer_template)
    db.session.flush()

    if offer_data.nationalProgramId:
        validation.validate_national_program(
            national_program_id=offer_data.nationalProgramId, domains=educational_domains
        )
        national_program_api.link_or_unlink_offer_to_program(offer_data.nationalProgramId, collective_offer_template)

    logger.info(
        "Collective offer template has been created", extra={"collectiveOfferTemplate": collective_offer_template.id}
    )
    return collective_offer_template


def create_collective_offer(
    offer_data: collective_offers_serialize.PostCollectiveOfferBodyModel,
    user: User,
    offer_id: int | None = None,
) -> educational_models.CollectiveOffer:
    venue = get_venue_and_check_access_for_offer_creation(offer_data, user)
    educational_domains = get_educational_domains_from_ids(offer_data.domains)

    if offer_data.template_id is not None:
        template = educational_repository.get_collective_offer_template_by_id(offer_data.template_id)
        validation.check_collective_offer_template_action_is_allowed(
            template, educational_models.CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER
        )

    offerer_address, intervention_area, offer_venue = get_location_values(offer_data=offer_data, user=user, venue=venue)

    collective_offer = educational_models.CollectiveOffer(
        isActive=False,  # a DRAFT offer cannot be active
        venueId=venue.id,
        name=offer_data.name,
        description=offer_data.description,
        domains=educational_domains,
        durationMinutes=offer_data.duration_minutes,
        students=offer_data.students,
        contactEmail=offer_data.contact_email,
        contactPhone=offer_data.contact_phone,
        offerVenue={**offer_venue, "addressType": offer_venue["addressType"].value},
        validation=offer_mixin.OfferValidationStatus.DRAFT,
        audioDisabilityCompliant=offer_data.audio_disability_compliant,
        mentalDisabilityCompliant=offer_data.mental_disability_compliant,
        motorDisabilityCompliant=offer_data.motor_disability_compliant,
        visualDisabilityCompliant=offer_data.visual_disability_compliant,
        interventionArea=intervention_area,
        templateId=offer_data.template_id,
        bookingEmails=offer_data.booking_emails,  # type: ignore[arg-type]
        formats=offer_data.formats,  # type: ignore[arg-type]
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

    national_program_id = offer_data.nationalProgramId
    if national_program_id is not None:
        try:
            validation.validate_national_program(national_program_id=national_program_id, domains=educational_domains)
        except (exceptions.InactiveNationalProgram, exceptions.IllegalNationalProgram):
            if offer_data.template_id is not None:
                # original offer template may have invalid national_program, in this case we set program to None
                national_program_id = None
            else:
                # if we are not creating from an offer template, we do not allow an invalid program
                raise

        if national_program_id is not None:
            national_program_api.link_or_unlink_offer_to_program(national_program_id, collective_offer)

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
        template = get_collective_offer_template_by_id(offer_data.template_id)
        rest.check_user_has_access_to_offerer(user, offerer_id=template.venue.managingOffererId)
    venue: offerers_models.Venue = db.session.query(offerers_models.Venue).get_or_404(offer_data.venue_id)
    rest.check_user_has_access_to_offerer(user, offerer_id=venue.managingOffererId)
    if not offerers_api.can_offerer_create_educational_offer(venue.managingOffererId):
        raise exceptions.CulturalPartnerNotFoundException("No venue has been found for the selected siren")

    return venue


def get_collective_offer_request_by_id(request_id: int) -> educational_models.CollectiveOfferRequest:
    return educational_repository.get_collective_offer_request_by_id(request_id)


def get_collective_offer_template_by_id(
    offer_id: int,
) -> educational_models.CollectiveOffer:
    return educational_repository.get_collective_offer_template_by_id(offer_id)


def get_collective_offer_by_id_for_adage(offer_id: int) -> educational_models.CollectiveOffer:
    return educational_repository.get_collective_offer_by_id_for_adage(offer_id)


def get_collective_offer_template_by_id_for_adage(
    offer_id: int,
) -> educational_models.CollectiveOfferTemplate:
    return educational_repository.get_collective_offer_template_by_id_for_adage(offer_id)


def get_query_for_collective_offers_by_ids_for_user(user: User, ids: typing.Iterable[int]) -> BaseQuery:
    return educational_repository.get_query_for_collective_offers_by_ids_for_user(user=user, ids=ids)


def get_query_for_collective_offers_template_by_ids_for_user(user: User, ids: typing.Iterable[int]) -> BaseQuery:
    return educational_repository.get_query_for_collective_offers_template_by_ids_for_user(user=user, ids=ids)


def update_collective_offer_educational_institution(
    offer_id: int, educational_institution_id: int | None, teacher_email: str | None
) -> educational_models.CollectiveOffer:
    offer = educational_repository.get_collective_offer_by_id(offer_id)

    validation.check_collective_offer_action_is_allowed(
        offer, educational_models.CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION
    )

    new_institution = None
    if educational_institution_id is not None:
        new_institution = validation.check_institution_id_exists(educational_institution_id)

    offer.institution = new_institution
    offer.teacher = None

    if offer.institution is not None:
        if not offer.institution.isActive:
            raise exceptions.EducationalInstitutionIsNotActive()
    elif teacher_email is not None:
        raise exceptions.EducationalRedactorCannotBeLinked()

    if offer.institution is not None and teacher_email:
        possible_teachers = educational_api_adage.autocomplete_educational_redactor_for_uai(
            uai=offer.institution.institutionId,
            candidate=teacher_email,
            use_email=True,
        )
        for teacher in possible_teachers:
            if teacher["mail"] == teacher_email:
                redactor = educational_repository.find_redactor_by_email(teacher["mail"])
                if not redactor:
                    redactor = educational_models.EducationalRedactor(
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

    if educational_institution_id is not None and offer.validation == offer_mixin.OfferValidationStatus.APPROVED:
        on_commit(partial(adage_client.notify_institution_association, serialize_collective_offer(offer)))

    return offer


def create_collective_offer_public(
    requested_id: int,
    body: public_api_collective_offers_serialize.PostCollectiveOfferBodyModel,
) -> educational_models.CollectiveOffer:
    venue = educational_repository.fetch_venue_for_new_offer(body.venue_id, requested_id)
    if not offerers_api.can_offerer_create_educational_offer(venue.managingOffererId):
        raise exceptions.CulturalPartnerNotFoundException("No venue has been found for the selected siren")

    validation.validate_offer_venue(body.offer_venue)

    educational_domains = educational_repository.get_educational_domains_from_ids(body.domains)

    if feature.FeatureToggle.WIP_ENABLE_NATIONAL_PROGRAM_NEW_RULES_PUBLIC_API.is_active():
        validation.validate_national_program(body.nationalProgramId, educational_domains)

    if len(educational_domains) != len(body.domains):
        raise exceptions.EducationalDomainsNotFound()

    institution = educational_repository.get_educational_institution_public(
        institution_id=body.educational_institution_id,
        uai=body.educational_institution,
    )
    if not institution:
        raise exceptions.EducationalInstitutionUnknown()
    if not institution.isActive:
        raise exceptions.EducationalInstitutionIsNotActive()

    end_datetime = body.end_datetime or body.start_datetime
    validation.check_start_and_end_dates_in_same_educational_year(body.start_datetime, end_datetime)

    offer_venue: educational_models.OfferVenueDict = {
        "venueId": body.offer_venue.venueId,
        "addressType": body.offer_venue.addressType,
        "otherAddress": body.offer_venue.otherAddress or "",
    }

    # when we receive offerVenue, we also write to OA fields
    location_venue = None
    if offer_venue["addressType"] == educational_models.OfferAddressType.OFFERER_VENUE:
        venue_id = offer_venue["venueId"]
        if venue_id is None:
            raise exceptions.VenueIdDontExist()

        location_venue = educational_repository.fetch_venue_for_new_offer(venue_id, requested_id)

    location = get_location_from_offer_venue(offer_venue=offer_venue, venue=location_venue)

    collective_offer = educational_models.CollectiveOffer(
        venue=venue,
        name=body.name,
        description=body.description,
        contactEmail=body.contact_email,
        contactPhone=body.contact_phone,
        domains=educational_domains,
        durationMinutes=body.duration_minutes,
        students=typing.cast(  # type transformation done by the validator (and not detected by mypy)
            list[educational_models.StudentLevels], body.students
        ),
        audioDisabilityCompliant=body.audio_disability_compliant,
        mentalDisabilityCompliant=body.mental_disability_compliant,
        motorDisabilityCompliant=body.motor_disability_compliant,
        visualDisabilityCompliant=body.visual_disability_compliant,
        offerVenue={**offer_venue, "addressType": offer_venue["addressType"].value},
        interventionArea=[],
        institution=institution,
        providerId=requested_id,
        nationalProgramId=body.nationalProgramId,
        formats=body.formats,
        bookingEmails=body.booking_emails,
        locationType=location.location_type,
        locationComment=location.location_comment,
        offererAddressId=location.offerer_address.id if location.offerer_address else None,
    )

    collective_stock = educational_models.CollectiveStock(
        collectiveOffer=collective_offer,
        startDatetime=body.start_datetime,
        endDatetime=end_datetime,
        bookingLimitDatetime=body.booking_limit_datetime,
        price=body.total_price,
        numberOfTickets=body.number_of_tickets,
        priceDetail=body.educational_price_detail,
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
    offer: educational_models.CollectiveOffer,
) -> educational_models.CollectiveOffer:
    if not offer.isEditable:
        raise exceptions.CollectiveOfferNotEditable()

    if provider_id != offer.providerId:
        raise exceptions.CollectiveOfferNotEditable()

    collective_stock_unique_booking = offer.collectiveStock.get_unique_non_cancelled_booking()
    if collective_stock_unique_booking is not None:
        if collective_stock_unique_booking.status == educational_models.CollectiveBookingStatus.CONFIRMED:
            # if the booking is CONFIRMED, we can only edit the price related fields and the price cannot be increased
            allowed_fields_for_confirmed_booking = {"price", "priceDetail", "numberOfTickets"}
            unallowed_fields = set(new_values) - allowed_fields_for_confirmed_booking
            if unallowed_fields:
                raise exceptions.CollectiveOfferForbiddenFields(
                    allowed_fields=["totalPrice", "educationalPriceDetail", "numberOfTickets"]
                )

            if "price" in new_values and offer.collectiveStock.price < new_values["price"]:
                raise exceptions.PriceRequesteCantBedHigherThanActualPrice()
        else:
            # if the booking is PENDING, we can edit any field
            validation.check_collective_booking_status_pending(collective_stock_unique_booking)

    offer_fields = {field for field in dir(educational_models.CollectiveOffer) if not field.startswith("_")}
    stock_fields = {field for field in dir(educational_models.CollectiveStock) if not field.startswith("_")}

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

    # when we receive offerVenue, we also write to OA fields
    offer_venue = new_values.get("offerVenue")
    if offer_venue is not None:
        location_venue = None
        if offer_venue["addressType"] == educational_models.OfferAddressType.OFFERER_VENUE:
            venue_id = offer_venue["venueId"]
            if venue_id is None:
                raise exceptions.VenueIdDontExist()

            location_venue = educational_repository.fetch_venue_for_new_offer(venue_id, provider_id)
            new_values["interventionArea"] = []

        # we might receive None for otherAddress but we store str
        if "otherAddress" in offer_venue:
            offer_venue["otherAddress"] = offer_venue["otherAddress"] or ""

        location = get_location_from_offer_venue(offer_venue=offer_venue, venue=location_venue)

        new_values["locationType"] = location.location_type
        new_values["locationComment"] = location.location_comment
        new_values["offererAddressId"] = location.offerer_address.id if location.offerer_address else None

    # This variable is meant for Adage mailing
    updated_fields = []
    for key, value in new_values.items():
        updated_fields.append(key)

        if key == "domains":
            domains = educational_repository.get_educational_domains_from_ids(value)
            if len(domains) != len(value):
                raise exceptions.EducationalDomainsNotFound()

            if feature.FeatureToggle.WIP_ENABLE_NATIONAL_PROGRAM_NEW_RULES_PUBLIC_API.is_active():
                validation.validate_national_program(
                    national_program_id=new_values.get("nationalProgramId"),
                    domains=domains,
                    check_program_is_active=False,  # do not check if program is active so that existing offers with inactive program can still be patched
                )
            offer.domains = domains
        elif key in ("educationalInstitutionId", "educationalInstitution"):
            if value is None:
                continue

            institution = educational_repository.get_educational_institution_public(
                institution_id=new_values.get("educationalInstitutionId"),
                uai=new_values.get("educationalInstitution"),
            )

            if not institution:
                raise exceptions.EducationalInstitutionUnknown()
            if not institution.isActive:
                raise exceptions.EducationalInstitutionIsNotActive()

            offer.institution = institution
        elif key == "offerVenue":
            offer.offerVenue["venueId"] = value.get("venueId")
            offer.offerVenue["addressType"] = value.get("addressType")
            offer.offerVenue["otherAddress"] = value.get("otherAddress") or ""
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

    api_shared.update_collective_stock_booking(
        stock=offer.collectiveStock,
        current_booking=collective_stock_unique_booking,
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


def publish_collective_offer(
    offer: educational_models.CollectiveOffer, user: User
) -> educational_models.CollectiveOffer:
    if offer.validation == offer_mixin.OfferValidationStatus.DRAFT:
        offers_api.update_offer_fraud_information(offer, user)

    return offer


def publish_collective_offer_template(
    offer_template: educational_models.CollectiveOfferTemplate, user: User
) -> educational_models.CollectiveOfferTemplate:
    if offer_template.validation == offer_mixin.OfferValidationStatus.DRAFT:
        offers_api.update_offer_fraud_information(offer_template, user)

        on_commit(
            partial(
                search.async_index_collective_offer_template_ids,
                [offer_template.id],
                reason=search.IndexationReason.OFFER_PUBLICATION,
            )
        )

        db.session.flush()

    return offer_template


def delete_image(obj: educational_models.HasImageMixin) -> None:
    obj.delete_image()
    db.session.flush()


def attach_image(
    obj: educational_models.HasImageMixin,
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
    collective_offers_template = educational_repository.get_expired_or_archived_collective_offers_template()
    collective_offers_template = collective_offers_template.offset(page * limit).limit(limit)
    return [offer_template.id for offer_template in collective_offers_template]


def duplicate_offer_and_stock(
    original_offer: educational_models.CollectiveOffer,
) -> educational_models.CollectiveOffer:
    validation.check_collective_offer_action_is_allowed(
        original_offer, educational_models.CollectiveOfferAllowedAction.CAN_DUPLICATE
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

    offer = educational_models.CollectiveOffer(
        isActive=False,  # a DRAFT offer cannot be active
        venue=original_offer.venue,
        name=original_offer.name,
        bookingEmails=original_offer.bookingEmails,
        description=original_offer.description,
        durationMinutes=original_offer.durationMinutes,
        students=original_offer.students,
        contactEmail=original_offer.contactEmail,
        contactPhone=original_offer.contactPhone,
        offerVenue=original_offer.offerVenue,
        interventionArea=original_offer.interventionArea,
        domains=original_offer.domains,
        template=original_offer.template,  # type: ignore[arg-type]
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
        educational_models.CollectiveStock(
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
    offer: educational_models.CollectiveOfferTemplate,
    institution: educational_models.EducationalInstitution,
    redactor: educational_models.EducationalRedactor,
) -> educational_models.CollectiveOfferRequest:
    request = educational_models.CollectiveOfferRequest(
        phoneNumber=body.phone_number,  # type: ignore[call-arg]
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

    request.email = redactor.email

    transactional_mails.send_new_request_made_by_redactor_to_pro(request)
    on_commit(
        partial(
            adage_client.notify_redactor_when_collective_request_is_made, serialize_collective_offer_request(request)
        )
    )

    return request


def get_offer_event_venue(offer: AnyCollectiveOffer) -> offerers_models.Venue:
    """Get the venue where the event occurs"""
    address_type = offer.offerVenue.get("addressType")
    offerer_venue_id = offer.offerVenue.get("venueId")

    # the offer takes place in a specific venue
    if address_type == "offererVenue" and offerer_venue_id:
        venue = db.session.query(offerers_models.Venue).get(offerer_venue_id)
    else:
        venue = None

    # no specific venue specified - or it does not exists
    # anymore
    if not venue:
        venue = offer.venue

    return venue


def get_offer_coordinates(offer: AnyCollectiveOffer) -> tuple[float | Decimal, float | Decimal] | tuple[None, None]:
    """
    Return the offer's coordinates to use. Use the specified venue
    if any or use the offer's billing address as the default.
    """
    venue = get_offer_event_venue(offer)

    # we should return a coherent value: either latitude AND
    # longitude or empty coordinates.
    if venue.offererAddress is not None:
        latitude = venue.offererAddress.address.latitude
        longitude = venue.offererAddress.address.longitude
    else:
        latitude, longitude = None, None

    if not latitude or not longitude:
        return (None, None)

    return latitude, longitude


def archive_collective_offers(
    offers: list[educational_models.CollectiveOffer],
    date_archived: datetime.datetime,
) -> None:
    for offer in offers:
        validation.check_collective_offer_action_is_allowed(
            offer, educational_models.CollectiveOfferAllowedAction.CAN_ARCHIVE
        )

        offer.isActive = False
        offer.dateArchived = date_archived

    db.session.flush()


def archive_collective_offers_template(
    offers: list[educational_models.CollectiveOfferTemplate],
    date_archived: datetime.datetime,
) -> None:
    for offer in offers:
        validation.check_collective_offer_template_action_is_allowed(
            offer, educational_models.CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE
        )
        offer.isActive = False
        offer.dateArchived = date_archived

    db.session.flush()

    on_commit(
        partial(
            search.async_index_collective_offer_template_ids,
            [offer.id for offer in offers],
            reason=search.IndexationReason.OFFER_BATCH_UPDATE,
            log_extra={"changes": {"isActive", "dateArchived"}},
        )
    )


def batch_update_collective_offers(query: BaseQuery, update_fields: dict) -> None:
    allowed_validation_status = {offers_models.OfferValidationStatus.APPROVED}
    if "dateArchived" in update_fields:
        allowed_validation_status.update(
            (offers_models.OfferValidationStatus.DRAFT, offers_models.OfferValidationStatus.REJECTED)
        )

    collective_offer_ids_tuples = query.filter(
        educational_models.CollectiveOffer.validation.in_(allowed_validation_status)  # type: ignore[attr-defined]
    ).with_entities(educational_models.CollectiveOffer.id)

    collective_offer_ids = [offer_id for offer_id, in collective_offer_ids_tuples]
    number_of_collective_offers_to_update = len(collective_offer_ids)
    batch_size = 1000

    for current_start_index in range(0, number_of_collective_offers_to_update, batch_size):
        collective_offer_ids_batch = collective_offer_ids[
            current_start_index : min(current_start_index + batch_size, number_of_collective_offers_to_update)
        ]

        query_to_update = db.session.query(educational_models.CollectiveOffer).filter(
            educational_models.CollectiveOffer.id.in_(collective_offer_ids_batch)
        )
        query_to_update.update(update_fields, synchronize_session=False)

        if is_managed_transaction():
            db.session.flush()
        else:
            db.session.commit()


def batch_update_collective_offers_template(query: BaseQuery, update_fields: dict) -> None:
    allowed_validation_status = {offers_models.OfferValidationStatus.APPROVED}
    if "dateArchived" in update_fields:
        allowed_validation_status.update(
            (offers_models.OfferValidationStatus.DRAFT, offers_models.OfferValidationStatus.REJECTED)
        )

    collective_offer_ids_tuples = query.filter(
        educational_models.CollectiveOfferTemplate.validation.in_(allowed_validation_status)  # type: ignore[attr-defined]
    ).with_entities(educational_models.CollectiveOfferTemplate.id)

    collective_offer_template_ids = [offer_id for offer_id, in collective_offer_ids_tuples]
    number_of_collective_offers_template_to_update = len(collective_offer_template_ids)
    batch_size = 1000

    for current_start_index in range(0, number_of_collective_offers_template_to_update, batch_size):
        collective_offer_template_ids_batch = collective_offer_template_ids[
            current_start_index : min(current_start_index + batch_size, number_of_collective_offers_template_to_update)
        ]

        query_to_update = db.session.query(educational_models.CollectiveOfferTemplate).filter(
            educational_models.CollectiveOfferTemplate.id.in_(collective_offer_template_ids_batch)
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
                reason=search.IndexationReason.OFFER_BATCH_UPDATE,
                log_extra={"changes": set(update_fields.keys())},
            )
        )


def check_can_move_collective_offer_venue(
    collective_offer: educational_models.CollectiveOffer, with_restrictions: bool = True
) -> list[offerers_models.Venue]:
    if with_restrictions:
        count_started_stocks = (
            db.session.query(educational_models.CollectiveStock)
            .with_entities(educational_models.CollectiveStock.id)
            .filter(
                educational_models.CollectiveStock.collectiveOfferId == collective_offer.id,
                educational_models.CollectiveStock.startDatetime < datetime.datetime.utcnow(),
            )
            .count()
        )
        if count_started_stocks > 0:
            raise offers_exceptions.OfferEventInThePast(count_started_stocks)

        count_reimbursed_bookings = (
            db.session.query(educational_models.CollectiveBooking)
            .with_entities(educational_models.CollectiveBooking.id)
            .join(educational_models.CollectiveBooking.collectiveStock)
            .filter(
                educational_models.CollectiveStock.collectiveOfferId == collective_offer.id,
                educational_models.CollectiveBooking.isReimbursed,
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


def move_collective_offer_venue(
    collective_offer: educational_models.CollectiveOffer,
    destination_venue: offerers_models.Venue,
    with_restrictions: bool = True,
) -> None:
    venue_choices = check_can_move_collective_offer_venue(collective_offer, with_restrictions=with_restrictions)

    if destination_venue not in venue_choices:
        raise offers_exceptions.ForbiddenDestinationVenue()

    destination_pricing_point_link = destination_venue.current_pricing_point_link
    if not with_restrictions:
        destination_pricing_point_id = (
            destination_pricing_point_link.pricingPointId if destination_pricing_point_link else None
        )
    else:
        assert destination_pricing_point_link  # for mypy - it would not be in venue_choices without link
        destination_pricing_point_id = destination_pricing_point_link.pricingPointId

    collective_bookings = (
        db.session.query(educational_models.CollectiveBooking)
        .join(educational_models.CollectiveBooking.collectiveStock)
        .outerjoin(
            # max 1 row joined thanks to idx_uniq_collective_booking_id
            finance_models.FinanceEvent,
            sa.and_(
                finance_models.FinanceEvent.collectiveBookingId == educational_models.CollectiveBooking.id,
                finance_models.FinanceEvent.status.in_(
                    [finance_models.FinanceEventStatus.PENDING, finance_models.FinanceEventStatus.READY]
                ),
            ),
        )
        .outerjoin(
            # max 1 row joined thanks to idx_uniq_booking_id
            finance_models.Pricing,
            sa.and_(
                finance_models.Pricing.collectiveBookingId == educational_models.CollectiveBooking.id,
                finance_models.Pricing.status != finance_models.PricingStatus.CANCELLED,
            ),
        )
        .options(
            sa_orm.load_only(educational_models.CollectiveBooking.status),
            sa_orm.contains_eager(educational_models.CollectiveBooking.finance_events).load_only(
                finance_models.FinanceEvent.status
            ),
            sa_orm.contains_eager(educational_models.CollectiveBooking.pricings).load_only(
                finance_models.Pricing.pricingPointId, finance_models.Pricing.status
            ),
        )
        .filter(educational_models.CollectiveStock.collectiveOfferId == collective_offer.id)
        .all()
    )

    collective_offer.venue = destination_venue
    db.session.add(collective_offer)

    for collective_booking in collective_bookings:
        collective_booking.venueId = destination_venue.id
        db.session.add(collective_booking)

        # when offer has priced bookings, pricing point for destination venue must be the same as pricing point
        # used for pricing (same as venue pricing point at the time pricing was processed)
        pricing = collective_booking.pricings[0] if collective_booking.pricings else None
        if pricing and pricing.pricingPointId != destination_pricing_point_id:
            raise offers_exceptions.BookingsHaveOtherPricingPoint()

        if with_restrictions:
            finance_event = collective_booking.finance_events[0] if collective_booking.finance_events else None
            if finance_event:
                finance_event.venueId = destination_venue.id
                finance_event.pricingPointId = destination_pricing_point_id
                if finance_event.status == finance_models.FinanceEventStatus.PENDING:
                    finance_event.status = finance_models.FinanceEventStatus.READY
                    finance_event.pricingOrderingDate = finance_api.get_pricing_ordering_date(collective_booking)
                db.session.add(finance_event)

    db.session.flush()


def update_collective_offer(
    offer_id: int, body: "collective_offers_serialize.PatchCollectiveOfferBodyModel", user: users_models.User
) -> None:
    new_values = body.dict(exclude_unset=True)

    offer_to_update = (
        db.session.query(educational_models.CollectiveOffer)
        .filter(educational_models.CollectiveOffer.id == offer_id)
        .first()
    )

    validation.check_collective_offer_action_is_allowed(
        offer_to_update, educational_models.CollectiveOfferAllowedAction.CAN_EDIT_DETAILS
    )

    new_venue = None
    if "venueId" in new_values and new_values["venueId"] != offer_to_update.venueId:
        offerer = offerers_repository.get_by_collective_offer_id(offer_to_update.id)
        new_venue = offerers_api.get_venue_by_id(new_values["venueId"])
        if not new_venue:
            raise exceptions.VenueIdDontExist()
        if new_venue.managingOffererId != offerer.id:
            raise exceptions.OffererOfVenueDontMatchOfferer()

    if new_venue:
        move_collective_offer_venue(offer_to_update, new_venue)

    updated_fields = _update_collective_offer(
        offer=offer_to_update, new_values=new_values, location_body=body.location, user=user
    )

    on_commit(
        partial(
            notify_educational_redactor_on_collective_offer_or_stock_edit,
            offer_to_update.id,
            updated_fields,
        )
    )


def update_collective_offer_template(
    offer_id: int, body: "collective_offers_serialize.PatchCollectiveOfferTemplateBodyModel", user: users_models.User
) -> None:
    new_values = body.dict(exclude_unset=True)

    offer_to_update: educational_models.CollectiveOfferTemplate = (
        db.session.query(educational_models.CollectiveOfferTemplate)
        .filter(educational_models.CollectiveOfferTemplate.id == offer_id)
        .one()
    )

    validation.check_collective_offer_template_action_is_allowed(
        offer_to_update, educational_models.CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS
    )

    if "venueId" in new_values and new_values["venueId"] != offer_to_update.venueId:
        new_venue = offerers_api.get_venue_by_id(new_values["venueId"])

        if not new_venue:
            raise exceptions.VenueIdDontExist()

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
            offer_to_update.dateRange = educational_utils.get_non_empty_date_time_range(start, end)
        else:
            offer_to_update.dateRange = None

    _update_collective_offer(offer=offer_to_update, new_values=new_values, location_body=body.location, user=user)

    on_commit(
        partial(
            search.async_index_collective_offer_template_ids,
            [offer_to_update.id],
            reason=search.IndexationReason.OFFER_UPDATE,
        )
    )


def _update_collective_offer(
    offer: AnyCollectiveOffer,
    new_values: dict,
    location_body: "collective_offers_serialize.CollectiveOfferLocationModel | None",
    user: users_models.User,
) -> list[str]:
    offer_validation.check_validation_status(offer)
    offer_validation.check_contact_request(offer, new_values)

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
        national_program_id = new_values.pop("nationalProgramId")
        national_program_api.link_or_unlink_offer_to_program(national_program_id, offer)
        program_id_to_check = national_program_id

    if edit_domains or edit_national_program:
        validation.validate_national_program(national_program_id=program_id_to_check, domains=domains_to_check)

    # check offerVenue
    edit_offer_venue = "offerVenue" in new_values
    edit_location = "location" in new_values
    if edit_offer_venue and edit_location:
        raise ValueError("Cannot receive offerVenue and location at the same time")

    if edit_offer_venue:
        offer_venue = new_values["offerVenue"]
        if offer_venue["addressType"] == educational_models.OfferAddressType.OFFERER_VENUE:
            check_venue_user_access(offer_venue["venueId"], user)
            new_values["interventionArea"] = []

    # receive location -> extract location field and write to offerVenue to keep the field up to date
    if edit_location:
        assert location_body is not None
        offerer_address = offers_api.get_offerer_address_from_address_body(
            address_body=location_body.address, venue=offer.venue
        )
        new_values["offererAddress"] = offerer_address

        offer_venue = get_offer_venue_from_location(
            location_type=location_body.locationType,
            location_comment=location_body.locationComment,
            offerer_address=offerer_address,
            is_venue_address=location_body.address.isVenueAddress if location_body.address is not None else False,
            venue_id=offer.venue.id,
        )
        new_values["offerVenue"] = offer_venue

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
    collective_offers_templates: list[educational_models.CollectiveOfferTemplate],
    is_active: bool,
) -> None:
    action = (
        educational_models.CollectiveOfferTemplateAllowedAction.CAN_PUBLISH
        if is_active
        else educational_models.CollectiveOfferTemplateAllowedAction.CAN_HIDE
    )
    for offer_template in collective_offers_templates:
        validation.check_collective_offer_template_action_is_allowed(offer_template, action)
        offer_template.isActive = is_active

    db.session.flush()

    on_commit(
        partial(
            search.async_index_collective_offer_template_ids,
            [offer.id for offer in collective_offers_templates],
            reason=search.IndexationReason.OFFER_BATCH_UPDATE,
            log_extra={"changes": {"isActive"}},
        )
    )
