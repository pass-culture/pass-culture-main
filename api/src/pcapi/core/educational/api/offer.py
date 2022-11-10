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
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import validation as offer_validation
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.routes.adage.v1.serialization import prebooking
from pcapi.routes.serialization import collective_offers_serialize
from pcapi.routes.serialization import public_api_collective_offers_serialize
from pcapi.routes.serialization.collective_offers_serialize import PostCollectiveOfferBodyModel
from pcapi.routes.serialization.collective_offers_serialize import PostCollectiveOfferTemplateBodyModel
from pcapi.routes.serialization.collective_stock_serialize import CollectiveStockCreationBodyModel
from pcapi.utils import rest
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import dehumanize_or_raise
from pcapi.utils.human_ids import humanize


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
        logger.info("[ALGOLIA] Found %d expired collective offers to unindex", len(collective_offer_ids))
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
        extra={"collectiveOfferTemplate": collective_offer_template.id, "offerId": offer_id},
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
        templateId=dehumanize(offer_data.template_id) if offer_data.template_id else None,
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
        template = get_collective_offer_template_by_id(dehumanize_or_raise(offer_data.template_id))
        rest.check_user_has_access_to_offerer(user, offerer_id=template.venue.managingOffererId)
    venue: offerers_models.Venue = rest.load_or_raise_error(offerers_models.Venue, offer_data.venue_id)
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
        extra={"collectiveOfferTemplate": collective_offer_template.id, "CollectiveOffer": offer.id},
    )
    return collective_offer_template


def get_collective_offer_by_id(offer_id: int) -> educational_models.CollectiveOffer:
    return educational_repository.get_collective_offer_by_id(offer_id)


def get_collective_offer_template_by_id(offer_id: int) -> educational_models.CollectiveOffer:
    return educational_repository.get_collective_offer_template_by_id(offer_id)


def get_collective_offer_by_id_for_adage(offer_id: int) -> educational_models.CollectiveOffer:
    return educational_repository.get_collective_offer_by_id_for_adage(offer_id)


def get_collective_offer_template_by_id_for_adage(offer_id: int) -> educational_models.CollectiveOfferTemplate:
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
    offer_id: int, educational_institution_id: int | None, user: User
) -> educational_models.CollectiveOffer:
    offer = educational_repository.get_collective_offer_by_id(offer_id)
    if educational_institution_id is not None:
        validation.check_institution_id_exists(educational_institution_id)

    if offer.collectiveStock and not offer.collectiveStock.isEditable:
        raise exceptions.CollectiveOfferNotEditable()
    offer.institutionId = educational_institution_id
    db.session.commit()

    search.async_index_collective_offer_ids([offer_id])

    if educational_institution_id is not None and offer.validation == offer_mixin.OfferValidationStatus.APPROVED:
        adage_client.notify_institution_association(serialize_collective_offer(offer))

    return offer


def create_collective_offer_public(
    offerer_id: int, body: public_api_collective_offers_serialize.PostCollectiveOfferBodyModel
) -> educational_models.CollectiveOffer:
    from pcapi.core.offers.api import update_offer_fraud_information

    offerers_api.can_offerer_create_educational_offer(offerer_id)
    venue = offerers_models.Venue.query.filter_by(id=body.venue_id).one_or_none()
    if venue is None or venue.managingOffererId != offerer_id:
        raise offerers_exceptions.VenueNotFoundException()
    typing.cast(offerers_models.Venue, venue)

    offer_validation.check_offer_subcategory_is_valid(body.subcategory_id)
    offer_validation.check_offer_is_eligible_for_educational(body.subcategory_id)
    validation.validate_offer_venue(body.offer_venue)
    validation.check_intervention_area(body.intervention_area)

    educational_domains = educational_repository.get_educational_domains_from_ids(body.domains)

    if body.educational_institution_id:
        if not educational_models.EducationalInstitution.query.filter_by(
            id=body.educational_institution_id
        ).one_or_none():
            raise exceptions.EducationalInstitutionUnknown()

    if body.offer_venue.venueId:
        query = db.session.query(sa.func.count(offerers_models.Venue.id))
        query = query.filter(
            offerers_models.Venue.id == body.offer_venue.venueId, offerers_models.Venue.managingOffererId == offerer_id
        )
        if query.scalar() == 0:
            raise offerers_exceptions.VenueNotFoundException()

    offer_venue = {
        "venueId": humanize(body.offer_venue.venueId) or "",
        "addressType": body.offer_venue.addressType,
        "otherAddress": body.offer_venue.otherAddress or "",
    }
    collective_offer = educational_models.CollectiveOffer(
        venueId=venue.id,
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
        interventionArea=body.intervention_area,
        institutionId=body.educational_institution_id,
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
    offerer_id: int, new_values: dict, offer: educational_models.CollectiveOffer
) -> educational_models.CollectiveOffer:
    if not (offer.isEditable and offer.collectiveStock.isEditable):
        raise exceptions.CollectiveOfferNotEditable()

    offer_fields = {field for field in dir(educational_models.CollectiveOffer) if not field.startswith("_")}
    stock_fields = {field for field in dir(educational_models.CollectiveStock) if not field.startswith("_")}

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
        elif key == "educationalInstitutionId":
            if value:
                if not educational_models.EducationalInstitution.query.filter_by(id=value).one_or_none():
                    raise exceptions.EducationalInstitutionUnknown()
            offer.institutionId = value
        elif key == "offerVenue":
            offer.offerVenue["venueId"] = humanize(value["venueId"]) or ""
            offer.offerVenue["addressType"] = value["addressType"].value
            offer.offerVenue["otherAddress"] = value["otherAddress"] or ""
        elif key == "bookingLimitDatetime" and value is None:
            offer.collectiveStock.bookingLimitDatetime = new_values.get(
                "beginningDatetime", offer.collectiveStock.beginningDatetime
            )
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


# PRIVATE


def _get_expired_collective_offer_ids(
    interval: tuple[datetime.datetime, datetime.datetime],
    page: int,
    limit: int,
) -> list[int]:
    collective_offers = educational_repository.get_expired_collective_offers(interval)
    collective_offers = collective_offers.offset(page * limit).limit(limit)
    return [offer_id for offer_id, in collective_offers.with_entities(educational_models.CollectiveOffer.id)]
