import datetime
from decimal import Decimal
import logging
import typing

from flask_sqlalchemy import BaseQuery
from psycopg2.extras import DateTimeRange

from pcapi import settings
from pcapi.core import search
import pcapi.core.categories.subcategories_v2 as subcategories
from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import validation
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer_request
from pcapi.core.educational.api import adage as educational_api_adage
import pcapi.core.educational.api.national_program as national_program_api
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.educational.models import HasImageMixin
from pcapi.core.educational.utils import get_image_from_url
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.object_storage import store_public_object
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import validation as offer_validation
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models import feature
from pcapi.models import offer_mixin
from pcapi.models import validation_status_mixin
from pcapi.routes.adage.v1.serialization import prebooking
from pcapi.routes.adage_iframe.serialization.offers import PostCollectiveRequestBodyModel
from pcapi.routes.public.collective.serialization import offers as public_api_collective_offers_serialize
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.routes.serialization.collective_offers_serialize import PostCollectiveOfferBodyModel
from pcapi.routes.serialization.collective_offers_serialize import PostCollectiveOfferTemplateBodyModel
from pcapi.utils import image_conversion
from pcapi.utils import rest


logger = logging.getLogger(__name__)
OFFERS_RECAP_LIMIT = 501


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

    data = prebooking.EducationalBookingEdition(
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


def unindex_expired_collective_offers_template(process_all_expired: bool = False) -> None:
    """Unindex collective offers template that have expired."""
    page = 0
    limit = settings.ALGOLIA_DELETING_COLLECTIVE_OFFERS_CHUNK_SIZE
    while collective_offer_template_ids := _get_expired_collective_offer_template_ids(page, limit):
        logger.info(
            "[ALGOLIA] Found %d expired collective offers template to unindex",
            len(collective_offer_template_ids),
        )
        search.unindex_collective_offer_template_ids(collective_offer_template_ids)
        page += 1


def list_collective_offers_for_pro_user(
    user_id: int,
    user_is_admin: bool,
    category_id: str | None,
    offerer_id: int | None,
    venue_id: int | None = None,
    name_keywords: str | None = None,
    statuses: list[str] | None = None,
    period_beginning_date: datetime.date | None = None,
    period_ending_date: datetime.date | None = None,
    offer_type: collective_offers_serialize.CollectiveOfferType | None = None,
    formats: list[subcategories.EacFormat] | None = None,
) -> list[educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate]:
    if offer_type != collective_offers_serialize.CollectiveOfferType.template:
        offers = educational_repository.get_collective_offers_for_filters(
            user_id=user_id,
            user_is_admin=user_is_admin,
            offers_limit=OFFERS_RECAP_LIMIT,
            offerer_id=offerer_id,
            statuses=statuses,
            venue_id=venue_id,
            category_id=category_id,
            name_keywords=name_keywords,
            period_beginning_date=period_beginning_date,
            period_ending_date=period_ending_date,
            formats=formats,
        )
        if offer_type is not None:
            return offers
    if offer_type != collective_offers_serialize.CollectiveOfferType.offer:
        templates = educational_repository.get_collective_offers_template_for_filters(
            user_id=user_id,
            user_is_admin=user_is_admin,
            offers_limit=OFFERS_RECAP_LIMIT,
            offerer_id=offerer_id,
            statuses=statuses,
            venue_id=venue_id,
            category_id=category_id,
            name_keywords=name_keywords,
            period_beginning_date=period_beginning_date,
            period_ending_date=period_ending_date,
            formats=formats,
        )
        if offer_type is not None:
            return templates
    offer_index = 0
    template_index = 0
    merged_offers = []

    # merge two ordered lists to one shorter than OFFERS_RECAP_LIMIT items
    for _ in range(min(OFFERS_RECAP_LIMIT, (len(offers) + len(templates)))):
        if offer_index >= len(offers) and template_index >= len(templates):
            # this should never happen. Only there as defensive measure.
            break

        if offer_index >= len(offers):
            merged_offers.append(templates[template_index])
            template_index += 1
            continue

        if template_index >= len(templates):
            merged_offers.append(offers[offer_index])
            offer_index += 1
            continue

        offer_date = offers[offer_index].dateCreated
        template_date = templates[template_index].dateCreated

        if offer_date > template_date:
            merged_offers.append(offers[offer_index])
            offer_index += 1
        else:
            merged_offers.append(templates[template_index])
            template_index += 1

    return merged_offers


def list_public_collective_offers(
    required_id: int,
    venue_id: int | None = None,
    status: offer_mixin.OfferStatus | None = None,
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


def create_collective_offer_template(
    offer_data: PostCollectiveOfferTemplateBodyModel,
    user: User,
    offer_id: int | None = None,
) -> educational_models.CollectiveOfferTemplate:
    venue = get_venue_and_check_access_for_offer_creation(offer_data, user)
    educational_domains = get_educational_domains_from_ids(offer_data.domains)

    # TODO: move this to validation and see if that can be merged with check_contact_request
    if not any((offer_data.contact_email, offer_data.contact_phone, offer_data.contact_url, offer_data.contact_form)):
        raise offers_exceptions.AllNullContactRequestDataError()
    if offer_data.contact_url and offer_data.contact_form:
        raise offers_exceptions.UrlandFormBothSetError()

    collective_offer_template = educational_models.CollectiveOfferTemplate(
        venueId=venue.id,
        name=offer_data.name,
        offerId=offer_id,
        description=offer_data.description,
        domains=educational_domains,
        durationMinutes=offer_data.duration_minutes,
        subcategoryId=offer_data.subcategory_id,
        students=offer_data.students,
        contactEmail=offer_data.contact_email,
        contactPhone=offer_data.contact_phone,
        contactUrl=offer_data.contact_url,
        contactForm=offer_data.contact_form,
        offerVenue=offer_data.offer_venue.dict(),
        validation=offer_mixin.OfferValidationStatus.DRAFT,
        audioDisabilityCompliant=offer_data.audio_disability_compliant,
        mentalDisabilityCompliant=offer_data.mental_disability_compliant,
        motorDisabilityCompliant=offer_data.motor_disability_compliant,
        visualDisabilityCompliant=offer_data.visual_disability_compliant,
        interventionArea=offer_data.intervention_area or [],
        priceDetail=offer_data.price_detail,
        formats=offer_data.formats,  # type: ignore[arg-type]
        author=user,
    )

    if offer_data.dates:
        collective_offer_template.dateRange = DateTimeRange(offer_data.dates.start, offer_data.dates.end)

    collective_offer_template.bookingEmails = offer_data.booking_emails
    db.session.add(collective_offer_template)
    db.session.commit()

    if offer_data.nationalProgramId:
        national_program_api.link_or_unlink_offer_to_program(offer_data.nationalProgramId, collective_offer_template)

    logger.info(
        "Collective offer template has been created",
        extra={
            "collectiveOfferTemplate": collective_offer_template.id,
            "offerId": offer_id,
        },
    )
    return collective_offer_template


def create_collective_offer(
    offer_data: PostCollectiveOfferBodyModel,
    user: User,
    offer_id: int | None = None,
) -> educational_models.CollectiveOffer:
    venue = get_venue_and_check_access_for_offer_creation(offer_data, user)
    educational_domains = get_educational_domains_from_ids(offer_data.domains)

    collective_offer = educational_models.CollectiveOffer(
        isActive=False,  # a DRAFT offer cannot be active
        venueId=venue.id,
        name=offer_data.name,
        offerId=offer_id,
        description=offer_data.description,
        domains=educational_domains,
        durationMinutes=offer_data.duration_minutes,
        subcategoryId=offer_data.subcategory_id,
        students=offer_data.students,
        contactEmail=offer_data.contact_email,
        contactPhone=offer_data.contact_phone,
        offerVenue=offer_data.offer_venue.dict(),
        validation=offer_mixin.OfferValidationStatus.DRAFT,
        audioDisabilityCompliant=offer_data.audio_disability_compliant,
        mentalDisabilityCompliant=offer_data.mental_disability_compliant,
        motorDisabilityCompliant=offer_data.motor_disability_compliant,
        visualDisabilityCompliant=offer_data.visual_disability_compliant,
        interventionArea=offer_data.intervention_area or [],
        templateId=offer_data.template_id,
        formats=offer_data.formats,  # type: ignore[arg-type]
        author=user,
    )
    collective_offer.bookingEmails = offer_data.booking_emails

    db.session.add(collective_offer)
    db.session.commit()

    if offer_data.nationalProgramId:
        national_program_api.link_or_unlink_offer_to_program(offer_data.nationalProgramId, collective_offer)

    logger.info(
        "Collective offer has been created",
        extra={"collectiveOffer": collective_offer.id, "offerId": offer_id},
    )
    return collective_offer


def get_venue_and_check_access_for_offer_creation(
    offer_data: PostCollectiveOfferBodyModel,
    user: User,
) -> offerers_models.Venue:
    if offer_data.template_id is not None:
        template = get_collective_offer_template_by_id(offer_data.template_id)
        rest.check_user_has_access_to_offerer(user, offerer_id=template.venue.managingOffererId)
    venue: offerers_models.Venue = offerers_models.Venue.query.get_or_404(offer_data.venue_id)
    rest.check_user_has_access_to_offerer(user, offerer_id=venue.managingOffererId)
    if not offerers_api.can_offerer_create_educational_offer(venue.managingOffererId):
        raise exceptions.CulturalPartnerNotFoundException("No venue has been found for the selected siren")

    offer_validation.check_offer_subcategory_is_valid(offer_data.subcategory_id)
    offer_validation.check_offer_is_eligible_for_educational(offer_data.subcategory_id)
    return venue


def create_collective_offer_template_from_collective_offer(
    price_detail: str | None, user: User, offer_id: int
) -> educational_models.CollectiveOfferTemplate:
    offer = educational_repository.get_collective_offer_by_id(offer_id)
    if offer.collectiveStock is not None:
        raise exceptions.EducationalStockAlreadyExists()

    collective_offer_template = educational_models.CollectiveOfferTemplate.create_from_collective_offer(
        offer, price_detail=price_detail
    )
    db.session.delete(offer)
    db.session.add(collective_offer_template)
    db.session.commit()

    logger.info(
        "Collective offer template has been created and regular collective offer deleted",
        extra={
            "collectiveOfferTemplate": collective_offer_template.id,
            "CollectiveOffer": offer.id,
        },
    )
    return collective_offer_template


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
    if educational_institution_id is not None:
        validation.check_institution_id_exists(educational_institution_id)

    if offer.collectiveStock and not offer.collectiveStock.isEditable:
        raise exceptions.CollectiveOfferNotEditable()

    offer.institutionId = educational_institution_id
    offer.teacher = None

    if offer.institutionId is not None:
        if not offer.institution.isActive:
            raise exceptions.EducationalInstitutionIsNotActive()
    elif teacher_email is not None:
        raise exceptions.EducationalRedcatorCannotBeLinked()

    if offer.institutionId is not None and teacher_email:
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

    db.session.commit()

    if educational_institution_id is not None and offer.validation == offer_mixin.OfferValidationStatus.APPROVED:
        adage_client.notify_institution_association(serialize_collective_offer(offer))

    return offer


def create_collective_offer_public(
    requested_id: int,
    body: public_api_collective_offers_serialize.PostCollectiveOfferBodyModel,
) -> educational_models.CollectiveOffer:
    from pcapi.core.offers.api import update_offer_fraud_information

    venue = educational_repository.fetch_venue_for_new_offer(body.venue_id, requested_id)
    if not offerers_api.can_offerer_create_educational_offer(venue.managingOffererId):
        raise exceptions.CulturalPartnerNotFoundException("No venue has been found for the selected siren")

    offer_validation.check_offer_subcategory_is_valid(body.subcategory_id)
    offer_validation.check_offer_is_eligible_for_educational(body.subcategory_id)
    validation.validate_offer_venue(body.offer_venue)

    educational_domains = educational_repository.get_educational_domains_from_ids(body.domains)

    if feature.FeatureToggle.WIP_ENABLE_NATIONAL_PROGRAM_NEW_RULES_PUBLIC_API.is_active():
        offer_validation.validate_national_program(body.nationalProgramId, educational_domains)

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

    offer_venue = {
        "venueId": body.offer_venue.venueId,
        "addressType": body.offer_venue.addressType,
        "otherAddress": body.offer_venue.otherAddress or "",
    }
    collective_offer = educational_models.CollectiveOffer(
        venue=venue,
        name=body.name,
        description=body.description,
        subcategoryId=body.subcategory_id,
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
        offerVenue=offer_venue,
        interventionArea=[],
        institution=institution,
        providerId=requested_id,
        nationalProgramId=body.nationalProgramId,
        formats=body.formats,
        bookingEmails=body.booking_emails,
    )

    collective_stock = educational_models.CollectiveStock(
        collectiveOffer=collective_offer,
        beginningDatetime=body.beginning_datetime,
        bookingLimitDatetime=body.booking_limit_datetime,
        price=body.total_price,
        numberOfTickets=body.number_of_tickets,
        priceDetail=body.educational_price_detail,
    )

    update_offer_fraud_information(offer=collective_offer, user=None)
    db.session.add(collective_offer)
    db.session.add(collective_stock)
    db.session.commit()
    logger.info(
        "Collective offer has been created",
        extra={"offerId": collective_offer.id},
    )
    return collective_offer


def edit_collective_offer_public(
    provider_id: int,
    new_values: dict,
    offer: educational_models.CollectiveOffer,
) -> educational_models.CollectiveOffer:
    from pcapi.core.educational.api.stock import _update_educational_booking_cancellation_limit_date
    from pcapi.core.educational.api.stock import _update_educational_booking_educational_year_id

    if not (offer.isEditable and offer.collectiveStock.isEditable):
        raise exceptions.CollectiveOfferNotEditable()

    if provider_id != offer.providerId:
        raise exceptions.CollectiveOfferNotEditable()

    offer_fields = {field for field in dir(educational_models.CollectiveOffer) if not field.startswith("_")}
    stock_fields = {field for field in dir(educational_models.CollectiveStock) if not field.startswith("_")}

    collective_stock_unique_booking = (
        educational_models.CollectiveBooking.query.join(
            educational_models.CollectiveStock,
            educational_models.CollectiveBooking.collectiveStock,
        )
        .filter(
            educational_models.CollectiveStock.collectiveOfferId == offer.id,
            educational_models.CollectiveBooking.status != educational_models.CollectiveBookingStatus.CANCELLED,
        )
        .one_or_none()
    )
    if collective_stock_unique_booking:
        validation.check_collective_booking_status_pending(collective_stock_unique_booking)

    # This variable is meant for Adage mailing
    updated_fields = []
    for key, value in new_values.items():
        updated_fields.append(key)

        if key == "subcategoryId":
            # offer_validation.check_offer_subcategory_is_valid(value)
            offer_validation.check_offer_is_eligible_for_educational(value)
            offer.subcategoryId = value
        elif key == "domains":
            domains = educational_repository.get_educational_domains_from_ids(value)
            if len(domains) != len(value):
                raise exceptions.EducationalDomainsNotFound()

            if feature.FeatureToggle.WIP_ENABLE_NATIONAL_PROGRAM_NEW_RULES_PUBLIC_API.is_active():
                offer_validation.validate_national_program(new_values.get("nationalProgramId"), domains)
            offer.domains = domains
        elif key in ("educationalInstitutionId", "educationalInstitution"):
            if value is not None:
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
            offer.offerVenue["venueId"] = value["venueId"] or None
            offer.offerVenue["addressType"] = value["addressType"].value
            offer.offerVenue["otherAddress"] = value["otherAddress"] or ""
        elif key == "bookingLimitDatetime" and value is None:
            offer.collectiveStock.bookingLimitDatetime = new_values.get(
                "beginningDatetime", offer.collectiveStock.beginningDatetime
            )
            if collective_stock_unique_booking:
                collective_stock_unique_booking.confirmationLimitDate = value
        elif key == "beginningDatetime":
            offer.collectiveStock.beginningDatetime = value
            if collective_stock_unique_booking:
                _update_educational_booking_cancellation_limit_date(collective_stock_unique_booking, value)
                _update_educational_booking_educational_year_id(collective_stock_unique_booking, value)
        elif key == "price":
            offer.collectiveStock.price = value
            if collective_stock_unique_booking:
                collective_stock_unique_booking.amount = value
        elif key in stock_fields:
            setattr(offer.collectiveStock, key, value)
        elif key in offer_fields:
            setattr(offer, key, value)
        else:
            raise ValueError(f"unknown field {key}")

    db.session.commit()

    notify_educational_redactor_on_collective_offer_or_stock_edit(
        offer.id,
        updated_fields,
    )
    return offer


def publish_collective_offer(
    offer: educational_models.CollectiveOffer, user: User
) -> educational_models.CollectiveOffer:
    from pcapi.core.offers.api import update_offer_fraud_information

    if offer.validation == offer_mixin.OfferValidationStatus.DRAFT:
        update_offer_fraud_information(offer, user)

    return offer


def publish_collective_offer_template(
    offer_template: educational_models.CollectiveOfferTemplate, user: User
) -> educational_models.CollectiveOfferTemplate:
    from pcapi.core.offers.api import update_offer_fraud_information

    if offer_template.validation == offer_mixin.OfferValidationStatus.DRAFT:
        update_offer_fraud_information(offer_template, user)
        search.async_index_collective_offer_template_ids(
            [offer_template.id],
            reason=search.IndexationReason.OFFER_PUBLICATION,
        )
        db.session.commit()

    return offer_template


def delete_image(obj: HasImageMixin) -> None:
    obj.delete_image()
    db.session.commit()
    return


def attach_image(
    obj: educational_models.HasImageMixin,
    image: bytes,
    crop_params: image_conversion.CropParams,
    credit: str,
) -> None:
    try:
        obj.set_image(
            image=image,
            credit=credit,
            crop_params=crop_params,
            ratio=image_conversion.ImageRatio.PORTRAIT,
            keep_original=False,
        )
    except:
        db.session.rollback()
        raise
    db.session.commit()


def _get_expired_collective_offer_template_ids(
    page: int,
    limit: int,
) -> list[int]:
    collective_offers_template = educational_repository.get_expired_collective_offers_template()
    collective_offers_template = collective_offers_template.offset(page * limit).limit(limit)
    return [offer_template.id for offer_template in collective_offers_template]


def duplicate_offer_and_stock(
    original_offer: educational_models.CollectiveOffer,
) -> educational_models.CollectiveOffer:
    if original_offer.validation == offer_mixin.OfferValidationStatus.DRAFT:
        raise exceptions.ValidationFailedOnCollectiveOffer()
    offerer = original_offer.venue.managingOfferer
    if offerer.validationStatus != validation_status_mixin.ValidationStatus.VALIDATED:
        raise exceptions.OffererNotAllowedToDuplicate()

    offer = educational_models.CollectiveOffer(
        isActive=False,  # a DRAFT offer cannot be active
        venue=original_offer.venue,
        name=original_offer.name,
        bookingEmails=original_offer.bookingEmails,
        description=original_offer.description,
        durationMinutes=original_offer.durationMinutes,
        subcategoryId=original_offer.subcategoryId,
        students=original_offer.students,
        contactEmail=original_offer.contactEmail,
        contactPhone=original_offer.contactPhone,
        offerVenue=original_offer.offerVenue,
        interventionArea=original_offer.interventionArea,
        domains=original_offer.domains,
        template=original_offer.template,
        lastValidationDate=original_offer.lastValidationDate,
        lastValidationType=original_offer.lastValidationType,
        validation=offer_mixin.OfferValidationStatus.DRAFT,
        audioDisabilityCompliant=original_offer.audioDisabilityCompliant,
        mentalDisabilityCompliant=original_offer.mentalDisabilityCompliant,
        motorDisabilityCompliant=original_offer.motorDisabilityCompliant,
        visualDisabilityCompliant=original_offer.visualDisabilityCompliant,
        imageCredit=original_offer.imageCredit,
        imageHasOriginal=original_offer.imageHasOriginal,
        institutionId=original_offer.institutionId,
        nationalProgramId=original_offer.nationalProgramId,
        formats=original_offer.formats,
    )
    educational_models.CollectiveStock(
        beginningDatetime=original_offer.collectiveStock.beginningDatetime,
        collectiveOffer=offer,
        price=original_offer.collectiveStock.price,
        bookingLimitDatetime=original_offer.collectiveStock.bookingLimitDatetime,
        numberOfTickets=original_offer.collectiveStock.numberOfTickets,
        priceDetail=original_offer.collectiveStock.priceDetail,
    )

    db.session.add(offer)
    db.session.commit()

    if original_offer.imageUrl:
        image_file = get_image_from_url(original_offer.imageUrl)

        offer.imageId = offer._generate_new_image_id(old_id=None)

        store_public_object(
            folder=offer.FOLDER,
            object_id=offer._get_image_storage_id(),
            blob=image_file,
            content_type="image/jpeg",
        )

        db.session.commit()
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
        educationalRedactorId=redactor.id,
    )

    db.session.add(request)
    db.session.commit()
    request.email = redactor.email

    transactional_mails.send_new_request_made_by_redactor_to_pro(request)

    adage_client.notify_redactor_when_collective_request_is_made(serialize_collective_offer_request(request))

    return request


def get_offer_event_venue(offer: AnyCollectiveOffer) -> offerers_models.Venue:
    """Get the venue where the event occurs"""
    address_type = offer.offerVenue.get("addressType")
    offerer_venue_id = offer.offerVenue.get("venueId")

    # the offer takes place in a specific venue
    if address_type == "offererVenue" and offerer_venue_id:
        venue = offerers_models.Venue.query.get(offerer_venue_id)
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
    latitude, longitude = venue.latitude, venue.longitude
    if not latitude or not longitude:
        return (None, None)

    return latitude, longitude
