import datetime
import logging
import typing

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sa

from pcapi import settings
from pcapi.core import search
from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import validation
from pcapi.core.educational.adage_backends.serialize import serialize_collective_offer
from pcapi.core.educational.api import adage as educational_api_adage
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.educational.exceptions import StudentsNotOpenedYet
from pcapi.core.educational.models import HasImageMixin
from pcapi.core.educational.utils import get_image_from_url
from pcapi.core.mails.transactional.educational.eac_new_request_made_by_redactor_to_pro import (
    send_new_request_made_by_redactor_to_pro,
)
from pcapi.core.object_storage import store_public_object
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import validation as offer_validation
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.models import validation_status_mixin
from pcapi.routes.adage.v1.serialization import prebooking
from pcapi.routes.adage_iframe.serialization.offers import PostCollectiveRequestBodyModel
from pcapi.routes.public.collective.serialization import offers as public_api_collective_offers_serialize
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.routes.serialization.collective_offers_serialize import PostCollectiveOfferBodyModel
from pcapi.routes.serialization.collective_offers_serialize import PostCollectiveOfferTemplateBodyModel
from pcapi.routes.serialization.collective_stock_serialize import CollectiveStockCreationBodyModel
from pcapi.utils import image_conversion
from pcapi.utils import rest


logger = logging.getLogger(__name__)
OFFERS_RECAP_LIMIT = 501


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


def unindex_expired_collective_offers(process_all_expired: bool = False) -> None:
    """Unindex collective offers that have expired.

    By default, process collective offers that have expired within the last 2
    days. For example, if run on Thursday (whatever the time), this
    function handles collective offers that have expired between Tuesday 00:00
    and Wednesday 23:59 (included).

    If ``process_all_expired`` is true, process... well all expired
    collective offers.
    """
    start_of_day = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    interval = (
        datetime.datetime(2000, 1, 1) if process_all_expired else start_of_day - datetime.timedelta(days=2),
        start_of_day,
    )

    page = 0
    limit = settings.ALGOLIA_DELETING_COLLECTIVE_OFFERS_CHUNK_SIZE
    while collective_offer_ids := _get_expired_collective_offer_ids(interval, page, limit):
        logger.info(
            "[ALGOLIA] Found %d expired collective offers to unindex",
            len(collective_offer_ids),
        )
        search.unindex_collective_offer_ids(collective_offer_ids)
        page += 1


def list_collective_offers_for_pro_user(
    user_id: int,
    user_is_admin: bool,
    category_id: str | None,
    offerer_id: int | None,
    venue_id: int | None = None,
    name_keywords: str | None = None,
    status: str | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
    offer_type: collective_offers_serialize.CollectiveOfferType | None = None,
) -> list[educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate]:
    if offer_type != collective_offers_serialize.CollectiveOfferType.template:
        offers = educational_repository.get_collective_offers_for_filters(
            user_id=user_id,
            user_is_admin=user_is_admin,
            offers_limit=OFFERS_RECAP_LIMIT,
            offerer_id=offerer_id,
            status=status,
            venue_id=venue_id,
            category_id=category_id,
            name_keywords=name_keywords,
            period_beginning_date=period_beginning_date,
            period_ending_date=period_ending_date,
        )
        if offer_type is not None:
            return offers
    if offer_type != collective_offers_serialize.CollectiveOfferType.offer:
        templates = educational_repository.get_collective_offers_template_for_filters(
            user_id=user_id,
            user_is_admin=user_is_admin,
            offers_limit=OFFERS_RECAP_LIMIT,
            offerer_id=offerer_id,
            status=status,
            venue_id=venue_id,
            category_id=category_id,
            name_keywords=name_keywords,
            period_beginning_date=period_beginning_date,
            period_ending_date=period_ending_date,
        )
        if offer_type is not None:
            return templates
    offer_index = 0
    template_index = 0
    merged_offers = []

    # merge two ordered lists to one shorter than OFFERS_RECAP_LIMIT items
    for _ in range(min(OFFERS_RECAP_LIMIT, (len(offers) + len(templates)))):
        if offer_index >= len(offers) and template_index >= len(templates):
            # this should never hapen. Only there as defensive mesure.
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
    offerer_id: int,
    venue_id: int | None = None,
    status: offer_mixin.OfferStatus | None = None,
    period_beginning_date: str | None = None,
    period_ending_date: str | None = None,
    limit: int = 500,
) -> list[educational_models.CollectiveOffer]:
    return educational_repository.list_public_collective_offers(
        offerer_id=offerer_id,
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
        offerVenue=offer_data.offer_venue.dict(),
        validation=offer_mixin.OfferValidationStatus.DRAFT,
        audioDisabilityCompliant=offer_data.audio_disability_compliant,
        mentalDisabilityCompliant=offer_data.mental_disability_compliant,
        motorDisabilityCompliant=offer_data.motor_disability_compliant,
        visualDisabilityCompliant=offer_data.visual_disability_compliant,
        interventionArea=offer_data.intervention_area or [],
        priceDetail=offer_data.price_detail,
    )
    collective_offer_template.bookingEmails = offer_data.booking_emails
    db.session.add(collective_offer_template)
    db.session.commit()
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
    )
    collective_offer.bookingEmails = offer_data.booking_emails
    db.session.add(collective_offer)
    db.session.commit()
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
    offerers_api.can_offerer_create_educational_offer(venue.managingOffererId)
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

    search.unindex_collective_offer_ids([offer.id])
    logger.info(
        "Collective offer template has been created and regular collective offer deleted",
        extra={
            "collectiveOfferTemplate": collective_offer_template.id,
            "CollectiveOffer": offer.id,
        },
    )
    return collective_offer_template


def get_collective_offer_by_id(offer_id: int) -> educational_models.CollectiveOffer:
    return educational_repository.get_collective_offer_by_id(offer_id)


def get_collective_offer_request_by_id(request_id: int) -> educational_models.CollectiveOfferRequest:
    return educational_repository.get_collective_offer_request_by_id(request_id)


def get_collective_offer_template_by_id(
    offer_id: int,
) -> educational_models.CollectiveOffer:
    return educational_repository.get_collective_offer_template_by_id(offer_id)


def get_collective_offer_by_id_for_adage(
    offer_id: int,
) -> educational_models.CollectiveOffer:
    return educational_repository.get_collective_offer_by_id_for_adage(offer_id)


def get_collective_offer_template_by_id_for_adage(
    offer_id: int,
) -> educational_models.CollectiveOfferTemplate:
    return educational_repository.get_collective_offer_template_by_id_for_adage(offer_id)


def transform_collective_offer_template_into_collective_offer(
    user: User, body: CollectiveStockCreationBodyModel
) -> educational_models.CollectiveOffer:
    from pcapi.core.educational.api.stock import create_collective_stock

    collective_offer_template = educational_models.CollectiveOfferTemplate.query.filter_by(id=body.offer_id).one()
    collective_offer_template_id = collective_offer_template.id

    offer_validation.check_validation_status(collective_offer_template)
    collective_offer = educational_models.CollectiveOffer.create_from_collective_offer_template(
        collective_offer_template
    )

    db.session.delete(collective_offer_template)
    db.session.add(collective_offer)
    db.session.commit()

    search.unindex_collective_offer_template_ids([collective_offer_template_id])

    create_collective_stock(stock_data=body, user=user, offer_id=collective_offer.id)
    return collective_offer


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
                    redactor = redactor = educational_models.EducationalRedactor(
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
    search.async_index_collective_offer_ids([offer_id])
    if educational_institution_id is not None and offer.validation == offer_mixin.OfferValidationStatus.APPROVED:
        adage_client.notify_institution_association(serialize_collective_offer(offer))

    return offer


def create_collective_offer_public(
    provider_id: int,
    body: public_api_collective_offers_serialize.PostCollectiveOfferBodyModel,
) -> educational_models.CollectiveOffer:
    from pcapi.core.offers.api import update_offer_fraud_information

    offerers_api.can_provider_create_educational_offer(provider_id)

    venue = offerers_models.Venue.query.filter_by(id=body.venue_id).one_or_none()
    if venue is None or venue.venueProviders.id != provider_id:
        raise offerers_exceptions.VenueNotFoundException()
    typing.cast(offerers_models.Venue, venue)

    if body.beginning_datetime < datetime.datetime(2023, 9, 1, tzinfo=body.beginning_datetime.tzinfo):
        # FIXME: remove after 2023-09-01
        new_students = []
        for student in body.students:
            if student not in (
                educational_models.StudentLevels.COLLEGE5,
                educational_models.StudentLevels.COLLEGE6,
            ):
                new_students.append(student)
        if new_students:
            body.students = new_students
        else:
            raise StudentsNotOpenedYet()

    offer_validation.check_offer_subcategory_is_valid(body.subcategory_id)
    offer_validation.check_offer_is_eligible_for_educational(body.subcategory_id)
    validation.validate_offer_venue(body.offer_venue)

    educational_domains = educational_repository.get_educational_domains_from_ids(body.domains)
    if not len(educational_domains) == len(body.domains):
        raise exceptions.EducationalDomainsNotFound()

    institution = educational_repository.get_educational_institution_public(
        institution_id=body.educational_institution_id,
        uai=body.educational_institution,
    )
    if not institution:
        raise exceptions.EducationalInstitutionUnknown()
    if not institution.isActive:
        raise exceptions.EducationalInstitutionIsNotActive()

    if body.offer_venue.venueId:
        query = db.session.query(sa.func.count(offerers_models.Venue.id))
        query = query.filter(
            offerers_models.Venue.id == body.offer_venue.venueId,
            offerers_models.Venue.managingOffererId == offerer_id,
        )
        if query.scalar() == 0:
            raise offerers_exceptions.VenueNotFoundException()

    offer_venue = {
        "venueId": body.offer_venue.venueId or "",
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
        isPublicApi=True,
    )
    collective_offer.bookingEmails = body.booking_emails
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
    search.async_index_collective_offer_ids([collective_offer.id])
    logger.info(
        "Collective offer has been created",
        extra={"offerId": collective_offer.id},
    )
    return collective_offer


def edit_collective_offer_public(
    offerer_id: int,
    new_values: dict,
    offer: educational_models.CollectiveOffer,
) -> educational_models.CollectiveOffer:
    from pcapi.core.educational.api.stock import _update_educational_booking_cancellation_limit_date
    from pcapi.core.educational.api.stock import _update_educational_booking_educational_year_id

    if not (offer.isEditable and offer.collectiveStock.isEditable):
        raise exceptions.CollectiveOfferNotEditable()

    if not offer.isPublicApi:
        raise exceptions.CollectiveOfferNotEditable()

    beginning = new_values.get("beginningDatetime", offer.collectiveStock.beginningDatetime)
    students = new_values.get("students", offer.students)
    if beginning < datetime.datetime(2023, 9, 1, tzinfo=beginning.tzinfo):
        for student in students:
            if student in (
                educational_models.StudentLevels.COLLEGE5,
                educational_models.StudentLevels.COLLEGE6,
            ):
                raise StudentsNotOpenedYet()

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
            offer_validation.check_offer_subcategory_is_valid(value)
            offer_validation.check_offer_is_eligible_for_educational(value)
            offer.subcategoryId = value
        elif key == "domains":
            domains = educational_repository.get_educational_domains_from_ids(value)
            if len(domains) != len(value):
                raise exceptions.EducationalDomainsNotFound()
            offer.domains = domains
        elif key in ("educationalInstitutionId", "educationalInstitution"):
            if value is not None:
                institution = institution = educational_repository.get_educational_institution_public(
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

    search.async_index_collective_offer_ids([offer.id])

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
        search.async_index_collective_offer_ids([offer.id])
        db.session.commit()

    return offer


def publish_collective_offer_template(
    offer_template: educational_models.CollectiveOfferTemplate, user: User
) -> educational_models.CollectiveOfferTemplate:
    from pcapi.core.offers.api import update_offer_fraud_information

    if offer_template.validation == offer_mixin.OfferValidationStatus.DRAFT:
        update_offer_fraud_information(offer_template, user)
        search.async_index_collective_offer_template_ids([offer_template.id])
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


# PRIVATE


def _get_expired_collective_offer_ids(
    interval: tuple[datetime.datetime, datetime.datetime],
    page: int,
    limit: int,
) -> list[int]:
    collective_offers = educational_repository.get_expired_collective_offers(interval)
    collective_offers = collective_offers.offset(page * limit).limit(limit)
    return [offer_id for offer_id, in collective_offers.with_entities(educational_models.CollectiveOffer.id)]


def duplicate_offer_and_stock(
    original_offer: educational_models.CollectiveOffer,
) -> educational_models.CollectiveOffer:
    if original_offer.validation == offer_mixin.OfferValidationStatus.DRAFT:
        raise exceptions.ValidationFailedOnCollectiveOffer()
    offerer = original_offer.venue.managingOfferer
    if offerer.validationStatus != validation_status_mixin.ValidationStatus.VALIDATED:
        raise exceptions.OffererNotAllowedToDuplicate()

    offer = educational_models.CollectiveOffer(
        isActive=original_offer.isActive,
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
        phoneNumber=body.phone_number,  # type: ignore [call-arg]
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

    send_new_request_made_by_redactor_to_pro(request)

    return request
