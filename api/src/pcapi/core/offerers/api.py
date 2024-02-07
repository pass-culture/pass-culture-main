import dataclasses
from datetime import datetime
import enum
import itertools
import logging
import re
import secrets
import time
import typing

from flask_sqlalchemy import BaseQuery
import jwt
from psycopg2.extras import NumericRange
import schwifty
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.connectors import sirene
import pcapi.connectors.thumb_storage as storage
from pcapi.core import search
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.external import zendesk_sell
from pcapi.core.external.attributes import api as external_attributes_api
import pcapi.core.finance.models as finance_models
import pcapi.core.history.api as history_api
import pcapi.core.history.models as history_models
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.users.models as users_models
import pcapi.core.users.repository as users_repository
from pcapi.models import db
from pcapi.models import feature
from pcapi.models import pc_object
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.repository import repository
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
import pcapi.routes.serialization.base as serialize_base
from pcapi.routes.serialization.offerers_serialize import OffererMemberStatus
from pcapi.utils import crypto
from pcapi.utils import human_ids
from pcapi.utils import image_conversion
import pcapi.utils.db as db_utils
import pcapi.utils.email as email_utils

from . import exceptions
from . import models
from . import repository as offerers_repository
from . import validation


logger = logging.getLogger(__name__)


class T_UNCHANGED(enum.Enum):
    TOKEN = 0


UNCHANGED = T_UNCHANGED.TOKEN
# List of fields of `Venue` which, when changed, must trigger a
# reindexation of offers.
VENUE_ALGOLIA_INDEXED_FIELDS = ["name", "publicName", "postalCode", "city", "latitude", "longitude"]
API_KEY_SEPARATOR = "_"
APE_TAG_MAPPING = {"84.11Z": "Collectivité"}
DMS_TOKEN_REGEX = r"^(?:PRO-)?([a-fA-F0-9]{12})$"


def create_digital_venue(offerer: models.Offerer) -> models.Venue:
    dms_token = generate_dms_token()
    digital_venue = models.Venue()
    digital_venue.isVirtual = True
    digital_venue.name = "Offre numérique"
    digital_venue.venueTypeCode = models.VenueTypeCode.DIGITAL
    digital_venue.managingOfferer = offerer
    digital_venue.dmsToken = dms_token
    return digital_venue


def update_venue(
    venue: models.Venue,
    author: users_models.User,
    contact_data: serialize_base.VenueContactModel | None = None,
    criteria: list[criteria_models.Criterion] | T_UNCHANGED = UNCHANGED,
    admin_update: bool = False,
    **attrs: typing.Any,
) -> models.Venue:
    validation.validate_coordinates(attrs.get("latitude"), attrs.get("longitude"))  # type: ignore [arg-type]
    reimbursement_point_id = attrs.pop("reimbursementPointId", UNCHANGED)

    modifications = {field: value for field, value in attrs.items() if venue.field_exists_and_has_changed(field, value)}

    if not admin_update:
        # run validation when the venue update is triggered by a pro
        # user. This can be bypassed when done by and admin/backoffice
        # user.
        validation.check_venue_edition(modifications, venue)

    venue_snapshot = history_api.ObjectUpdateSnapshot(venue, author)

    if contact_data:
        # target must not be None, otherwise contact_data fields will be compared to fields in Venue, which do not exist
        target = venue.contact if venue.contact is not None else offerers_models.VenueContact()
        venue_snapshot.trace_update(contact_data.dict(), target=target, field_name_template="contact.{}")
        upsert_venue_contact(venue, contact_data)

    if criteria is not UNCHANGED:
        if set(venue.criteria) != set(criteria):
            modifications["criteria"] = criteria

    if not modifications and reimbursement_point_id == UNCHANGED:
        # avoid any contact information update loss
        venue_snapshot.add_action()
        db.session.commit()
        return venue

    if reimbursement_point_id != UNCHANGED:
        # this block makes additional db requests
        current_link = venue.current_reimbursement_point_link
        current_reimbursement_point_id = current_link.reimbursementPointId if current_link else None
        if reimbursement_point_id != current_reimbursement_point_id:
            link_venue_to_reimbursement_point(venue, reimbursement_point_id)
            new_link = venue.current_reimbursement_point_link
            venue_snapshot.set(
                "reimbursementPointSiret",
                current_link.reimbursementPoint.siret if current_link else None,
                new_link.reimbursementPoint.siret if new_link else None,
            )

    old_booking_email = venue.bookingEmail if modifications.get("bookingEmail") else None

    venue_snapshot.trace_update(modifications)
    if venue.is_soft_deleted():
        raise pc_object.DeletedRecordException()
    for key, value in modifications.items():
        setattr(venue, key, value)

    venue_snapshot.add_action()

    # keep commit with repository.save() as long as venue is validated in pcapi.validation.models.venue
    repository.save(venue)

    search.async_index_venue_ids(
        [venue.id],
        reason=search.IndexationReason.VENUE_UPDATE,
        log_extra={"changes": set(modifications.keys())},
    )

    indexing_modifications_fields = set(modifications.keys()) & set(VENUE_ALGOLIA_INDEXED_FIELDS)
    if indexing_modifications_fields:
        search.async_index_offers_of_venue_ids(
            [venue.id],
            reason=search.IndexationReason.VENUE_UPDATE,
            log_extra={"changes": set(indexing_modifications_fields)},
        )

    # Former booking email address shall no longer receive emails about data related to this venue.
    # If booking email was only in this object, this will clear all columns here and it will never be updated later.
    external_attributes_api.update_external_pro(old_booking_email)
    external_attributes_api.update_external_pro(venue.bookingEmail)
    zendesk_sell.update_venue(venue)

    return venue


def update_venue_collective_data(
    venue: models.Venue,
    **attrs: typing.Any,
) -> models.Venue:
    collective_domains_in_attrs = "collectiveDomains" in attrs
    collective_legal_status_in_attrs = "collectiveLegalStatus" in attrs
    collectiveDomains = attrs.pop("collectiveDomains", None)
    collectiveLegalStatus = attrs.pop("collectiveLegalStatus", None)

    modifications = {field: value for field, value in attrs.items() if venue.field_exists_and_has_changed(field, value)}

    if collective_domains_in_attrs:
        venue.collectiveDomains = educational_repository.get_educational_domains_from_ids(collectiveDomains or [])

    if collective_legal_status_in_attrs:
        if collectiveLegalStatus:
            venue.venueEducationalStatusId = collectiveLegalStatus
        else:
            venue.venueEducationalStatusId = None

    if venue.is_soft_deleted():
        raise pc_object.DeletedRecordException()
    for key, value in modifications.items():
        setattr(venue, key, value)

    repository.save(venue)

    zendesk_sell.update_venue(venue)

    return venue


def upsert_venue_contact(venue: models.Venue, contact_data: serialize_base.VenueContactModel) -> models.Venue:
    """
    Create and attach a VenueContact to a Venue if it has none.
    Update (replace) an existing VenueContact otherwise.
    """
    venue_contact = venue.contact
    if not venue_contact:
        venue_contact = models.VenueContact()

    modifications = {
        field: value
        for field, value in contact_data.dict().items()
        if venue_contact.field_exists_and_has_changed(field, value)
    }

    if not modifications:
        return venue

    venue_contact.venue = venue
    venue_contact.email = contact_data.email
    venue_contact.website = contact_data.website
    venue_contact.phone_number = contact_data.phone_number
    venue_contact.social_medias = contact_data.social_medias or {}

    repository.save(venue_contact)
    return venue


def create_venue(
    venue_data: venues_serialize.PostVenueBodyModel, strict_accessibility_compliance: bool = True
) -> models.Venue:
    data = venue_data.dict(by_alias=True)
    validation.check_venue_creation(data, strict_accessibility_compliance)
    venue = models.Venue()
    data["dmsToken"] = generate_dms_token()
    if venue.is_soft_deleted():
        raise pc_object.DeletedRecordException()
    for key, value in data.items():
        if key == "contact":
            continue
        setattr(venue, key, value)
    if venue_data.contact:
        upsert_venue_contact(venue, venue_data.contact)
    repository.save(venue)

    if venue.siret:
        link_venue_to_pricing_point(venue, pricing_point_id=venue.id)

    search.async_index_venue_ids(
        [venue.id],
        reason=search.IndexationReason.VENUE_CREATION,
    )

    external_attributes_api.update_external_pro(venue.bookingEmail)
    zendesk_sell.create_venue(venue)

    return venue


def delete_venue(venue_id: int) -> None:
    venue_has_bookings = db.session.query(
        bookings_models.Booking.query.filter(bookings_models.Booking.venueId == venue_id).exists()
    ).scalar()
    venue_has_collective_bookings = db.session.query(
        educational_models.CollectiveBooking.query.filter(
            educational_models.CollectiveBooking.venueId == venue_id
        ).exists()
    ).scalar()

    if venue_has_bookings or venue_has_collective_bookings:
        raise exceptions.CannotDeleteVenueWithBookingsException()

    venue_used_as_pricing_point = db.session.query(
        offerers_models.VenuePricingPointLink.query.filter(
            offerers_models.VenuePricingPointLink.venueId != venue_id,
            offerers_models.VenuePricingPointLink.pricingPointId == venue_id,
        ).exists()
    ).scalar()

    if venue_used_as_pricing_point:
        raise exceptions.CannotDeleteVenueUsedAsPricingPointException()

    venue_used_as_reimbursement_point = db.session.query(
        offerers_models.VenueReimbursementPointLink.query.filter(
            offerers_models.VenueReimbursementPointLink.venueId != venue_id,
            offerers_models.VenueReimbursementPointLink.reimbursementPointId == venue_id,
        ).exists()
    ).scalar()

    if venue_used_as_reimbursement_point:
        raise exceptions.CannotDeleteVenueUsedAsReimbursementPointException()

    offer_ids_to_delete = _delete_objects_linked_to_venue(venue_id)

    # Warning: we should only delete rows where the "venueId" is the
    # venue to delete. We should NOT delete rows where the
    # "pricingPointId" or the "reimbursementId" is the venue to
    # delete. If other venues still have the "venue to delete" as
    # their pricing/reimbursement point, the database will rightfully
    # raise an error. Either these venues should be deleted first, or
    # the "venue to delete" should not be deleted.
    offerers_models.VenuePricingPointLink.query.filter_by(
        venueId=venue_id,
    ).delete(synchronize_session=False)
    offerers_models.VenueReimbursementPointLink.query.filter_by(venueId=venue_id).delete(synchronize_session=False)

    offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id).delete(synchronize_session=False)

    db.session.commit()

    search.unindex_offer_ids(offer_ids_to_delete["individual_offer_ids_to_delete"])
    search.unindex_collective_offer_ids(offer_ids_to_delete["collective_offer_ids_to_delete"])
    search.unindex_collective_offer_template_ids(offer_ids_to_delete["collective_offer_template_ids_to_delete"])
    search.unindex_venue_ids([venue_id])


def _delete_objects_linked_to_venue(venue_id: int) -> dict:
    STEP = 200

    offer_ids_to_delete: dict[str, list[int]] = {
        "individual_offer_ids_to_delete": [],
        "collective_offer_ids_to_delete": [],
        "collective_offer_template_ids_to_delete": [],
    }
    # delete offers and their dependencies
    packed_offers_id = db.session.query(offers_models.Offer.id).filter(offers_models.Offer.venueId == venue_id).all()
    offers_id = [i for i, in packed_offers_id]  # an iterable are not enough here we really need a list in memory
    offer_index = 0
    while offers_id_chunk := offers_id[offer_index : offer_index + STEP]:
        offer_index += STEP
        offer_ids_to_delete["individual_offer_ids_to_delete"].extend(offers_id_chunk)

        packed_stocks_id = (
            db.session.query(offers_models.Stock.id).filter(offers_models.Stock.offerId.in_(offers_id_chunk)).all()
        )
        stocks_id = [i for i, in packed_stocks_id]  # an iterable are not enough here we really need a list in memory
        stock_index = 0
        while stocks_id_chunk := stocks_id[stock_index : stock_index + STEP]:
            stock_index += STEP

            offers_models.ActivationCode.query.filter(
                offers_models.ActivationCode.stockId.in_(stocks_id_chunk),
                # All bookingId should be None if venue_has_bookings is False, keep condition to get an exception otherwise
                offers_models.ActivationCode.bookingId.is_(None),
            ).delete(synchronize_session=False)

        offers_models.Stock.query.filter(offers_models.Stock.offerId.in_(offers_id_chunk)).delete(
            synchronize_session=False
        )
        users_models.Favorite.query.filter(users_models.Favorite.offerId.in_(offers_id_chunk)).delete(
            synchronize_session=False
        )
        criteria_models.OfferCriterion.query.filter(criteria_models.OfferCriterion.offerId.in_(offers_id_chunk)).delete(
            synchronize_session=False
        )
        offers_models.Mediation.query.filter(offers_models.Mediation.offerId.in_(offers_id_chunk)).delete(
            synchronize_session=False
        )
    offers_models.Offer.query.filter(offers_models.Offer.venueId == venue_id).delete(synchronize_session=False)

    # delete all things providers related
    providers_models.AllocineVenueProviderPriceRule.query.filter(
        providers_models.AllocineVenueProviderPriceRule.allocineVenueProviderId
        == providers_models.AllocineVenueProvider.id,
        providers_models.AllocineVenueProvider.id == providers_models.VenueProvider.id,
        providers_models.VenueProvider.venueId == venue_id,
        offerers_models.Venue.id == venue_id,
    ).delete(synchronize_session=False)
    providers_models.AllocineVenueProvider.query.filter(
        providers_models.AllocineVenueProvider.id == providers_models.VenueProvider.id,
        providers_models.VenueProvider.venueId == venue_id,
        offerers_models.Venue.id == venue_id,
    ).delete(synchronize_session=False)
    providers_models.VenueProvider.query.filter(providers_models.VenueProvider.venueId == venue_id).delete(
        synchronize_session=False
    )
    providers_models.AllocinePivot.query.filter_by(venueId=venue_id).delete(synchronize_session=False)

    # delete collective offers and templates and their dependencies:
    packed_collective_offers_id = db.session.query(educational_models.CollectiveOffer.id).filter(
        educational_models.CollectiveOffer.venueId == venue_id
    )
    collective_offers_id = [i for i, in packed_collective_offers_id]
    collective_offer_index = 0
    while collective_offers_id_chunk := collective_offers_id[collective_offer_index : collective_offer_index + STEP]:
        collective_offer_index += STEP
        offer_ids_to_delete["collective_offer_ids_to_delete"].extend(collective_offers_id_chunk)
        educational_models.CollectiveStock.query.filter(
            educational_models.CollectiveStock.collectiveOfferId.in_(collective_offers_id_chunk)
        ).delete(synchronize_session=False)
        educational_models.CollectiveOfferEducationalRedactor.query.filter(
            educational_models.CollectiveOfferEducationalRedactor.collectiveOfferId.in_(collective_offers_id_chunk)
        ).delete(synchronize_session=False)

    educational_models.CollectiveOffer.query.filter(educational_models.CollectiveOffer.venueId == venue_id).delete(
        synchronize_session=False
    )

    packed_collective_offer_templates_id = db.session.query(educational_models.CollectiveOfferTemplate.id).filter(
        educational_models.CollectiveOfferTemplate.venueId == venue_id
    )
    collective_offer_templates_id = [i for i, in packed_collective_offer_templates_id]
    collective_offer_template_index = 0
    while collective_offer_templates_id_chunk := collective_offer_templates_id[
        collective_offer_template_index : collective_offer_template_index + STEP
    ]:
        collective_offer_template_index += STEP
        offer_ids_to_delete["collective_offer_template_ids_to_delete"].extend(collective_offer_templates_id_chunk)
        educational_models.CollectiveOffer.query.filter(
            educational_models.CollectiveOffer.templateId.in_(collective_offer_templates_id_chunk)
        ).update({"templateId": None}, synchronize_session=False)
        educational_models.CollectiveOfferTemplateEducationalRedactor.query.filter(
            educational_models.CollectiveOfferTemplateEducationalRedactor.collectiveOfferTemplateId.in_(
                collective_offer_templates_id_chunk
            )
        ).delete(synchronize_session=False)

    educational_models.CollectiveOfferTemplate.query.filter(
        educational_models.CollectiveOfferTemplate.venueId == venue_id
    ).delete(synchronize_session=False)

    finance_models.BankInformation.query.filter(finance_models.BankInformation.venueId == venue_id).delete(
        synchronize_session=False
    )
    return offer_ids_to_delete


def link_venue_to_pricing_point(
    venue: models.Venue,
    pricing_point_id: int,
    timestamp: datetime | None = None,
    force_link: bool = False,
    commit: bool = True,
) -> None:
    """
    Creates a VenuePricingPointLink if the venue had not been previously linked to a pricing point.
    If it had, then it will raise an error, unless the force_link parameter is True, in exceptional circumstances.
    """
    validation.check_venue_can_be_linked_to_pricing_point(venue, pricing_point_id)
    if not timestamp:
        timestamp = datetime.utcnow()
    current_link = models.VenuePricingPointLink.query.filter(
        models.VenuePricingPointLink.venueId == venue.id,
        models.VenuePricingPointLink.timespan.contains(timestamp),
    ).one_or_none()
    if current_link:
        if force_link:
            current_link.timespan = db_utils.make_timerange(
                current_link.timespan.lower,
                timestamp,
            )
            db.session.add(current_link)
        else:
            raise exceptions.CannotLinkVenueToPricingPoint(
                f"This Venue is already linked to Venue #{current_link.pricingPointId} for pricing"
            )
    new_link = models.VenuePricingPointLink(
        pricingPointId=pricing_point_id, venueId=venue.id, timespan=(timestamp, None)
    )
    db.session.add(new_link)
    for from_tables, where_clauses in (
        (
            "booking, stock",
            'finance_event."bookingId" is not null '
            'and booking.id = finance_event."bookingId" '
            'and stock.id = booking."stockId"',
        ),
        (
            # use aliases to have the same `set` clause
            "collective_booking as booking, collective_stock as stock",
            'finance_event."collectiveBookingId" is not null '
            'and booking.id = finance_event."collectiveBookingId" '
            'and stock.id = booking."collectiveStockId"',
        ),
    ):
        ppoint_update_result = db.session.execute(
            f"""
              update finance_event
              set
                "pricingPointId" = :pricing_point_id,
                status = :finance_event_status_ready,
                "pricingOrderingDate" = greatest(
                  booking."dateUsed",
                  stock."beginningDatetime",
                  :new_link_start
                )
              from {from_tables}
              where
                {where_clauses}
                and finance_event.status = :finance_event_status_pending
                and finance_event."pricingPointId" IS NULL
                and finance_event."venueId" = :venue_id
            """,
            {
                "venue_id": venue.id,
                "pricing_point_id": pricing_point_id,
                "finance_event_status_pending": finance_models.FinanceEventStatus.PENDING.value,
                "finance_event_status_ready": finance_models.FinanceEventStatus.READY.value,
                "new_link_start": timestamp,
            },
        )
    if commit:
        db.session.commit()
    logger.info(
        "Linked venue to pricing point",
        extra={
            "venue": venue.id,
            "new_pricing_point": pricing_point_id,
            "previous_pricing_point": current_link.pricingPointId if current_link else None,
            "updated_finance_events": ppoint_update_result.rowcount,
            "commit": commit,
        },
    )


def link_venue_to_reimbursement_point(
    venue: models.Venue,
    reimbursement_point_id: int | None,
    timestamp: datetime | None = None,
) -> None:
    if reimbursement_point_id:
        validation.check_venue_can_be_linked_to_reimbursement_point(venue, reimbursement_point_id)
    if not timestamp:
        timestamp = datetime.utcnow()
    current_link = models.VenueReimbursementPointLink.query.filter(
        models.VenueReimbursementPointLink.venueId == venue.id,
        models.VenueReimbursementPointLink.timespan.contains(timestamp),
    ).one_or_none()
    if current_link:
        if current_link.reimbursementPointId == reimbursement_point_id:
            return
        current_link.timespan = db_utils.make_timerange(
            current_link.timespan.lower,
            timestamp,
        )
        db.session.add(current_link)
        logger.info(
            "VenueReimbursementPointLink has ended",
            extra={"venue_id:": venue.id, "former_reimbursement_point_id": current_link.reimbursementPointId},
        )
    if reimbursement_point_id:
        new_link = models.VenueReimbursementPointLink(
            reimbursementPointId=reimbursement_point_id, venueId=venue.id, timespan=(timestamp, None)
        )
        db.session.add(new_link)
        logger.info(
            "VenueReimbursementPointLink has been created",
            extra={"venue_id:": venue.id, "new_reimbursement_point_id": new_link.reimbursementPointId},
        )
    db.session.commit()


def generate_and_save_api_key(offerer_id: int) -> str:
    # This is a soft limit for visual purposes only (not for security
    # reasons). A user could create more than MAX_API_KEY_PER_OFFERER
    # keys through a race condition. It's fine.
    if models.ApiKey.query.filter_by(offererId=offerer_id).count() >= settings.MAX_API_KEY_PER_OFFERER:
        raise exceptions.ApiKeyCountMaxReached()
    model_api_key, clear_api_key = generate_offerer_api_key(offerer_id)
    repository.save(model_api_key)
    return clear_api_key


def generate_offerer_api_key(offerer_id: int) -> tuple[models.ApiKey, str]:
    clear_secret = secrets.token_hex(32)
    prefix = _generate_api_key_prefix()
    key = models.ApiKey(offererId=offerer_id, prefix=prefix, secret=crypto.hash_password(clear_secret))

    return key, f"{prefix}{API_KEY_SEPARATOR}{clear_secret}"


def generate_provider_api_key(provider: providers_models.Provider) -> tuple[models.ApiKey, str]:
    offerer = provider.offererProvider.offerer if provider.offererProvider else None
    if offerer is None:
        raise exceptions.CannotFindProviderOfferer()

    clear_secret = secrets.token_hex(32)
    prefix = _generate_api_key_prefix()
    key = models.ApiKey(offerer=offerer, provider=provider, prefix=prefix, secret=crypto.hash_password(clear_secret))

    return key, f"{prefix}{API_KEY_SEPARATOR}{clear_secret}"


def _generate_api_key_prefix() -> str:
    for _ in range(100):
        prefix_identifier = secrets.token_hex(6)
        prefix = _create_prefix(settings.ENV, prefix_identifier)
        if not db.session.query(models.ApiKey.query.filter_by(prefix=prefix).exists()).scalar():
            return prefix
    raise exceptions.ApiKeyPrefixGenerationError()


def find_api_key(key: str) -> models.ApiKey | None:
    if key.count(API_KEY_SEPARATOR) != 2:
        # Handle legacy keys that did not have any prefix. They were
        # plain 64-characters strings. They have been migrated so that
        # their prefix is their first 8 characters (and the rest is
        # their secret).
        env = settings.ENV
        prefix_identifier, clear_secret = key[:8], key[8:]
    else:
        env, prefix_identifier, clear_secret = key.split(API_KEY_SEPARATOR)
    prefix = _create_prefix(env, prefix_identifier)

    api_key = (
        models.ApiKey.query.filter_by(prefix=prefix)
        .options(
            sa_orm.joinedload(models.ApiKey.offerer),
        )
        .options(sa_orm.joinedload(models.ApiKey.provider))
        .one_or_none()
    )

    if not api_key:
        return None

    return api_key if api_key.check_secret(clear_secret) else None


def _create_prefix(env: str, prefix_identifier: str) -> str:
    return f"{env}{API_KEY_SEPARATOR}{prefix_identifier}"


def delete_api_key_by_user(user: users_models.User, api_key_prefix: str) -> None:
    api_key = models.ApiKey.query.filter_by(prefix=api_key_prefix).one()

    if not user.has_access(api_key.offererId):
        raise exceptions.ApiKeyDeletionDenied()

    db.session.delete(api_key)


def _fill_in_offerer(
    offerer: offerers_models.Offerer, offerer_informations: offerers_serialize.CreateOffererQueryModel
) -> None:
    offerer.address = offerer_informations.address
    offerer.city = offerer_informations.city
    offerer.name = offerer_informations.name
    offerer.postalCode = offerer_informations.postalCode
    offerer.siren = offerer_informations.siren
    if settings.IS_INTEGRATION:
        offerer.validationStatus = ValidationStatus.VALIDATED
    else:
        offerer.validationStatus = ValidationStatus.NEW
    offerer.isActive = True
    offerer.dateCreated = datetime.utcnow()


def auto_tag_new_offerer(
    offerer: offerers_models.Offerer, siren_info: sirene.SirenInfo | None, user: users_models.User
) -> None:
    tag_names_to_apply = set()

    if siren_info:
        tag_label = APE_TAG_MAPPING.get(siren_info.ape_code)
        if tag_label:
            tag = offerers_models.OffererTag.query.filter_by(label=tag_label).one_or_none()
            if not tag:
                logger.error(
                    "Could not assign tag to offerer: tag not found in DB",
                    extra={"offerer": offerer.id, "tag_label": tag_label},
                )
            else:
                offerer.tags.append(tag)

        if not siren_info.diffusible:
            tag_names_to_apply.add("non-diffusible")

        if siren_info.siren in settings.EPN_SIREN:
            tag_names_to_apply.add("ecosysteme-epn")

    if user.email.split("@")[-1] in set(settings.NATIONAL_PARTNERS_EMAIL_DOMAINS.split(",")):
        tag_names_to_apply.add("partenaire-national")

    if tag_names_to_apply:
        tags = offerers_models.OffererTag.query.filter(offerers_models.OffererTag.name.in_(tag_names_to_apply)).all()
        if len(tags) != len(tag_names_to_apply):
            missing_tags = tag_names_to_apply - set(tag.name for tag in tags)
            logger.error(
                "Could not assign tag to offerer: tag not found in DB",
                extra={"offerer": offerer.id, "tag_name": ",".join(missing_tags)},
            )
        offerer.tags.extend(tags)

    db.session.add(offerer)


@dataclasses.dataclass
class NewOnboardingInfo:
    target: models.Target
    venueTypeCode: str
    webPresence: str | None


def _add_new_onboarding_info_to_extra_data(new_onboarding_info: NewOnboardingInfo | None, extra_data: dict) -> None:
    if new_onboarding_info:
        extra_data["target"] = new_onboarding_info.target
        extra_data["venue_type_code"] = new_onboarding_info.venueTypeCode
        extra_data["web_presence"] = new_onboarding_info.webPresence


def create_offerer(
    user: users_models.User,
    offerer_informations: offerers_serialize.CreateOffererQueryModel,
    new_onboarding_info: NewOnboardingInfo | None = None,
    author: users_models.User | None = None,
    comment: str | None = None,
    **kwargs: typing.Any,
) -> models.UserOfferer:
    offerer = offerers_repository.find_offerer_by_siren(offerer_informations.siren)
    is_new = False

    if author is None:
        author = user

    if offerer is not None:
        # The user can have his attachment rejected or deleted to the structure,
        # in this case it is passed to NEW if the structure is not rejected
        user_offerer = (
            offerers_models.UserOfferer.query.filter_by(userId=user.id, offererId=offerer.id)
            .filter(sa.or_(offerers_models.UserOfferer.isRejected, offerers_models.UserOfferer.isDeleted))  # type: ignore [type-var]
            .first()
        )
        if user_offerer:
            user_offerer.validationStatus = ValidationStatus.VALIDATED
        else:
            user_offerer = grant_user_offerer_access(offerer, user)
        db.session.add(user_offerer)

        if offerer.isRejected:
            # When offerer was rejected, it is considered as a new offerer in validation process;
            # history is kept with same id and siren
            is_new = True
            _fill_in_offerer(offerer, offerer_informations)
            comment = (comment + "\n" if comment else "") + "Nouvelle demande sur un SIREN précédemment rejeté"
        else:
            user_offerer.validationStatus = ValidationStatus.NEW
            user_offerer.dateCreated = datetime.utcnow()
            extra_data: dict[str, typing.Any] = {}
            _add_new_onboarding_info_to_extra_data(new_onboarding_info, extra_data)
            history_api.add_action(
                history_models.ActionType.USER_OFFERER_NEW,
                author,
                user=user,
                offerer=offerer,
                comment=comment,
                **extra_data,
            )
    else:
        is_new = True
        offerer = models.Offerer()
        _fill_in_offerer(offerer, offerer_informations)
        digital_venue = create_digital_venue(offerer)
        user_offerer = grant_user_offerer_access(offerer, user)
        db.session.add_all([offerer, digital_venue, user_offerer])

    assert offerer.siren  # helps mypy until Offerer.siren is set as NOT NULL
    try:
        siren_info = sirene.get_siren(offerer.siren, raise_if_non_public=False)
    except sirene.SireneException as exc:
        logger.info("Could not fetch info from Sirene API", extra={"exc": exc})
        siren_info = None

    if is_new:
        auto_tag_new_offerer(offerer, siren_info, user)

        extra_data = {}
        if siren_info:
            extra_data = {"sirene_info": dict(siren_info)}
        _add_new_onboarding_info_to_extra_data(new_onboarding_info, extra_data)
        extra_data.update(kwargs)

        history_api.add_action(
            history_models.ActionType.OFFERER_NEW, author, user=user, offerer=offerer, comment=comment, **extra_data
        )

    # keep commit with repository.save() as long as siren is validated in pcapi.validation.models.offerer
    repository.save(offerer)

    external_attributes_api.update_external_pro(user.email)
    zendesk_sell.create_offerer(offerer)

    return user_offerer


def grant_user_offerer_access(offerer: models.Offerer, user: users_models.User) -> models.UserOfferer:
    return models.UserOfferer(offerer=offerer, user=user, validationStatus=ValidationStatus.VALIDATED)


def _format_tags(tags: typing.Iterable[models.OffererTag]) -> str:
    return ", ".join(sorted(tag.label for tag in tags))


def update_offerer(
    offerer: models.Offerer,
    author: users_models.User,
    name: str | T_UNCHANGED = UNCHANGED,
    city: str | T_UNCHANGED = UNCHANGED,
    postal_code: str | T_UNCHANGED = UNCHANGED,
    address: str | T_UNCHANGED = UNCHANGED,
    tags: list[models.OffererTag] | T_UNCHANGED = UNCHANGED,
) -> None:
    modified_info: dict[str, dict[str, str | None]] = {}

    if name is not UNCHANGED and offerer.name != name:
        modified_info["name"] = {"old_info": offerer.name, "new_info": name}
        offerer.name = name
    if city is not UNCHANGED and offerer.city != city:
        modified_info["city"] = {"old_info": offerer.city, "new_info": city}
        offerer.city = city
    if postal_code is not UNCHANGED and offerer.postalCode != postal_code:
        modified_info["postalCode"] = {"old_info": offerer.postalCode, "new_info": postal_code}
        offerer.postalCode = postal_code
    if address is not UNCHANGED and offerer.address != address:
        modified_info["address"] = {"old_info": offerer.address, "new_info": address}
        offerer.address = address
    if tags is not UNCHANGED:
        if set(offerer.tags) != set(tags):
            modified_info["tags"] = {
                "old_info": _format_tags(offerer.tags) or None,
                "new_info": _format_tags(tags) or None,
            }
            offerer.tags = tags

    if modified_info:
        history_api.add_action(
            history_models.ActionType.INFO_MODIFIED, author, offerer=offerer, modified_info=modified_info
        )

    # keep commit with repository.save() as long as postal code is validated in pcapi.validation.models.offerer
    repository.save(offerer)

    zendesk_sell.update_offerer(offerer)


def remove_pro_role_and_add_non_attached_pro_role(users: list[users_models.User]) -> None:
    users_with_offerers = (
        users_models.User.query.filter(users_models.User.id.in_([user.id for user in users]))
        .options(
            sa.orm.load_only(users_models.User.roles),
            sa.orm.joinedload(users_models.User.UserOfferers)
            .load_only(models.UserOfferer.validationStatus)
            .joinedload(models.UserOfferer.offerer)
            .load_only(models.Offerer.validationStatus),
        )
        .all()
    )

    for user_with_offerers in users_with_offerers:
        if not any(
            user_offerer.isValidated and user_offerer.offerer.isValidated
            for user_offerer in user_with_offerers.UserOfferers
        ):
            user_with_offerers.add_non_attached_pro_role()


def validate_offerer_attachment(
    user_offerer: offerers_models.UserOfferer, author_user: users_models.User, comment: str | None = None
) -> None:
    if user_offerer.isValidated:
        raise exceptions.UserOffererAlreadyValidatedException()

    user_offerer.user.add_pro_role()
    user_offerer.validationStatus = ValidationStatus.VALIDATED
    db.session.add(user_offerer)

    history_api.add_action(
        history_models.ActionType.USER_OFFERER_VALIDATED,
        author=author_user,
        user=user_offerer.user,
        offerer=user_offerer.offerer,
        comment=comment,
    )

    db.session.commit()

    external_attributes_api.update_external_pro(user_offerer.user.email)

    transactional_mails.send_offerer_attachment_validation_email_to_pro(user_offerer)

    offerer_invitation = (
        models.OffererInvitation.query.filter_by(offererId=user_offerer.offererId)
        .filter_by(email=user_offerer.user.email)
        .one_or_none()
    )
    if offerer_invitation:
        transactional_mails.send_offerer_attachment_invitation_accepted(
            user_offerer.user, offerer_invitation.user.email
        )


def set_offerer_attachment_pending(
    user_offerer: offerers_models.UserOfferer, author_user: users_models.User, comment: str | None = None
) -> None:
    user_offerer.validationStatus = ValidationStatus.PENDING
    remove_pro_role_and_add_non_attached_pro_role([user_offerer.user])
    db.session.add(user_offerer)
    history_api.add_action(
        history_models.ActionType.USER_OFFERER_PENDING,
        author_user,
        user=user_offerer.user,
        offerer=user_offerer.offerer,
        comment=comment,
    )
    db.session.commit()


def reject_offerer_attachment(
    user_offerer: offerers_models.UserOfferer,
    author_user: users_models.User | None,
    comment: str | None = None,
    send_email: bool = True,
    commit: bool = True,
) -> None:
    user_offerer.validationStatus = ValidationStatus.REJECTED
    db.session.add(user_offerer)

    history_api.add_action(
        history_models.ActionType.USER_OFFERER_REJECTED,
        author_user,
        user=user_offerer.user,
        offerer=user_offerer.offerer,
        comment=comment,
    )

    if send_email:
        transactional_mails.send_offerer_attachment_rejection_email_to_pro(user_offerer)

    remove_pro_role_and_add_non_attached_pro_role([user_offerer.user])

    if commit:
        db.session.commit()


def delete_offerer_attachment(
    user_offerer: offerers_models.UserOfferer,
    author_user: users_models.User,
    comment: str | None = None,
) -> None:
    user_offerer.validationStatus = ValidationStatus.DELETED
    db.session.add(user_offerer)

    history_api.add_action(
        history_models.ActionType.USER_OFFERER_DELETED,
        author_user,
        user=user_offerer.user,
        offerer=user_offerer.offerer,
        comment=comment,
    )

    remove_pro_role_and_add_non_attached_pro_role([user_offerer.user])
    db.session.commit()


def validate_offerer(offerer: models.Offerer, author_user: users_models.User) -> None:
    if offerer.isValidated:
        raise exceptions.OffererAlreadyValidatedException()

    applicants = users_repository.get_users_with_validated_attachment_by_offerer(offerer)
    offerer.validationStatus = ValidationStatus.VALIDATED
    offerer.dateValidated = datetime.utcnow()
    offerer.isActive = True
    db.session.add(offerer)

    for applicant in applicants:
        applicant.add_pro_role()
    db.session.add_all(applicants)

    history_api.add_action(
        history_models.ActionType.OFFERER_VALIDATED,
        author_user,
        offerer=offerer,
        user=applicants[0] if applicants else None,  # before validation we should have only one applicant
    )

    db.session.commit()

    managed_venues = offerer.managedVenues
    search.async_index_offers_of_venue_ids(
        [venue.id for venue in managed_venues],
        reason=search.IndexationReason.OFFERER_VALIDATION,
    )

    for applicant in applicants:
        external_attributes_api.update_external_pro(applicant.email)

    zendesk_sell.update_offerer(offerer)

    if applicants:
        transactional_mails.send_new_offerer_validation_email_to_pro(offerer)
    for managed_venue in managed_venues:
        if managed_venue.adageId:
            emails = offerers_repository.get_emails_by_venue(managed_venue)
            transactional_mails.send_eac_offerer_activation_email(managed_venue, list(emails))
            break


def reject_offerer(
    offerer: offerers_models.Offerer, author_user: users_models.User | None, **action_args: typing.Any
) -> None:
    if offerer.isRejected:
        raise exceptions.OffererAlreadyRejectedException()

    applicants = users_repository.get_users_with_validated_attachment(offerer)
    first_user_to_register_offerer = applicants[0] if applicants else None

    was_validated = offerer.isValidated
    offerer.validationStatus = ValidationStatus.REJECTED
    offerer.dateValidated = None
    offerer.isActive = False
    db.session.add(offerer)
    history_api.add_action(
        history_models.ActionType.OFFERER_REJECTED,
        author_user,
        offerer=offerer,
        user=first_user_to_register_offerer,
        **action_args,
    )

    if applicants:
        transactional_mails.send_new_offerer_rejection_email_to_pro(offerer)

    users_offerer = offerers_models.UserOfferer.query.filter_by(offererId=offerer.id).all()
    for user_offerer in users_offerer:
        reject_offerer_attachment(
            user_offerer,
            author_user,
            "Compte pro rejeté suite au rejet de la structure",
            send_email=(user_offerer.user not in applicants),  # do not send a second email
            commit=False,
        )

    remove_pro_role_and_add_non_attached_pro_role(applicants)

    # Remove any API key which could have been created when user was waiting for validation
    models.ApiKey.query.filter(models.ApiKey.offererId == offerer.id).delete()

    db.session.commit()

    if was_validated:
        for applicant in applicants:
            external_attributes_api.update_external_pro(applicant.email)


def set_offerer_pending(
    offerer: offerers_models.Offerer,
    author_user: users_models.User,
    comment: str | None = None,
    tags_to_add: typing.Iterable[offerers_models.OffererTag] | None = None,
    tags_to_remove: typing.Iterable[offerers_models.OffererTag] | None = None,
) -> None:
    offerer.validationStatus = ValidationStatus.PENDING
    offerer.isActive = True

    applicants = users_repository.get_users_with_validated_attachment_by_offerer(offerer)
    remove_pro_role_and_add_non_attached_pro_role(applicants)

    extra_data = {}
    if tags_to_add or tags_to_remove:
        extra_data["modified_info"] = {
            "tags": {"old_info": _format_tags(tags_to_remove or set()), "new_info": _format_tags(tags_to_add or set())}
        }
        if tags_to_add:
            offerer.tags += list(tags_to_add)
        if tags_to_remove:
            offerer.tags = [tag for tag in offerer.tags if tag not in tags_to_remove]

    db.session.add(offerer)

    history_api.add_action(
        history_models.ActionType.OFFERER_PENDING,
        author_user,
        offerer=offerer,
        venue=None,  # otherwise mypy does not accept extra_data dict
        user=None,  # otherwise mypy does not accept extra_data dict
        finance_incident=None,  # otherwise mypy does not accept extra_data dict
        bank_account=None,  # otherwise mypy does not accept extra_data dict
        rule=None,  # otherwise mypy does not accept extra_data dict
        comment=comment,
        **extra_data,
    )

    db.session.commit()


def add_comment_to_offerer(offerer: offerers_models.Offerer, author_user: users_models.User, comment: str) -> None:
    history_api.add_action(history_models.ActionType.COMMENT, author_user, offerer=offerer, comment=comment)
    db.session.commit()


def add_comment_to_venue(venue: offerers_models.Venue, author_user: users_models.User, comment: str) -> None:
    history_api.add_action(history_models.ActionType.COMMENT, author_user, venue=venue, comment=comment)
    db.session.commit()


def get_timestamp_from_url(image_url: str) -> str:
    return image_url.split("_")[-1]


def rm_previous_venue_thumbs(venue: models.Venue) -> None:
    if not venue._bannerUrl:  # bannerUrl (with no undescore) always returns an url (potentially a default one)
        return

    # handle old banner urls that did not have a timestamp
    timestamp = get_timestamp_from_url(venue.bannerUrl) if "_" in venue.bannerUrl else ""
    storage.remove_thumb(venue, storage_id_suffix=str(timestamp), ignore_thumb_count=True)

    # some older venues might have a banner but not the original file
    # note: if bannerUrl is not None, bannerMeta should not be either.
    assert venue.bannerMeta is not None
    if original_image_url := venue.bannerMeta.get("original_image_url"):
        original_image_timestamp = get_timestamp_from_url(original_image_url)
        storage.remove_thumb(venue, storage_id_suffix=original_image_timestamp)

    venue.bannerUrl = None  # type: ignore [method-assign]
    venue.bannerMeta = None
    venue.thumbCount = 1


def save_venue_banner(
    user: users_models.User,
    venue: models.Venue,
    content: bytes,
    image_credit: str,
    crop_params: image_conversion.CropParams | None = None,
) -> None:
    """
    Save the new venue's new banner: crop it and resize it if asked
    or needed, and save the original image too (shrinked if too big,
    but with the same ratio).

    The previous banner (if any) is removed.

    Use a timestamps as indexes in order to have a unique URL for each
    upload.
    """
    rm_previous_venue_thumbs(venue)

    updated_at = datetime.utcnow()
    banner_timestamp = str(int(updated_at.timestamp()))
    storage.create_thumb(
        model_with_thumb=venue,
        image_as_bytes=content,
        storage_id_suffix_str=banner_timestamp,
        crop_params=crop_params,
        ratio=image_conversion.ImageRatio.LANDSCAPE,
    )

    original_image_timestamp = str(int(updated_at.timestamp() + 1))
    storage.create_thumb(
        model_with_thumb=venue, image_as_bytes=content, storage_id_suffix_str=original_image_timestamp, keep_ratio=True
    )

    venue.bannerUrl = f"{venue.thumbUrl}_{banner_timestamp}"  # type: ignore [method-assign]
    venue.bannerMeta = {
        "image_credit": image_credit,
        "author_id": user.id,
        "original_image_url": f"{venue.thumbUrl}_{original_image_timestamp}",
        "crop_params": crop_params,
        "updated_at": updated_at,
    }

    repository.save(venue)

    search.async_index_venue_ids(
        [venue.id],
        reason=search.IndexationReason.VENUE_BANNER_UPDATE,
    )


def delete_venue_banner(venue: models.Venue) -> None:
    rm_previous_venue_thumbs(venue)
    repository.save(venue)
    search.async_index_venue_ids(
        [venue.id],
        reason=search.IndexationReason.VENUE_BANNER_DELETION,
    )


def can_offerer_create_educational_offer(offerer_id: int) -> None:
    import pcapi.core.educational.adage_backends as adage_client

    if settings.CAN_COLLECTIVE_OFFERER_IGNORE_ADAGE:
        return

    if offerers_repository.offerer_has_venue_with_adage_id(offerer_id):
        return

    siren = offerers_repository.find_siren_by_offerer_id(offerer_id)
    try:
        response = adage_client.get_adage_offerer(siren)
        if len(response) == 0:
            raise educational_exceptions.CulturalPartnerNotFoundException(
                "No venue has been found for the selected siren"
            )
    except (
        educational_exceptions.CulturalPartnerNotFoundException,
        educational_exceptions.AdageException,
    ) as exception:
        raise exception


def can_venue_create_educational_offer(venue_id: int) -> None:
    import pcapi.core.educational.adage_backends as adage_client

    offerer = (
        offerers_models.Offerer.query.join(offerers_models.Venue, offerers_models.Offerer.managedVenues)
        .filter(offerers_models.Venue.id == venue_id)
        .one()
    )

    if offerers_repository.offerer_has_venue_with_adage_id(offerer.id):
        return

    siren = offerers_repository.find_siren_by_offerer_id(offerer.id)

    try:
        response = adage_client.get_adage_offerer(siren)
        if len(response) == 0:
            raise educational_exceptions.CulturalPartnerNotFoundException(
                "No venue has been found for the selected siren"
            )
    except (
        educational_exceptions.CulturalPartnerNotFoundException,
        educational_exceptions.AdageException,
    ) as exception:
        raise exception


def get_educational_offerers(offerer_id: int | None, current_user: users_models.User) -> list[models.Offerer]:
    if current_user.has_admin_role and not offerer_id:
        logger.info("Admin user must provide offerer_id as a query parameter")
        raise exceptions.MissingOffererIdQueryParameter

    if offerer_id and current_user.has_admin_role:
        offerers = (
            models.Offerer.query.filter(
                models.Offerer.isValidated,
                models.Offerer.isActive.is_(True),
                models.Offerer.id == offerer_id,
            )
            .options(sa.orm.joinedload(models.Offerer.managedVenues))
            .all()
        )
    else:
        offerers = (
            offerers_repository.get_all_offerers_for_user(
                user=current_user,
                validated=True,
            )
            .options(sa.orm.joinedload(models.Offerer.managedVenues))
            .distinct(models.Offerer.id)
            .all()
        )
    return offerers


def get_venues_by_batch(
    max_venues: int | None = None,
) -> typing.Generator[models.Venue, None, None]:
    query = models.Venue.query.order_by(models.Venue.id)

    if max_venues:
        query = query.limit(max_venues)

    for venue in query.yield_per(1_000):
        yield venue


def get_offerer_by_collective_offer_id(collective_offer_id: int) -> models.Offerer:
    return offerers_repository.get_by_collective_offer_id(collective_offer_id)


def get_offerer_by_collective_offer_template_id(collective_offer_id: int) -> models.Offerer:
    return offerers_repository.get_by_collective_offer_template_id(collective_offer_id)


def has_venue_at_least_one_bookable_offer(venue: models.Venue) -> bool:
    if not feature.FeatureToggle.ENABLE_VENUE_STRICT_SEARCH.is_active():
        return True

    if not venue.is_eligible_for_search or not venue.isReleased:
        return False

    at_least_one_eligible_offer_query = (
        offers_models.Stock.query.join(offers_models.Offer)
        .filter(offers_models.Offer.venueId == venue.id)
        .filter(offers_models.Offer.is_eligible_for_search)
        .exists()
    )

    return db.session.query(at_least_one_eligible_offer_query).scalar()


def generate_dms_token() -> str:
    """
    Returns a 12-char hex str of 6 random bytes
    The collision probability is 0.001 for 750k Venues
    """
    for _i in range(10):
        dms_token = secrets.token_hex(6)
        if not offerers_repository.dms_token_exists(dms_token):
            return dms_token
    raise ValueError("Could not generate new dmsToken for Venue")


def get_venues_educational_statuses() -> list[offerers_models.VenueEducationalStatus]:
    return offerers_repository.get_venues_educational_statuses()


def get_venue_by_id(venue_id: int) -> offerers_models.Venue:
    return offerers_repository.get_venue_by_id(venue_id)


def search_offerer(search_query: str, departments: typing.Iterable[str] = ()) -> BaseQuery:
    offerers = models.Offerer.query

    search_query = search_query.strip() if search_query else ""
    if not search_query:
        return offerers.filter(False)

    if departments:
        offerers = offerers.filter(models.Offerer.departementCode.in_(departments))  # type: ignore [attr-defined]

    if search_query.isnumeric():
        if len(search_query) == 9:
            offerers = offerers.filter(
                sa.or_(models.Offerer.id == int(search_query), models.Offerer.siren == search_query)
            )
        else:
            offerers = offerers.filter(models.Offerer.id == int(search_query))
    else:
        offerers = offerers.filter(
            sa.func.similarity(models.Offerer.name, search_query) > settings.BACKOFFICE_SEARCH_SIMILARITY_MINIMAL_SCORE
        )
        # Always order by similarity when searching by name
        offerers = offerers.order_by(sa.desc(sa.func.similarity(models.Offerer.name, search_query)))

    # At the end, order by id, in case of equal similarity score
    offerers = offerers.order_by(models.Offerer.id)

    return offerers


def get_offerer_base_query(offerer_id: int) -> BaseQuery:
    return models.Offerer.query.filter(models.Offerer.id == offerer_id)


def search_venue(search_query: str, departments: typing.Iterable[str] = ()) -> BaseQuery:
    venues = models.Venue.query.outerjoin(models.VenueContact).options(
        sa.orm.joinedload(models.Venue.contact),
        sa.orm.joinedload(models.Venue.managingOfferer),
    )

    search_query = search_query.strip()
    if not search_query:
        return venues.filter(False)

    if departments:
        venues = venues.filter(models.Venue.departementCode.in_(departments))

    if search_query.isnumeric():
        if len(search_query) == 14:
            venues = venues.filter(sa.or_(models.Venue.id == int(search_query), models.Venue.siret == search_query))
        # for dmsToken containing digits only
        elif len(search_query) == 12:
            venues = venues.filter(sa.or_(models.Venue.id == int(search_query), models.Venue.dmsToken == search_query))
        else:
            venues = venues.filter(models.Venue.id == int(search_query))
    else:
        # email
        sanitized_term = email_utils.sanitize_email(search_query)
        if email_utils.is_valid_email(sanitized_term):
            venues = venues.filter(
                sa.or_(models.Venue.bookingEmail == sanitized_term, models.VenueContact.email == sanitized_term)
            )
        elif email_utils.is_valid_email_domain(sanitized_term):
            # search for all emails @domain.ext
            venues = venues.filter(
                sa.or_(
                    models.Venue.bookingEmail.like(f"%{sanitized_term}"),
                    models.VenueContact.email.like(f"%{sanitized_term}"),
                )
            )
        # dmsToken
        # We theoretically can have venues which name is 12 letters between a and f
        # But it never happened in the database, and it's costly to handle
        elif dms_token_term := re.match(DMS_TOKEN_REGEX, search_query):
            venues = venues.filter(models.Venue.dmsToken == dms_token_term.group(1).lower())
        else:
            # non-numeric terms are searched by trigram distance in the name
            venues = venues.filter(
                sa.or_(
                    sa.func.similarity(models.Venue.name, search_query)
                    > settings.BACKOFFICE_SEARCH_SIMILARITY_MINIMAL_SCORE,
                    sa.func.similarity(models.Venue.publicName, search_query)
                    > settings.BACKOFFICE_SEARCH_SIMILARITY_MINIMAL_SCORE,
                )
            ).order_by(
                # Always order by similarity when searching by name
                sa.desc(
                    sa.func.greatest(
                        sa.func.similarity(models.Venue.name, search_query),
                        sa.func.similarity(models.Venue.publicName, search_query),
                    )
                )
            )

    # At the end, order by id, in case of equal similarity score
    venues = venues.order_by(models.Venue.id)

    return venues


def get_venue_base_query(venue_id: int) -> BaseQuery:
    return models.Venue.query.outerjoin(offerers_models.VenueContact).filter(models.Venue.id == venue_id)


def get_bank_account_base_query(bank_account_id: int) -> BaseQuery:
    return finance_models.BankAccount.filter(finance_models.BankAccount.id == bank_account_id)


def search_bank_account(search_query: str, *_: typing.Any) -> BaseQuery:
    bank_accounts_query = finance_models.BankAccount.query.options(
        sa.orm.joinedload(finance_models.BankAccount.offerer)
    )

    search_query = search_query.strip()
    if not search_query:
        return bank_accounts_query.filter(False)

    filters = []

    try:
        dehumanized_id = human_ids.dehumanize(search_query)
    except human_ids.NonDehumanizableId:
        pass
    else:
        filters.append(finance_models.BankAccount.id == dehumanized_id)

    try:
        iban = schwifty.IBAN(search_query)
    except ValueError:  # All SchwiftyException are ValueError
        pass
    else:
        filters.append(finance_models.BankAccount.iban == iban.compact)

    if not filters:
        return bank_accounts_query.filter(False)

    return bank_accounts_query.filter(sa.or_(*filters) if len(filters) > 0 else filters[0])


def get_offerer_total_revenue(offerer_id: int) -> float:
    individual_revenue_query = sa.select(
        sa.func.coalesce(
            sa.func.sum(bookings_models.Booking.amount * bookings_models.Booking.quantity),
            0.0,
        )
    ).filter(
        bookings_models.Booking.offererId == offerer_id,
        bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED.value,
    )
    collective_revenue_query = (
        sa.select(
            sa.func.coalesce(
                sa.func.sum(educational_models.CollectiveStock.price),
                0.0,
            )
        )
        .select_from(
            educational_models.CollectiveBooking,
        )
        .join(
            educational_models.CollectiveStock,
            onclause=educational_models.CollectiveStock.id == educational_models.CollectiveBooking.collectiveStockId,
        )
        .filter(
            educational_models.CollectiveBooking.offererId == offerer_id,
            educational_models.CollectiveBooking.status != bookings_models.BookingStatus.CANCELLED.value,
        )
    )

    total_revenue_query = sa.select(
        individual_revenue_query.scalar_subquery() + collective_revenue_query.scalar_subquery()
    )

    return db.session.execute(total_revenue_query).scalar() or 0.0


def get_offerer_offers_stats(offerer_id: int, max_offer_count: int = 0) -> dict:
    def _get_query(offer_class: type[offers_api.AnyOffer]) -> BaseQuery:
        return sa.select(sa.func.jsonb_object_agg(sa.text("status"), sa.text("number"))).select_from(
            sa.select(
                sa.case(
                    (offer_class.isActive.is_(True), "active"),  # type: ignore [attr-defined]
                    (offer_class.isActive.is_(False), "inactive"),  # type: ignore [attr-defined]
                ).label("status"),
                sa.func.count(offer_class.id).label("number"),
            )
            .select_from(offerers_models.Venue)
            .outerjoin(offer_class)
            .filter(
                offerers_models.Venue.managingOffererId == offerer_id,
                # TODO: remove filter on isActive when all DRAFT and PENDING collective_offers are effectively at isActive = False
                sa.or_(
                    sa.and_(
                        offer_class.isActive.is_(True),  # type: ignore [attr-defined]
                        offer_class.validation == offers_models.OfferValidationStatus.APPROVED.value,
                    ),
                    sa.and_(
                        offer_class.isActive.is_(False),  # type: ignore [attr-defined]
                        offer_class.validation.in_(  # type: ignore [attr-defined]
                            [
                                offers_models.OfferValidationStatus.APPROVED.value,
                                offers_models.OfferValidationStatus.PENDING.value,
                                offers_models.OfferValidationStatus.DRAFT.value,
                            ]
                        ),
                    ),
                ),
            )
            .group_by(offer_class.isActive)
            .subquery()
        )

    def _max_count_query(offer_class: type[offers_api.AnyOffer]) -> BaseQuery:
        return sa.select(sa.func.count(sa.text("offer_id"))).select_from(
            sa.select(offer_class.id.label("offer_id"))  # type: ignore [attr-defined]
            .join(offerers_models.Venue, offer_class.venue)
            .filter(offerers_models.Venue.managingOffererId == offerer_id)
            .limit(max_offer_count)
            .subquery()
        )

    def _get_stats_for_offer_type(offer_class: type[offers_api.AnyOffer]) -> dict:
        if max_offer_count and db.session.execute(_max_count_query(offer_class)).scalar() >= max_offer_count:
            return {
                "active": -1,
                "inactive": -1,
            }
        (data,) = db.session.execute(_get_query(offer_class)).one()
        return {
            "active": data.get("active", 0) if data else 0,
            "inactive": data.get("inactive", 0) if data else 0,
        }

    return {
        "offer": _get_stats_for_offer_type(offers_models.Offer),
        "collective_offer": _get_stats_for_offer_type(educational_models.CollectiveOffer),
        "collective_offer_template": _get_stats_for_offer_type(educational_models.CollectiveOfferTemplate),
    }


def get_venue_total_revenue(venue_id: int) -> float:
    individual_revenue_query = sa.select(
        sa.func.coalesce(
            sa.func.sum(bookings_models.Booking.amount * bookings_models.Booking.quantity),
            0.0,
        )
    ).filter(
        bookings_models.Booking.venueId == venue_id,
        bookings_models.Booking.status != bookings_models.BookingStatus.CANCELLED.value,
    )
    collective_revenue_query = (
        sa.select(
            sa.func.coalesce(
                sa.func.sum(educational_models.CollectiveStock.price),
                0.0,
            )
        )
        .select_from(educational_models.CollectiveBooking)
        .join(educational_models.CollectiveBooking.collectiveStock)
        .filter(
            educational_models.CollectiveBooking.venueId == venue_id,
            educational_models.CollectiveBooking.status != bookings_models.BookingStatus.CANCELLED.value,
        )
    )

    total_revenue_query = sa.select(
        individual_revenue_query.scalar_subquery() + collective_revenue_query.scalar_subquery()
    )

    return db.session.execute(total_revenue_query).scalar() or 0.0


def get_venue_offers_stats(venue_id: int, max_offer_count: int = 0) -> dict:
    def _get_query(offer_class: type[offers_api.AnyOffer]) -> BaseQuery:
        return sa.select(sa.func.jsonb_object_agg(sa.text("status"), sa.text("number"))).select_from(
            sa.select(
                sa.case(
                    (offer_class.isActive.is_(True), "active"),  # type: ignore [attr-defined]
                    (offer_class.isActive.is_(False), "inactive"),  # type: ignore [attr-defined]
                ).label("status"),
                sa.func.count(offer_class.id).label("number"),
            )
            .select_from(offerers_models.Venue)
            .outerjoin(offer_class)
            .filter(
                # TODO: remove filter on isActive when all DRAFT and PENDING collective_offers are effectively at isActive = False
                sa.or_(
                    sa.and_(
                        offer_class.isActive.is_(True),  # type: ignore [attr-defined]
                        offer_class.venueId == venue_id,
                        offer_class.validation == offers_models.OfferValidationStatus.APPROVED.value,
                    ),
                    sa.and_(
                        offer_class.isActive.is_(False),  # type: ignore [attr-defined]
                        offer_class.venueId == venue_id,
                        offer_class.validation.in_(  # type: ignore [attr-defined]
                            [
                                offers_models.OfferValidationStatus.APPROVED.value,
                                offers_models.OfferValidationStatus.PENDING.value,
                                offers_models.OfferValidationStatus.DRAFT.value,
                            ]
                        ),
                    ),
                ),
            )
            .group_by(offer_class.isActive)
            .subquery()
        )

    def _max_count_query(offer_class: type[offers_api.AnyOffer]) -> BaseQuery:
        return sa.select(sa.func.count(sa.text("offer_id"))).select_from(
            sa.select(offer_class.id.label("offer_id"))  # type: ignore [attr-defined]
            .filter(offer_class.venueId == venue_id)
            .limit(max_offer_count)
            .subquery()
        )

    def _get_stats_for_offer_type(offer_class: type[offers_api.AnyOffer]) -> dict:
        if max_offer_count and db.session.execute(_max_count_query(offer_class)).scalar() >= max_offer_count:
            return {
                "active": -1,
                "inactive": -1,
            }
        (data,) = db.session.execute(_get_query(offer_class)).one()
        return {
            "active": data.get("active", 0) if data else 0,
            "inactive": data.get("inactive", 0) if data else 0,
        }

    return {
        "offer": _get_stats_for_offer_type(offers_models.Offer),
        "collective_offer": _get_stats_for_offer_type(educational_models.CollectiveOffer),
        "collective_offer_template": _get_stats_for_offer_type(educational_models.CollectiveOfferTemplate),
    }


def count_offerers_by_validation_status() -> dict[str, int]:
    stats = dict(
        offerers_models.Offerer.query.with_entities(
            offerers_models.Offerer.validationStatus,
            sa.func.count(offerers_models.Offerer.validationStatus).label("count"),
        )
        .group_by(offerers_models.Offerer.validationStatus)
        .all()
    )

    # Ensure that the result includes every status, even if no offerer has this status
    return {status.name: stats.get(status, 0) for status in ValidationStatus}


def update_offerer_tag(
    offerer_tag: models.OffererTag,
    name: str | T_UNCHANGED = UNCHANGED,
    label: str | T_UNCHANGED = UNCHANGED,
    description: str | T_UNCHANGED = UNCHANGED,
    categories: list[models.OffererTagCategory] | T_UNCHANGED = UNCHANGED,
) -> None:
    if name is not UNCHANGED:
        offerer_tag.name = name
    if label is not UNCHANGED:
        offerer_tag.label = label
    if description is not UNCHANGED:
        offerer_tag.description = description
    if categories is not UNCHANGED:
        if set(offerer_tag.categories) != set(categories):
            offerer_tag.categories = categories

    db.session.add(offerer_tag)
    db.session.commit()


def get_metabase_stats_iframe_url(
    offerer: models.Offerer,
    venues: typing.Sequence[models.Venue],
) -> str:
    """Generate a JWT-secured URL to a Metabase dashboard that shows
    statistics about one or more venues.
    """
    if not {venue.managingOffererId for venue in venues}.issubset({offerer.id}):
        raise ValueError("Cannot specify venue of another offerer")
    payload = {
        "resource": {"dashboard": settings.METABASE_DASHBOARD_ID},
        "params": {"siren": [offerer.siren], "venueid": [str(venue.id) for venue in venues]},
        # The dashboard token expires after 10 min. After that delay,
        # the user has to refresh their page to interact with the
        # dashbord (e.g to export content).
        "exp": round(time.time()) + (60 * 10),
    }
    token = jwt.encode(payload, settings.METABASE_SECRET_KEY, algorithm="HS256")
    return f"{settings.METABASE_SITE_URL}/embed/dashboard/{token}#bordered=false&titled=false"


def create_venue_registration(venue_id: int, target: offerers_models.Target, web_presence: str | None) -> None:
    venue_registration = offerers_models.VenueRegistration(venueId=venue_id, target=target, webPresence=web_presence)
    repository.save(venue_registration)


def create_from_onboarding_data(
    user: users_models.User,
    onboarding_data: offerers_serialize.SaveNewOnboardingDataQueryModel,
) -> models.UserOfferer:
    # Get name (raison sociale) from Sirene API
    siret_info = sirene.get_siret(onboarding_data.siret)
    if not siret_info.active:
        raise exceptions.InactiveSirenException()
    name = siret_info.name

    # Create Offerer or attach user to existing Offerer
    offerer_creation_info = offerers_serialize.CreateOffererQueryModel(
        address=onboarding_data.address,
        city=onboarding_data.city,
        latitude=onboarding_data.latitude,
        longitude=onboarding_data.longitude,
        name=name,
        postalCode=onboarding_data.postalCode,
        siren=onboarding_data.siret[:9],
    )
    new_onboarding_info = NewOnboardingInfo(
        target=onboarding_data.target,
        venueTypeCode=onboarding_data.venueTypeCode,
        webPresence=onboarding_data.webPresence,
    )
    user_offerer = create_offerer(user, offerer_creation_info, new_onboarding_info)

    # Create Venue with siret if it's not in DB yet, or Venue without siret if requested
    venue = offerers_repository.find_venue_by_siret(onboarding_data.siret)
    if not venue or onboarding_data.createVenueWithoutSiret:
        common_kwargs = dict(
            address=onboarding_data.address or "n/d",  # handle empty VoieEtablissement from Sirene API
            banId=onboarding_data.banId,
            bookingEmail=user.email,
            city=onboarding_data.city,
            latitude=onboarding_data.latitude,
            longitude=onboarding_data.longitude,
            managingOffererId=user_offerer.offererId,
            name=name,
            publicName=onboarding_data.publicName,
            postalCode=onboarding_data.postalCode,
            venueLabelId=None,
            venueTypeCode=onboarding_data.venueTypeCode,
            withdrawalDetails=None,
            description=None,
            contact=None,
            audioDisabilityCompliant=None,
            mentalDisabilityCompliant=None,
            motorDisabilityCompliant=None,
            visualDisabilityCompliant=None,
        )
        if onboarding_data.createVenueWithoutSiret:
            comment_and_siret = dict(
                comment="Lieu sans SIRET car dépend du SIRET d'un autre lieu",
                siret=None,
            )
        else:
            comment_and_siret = dict(
                comment=None,
                siret=onboarding_data.siret,
            )
        venue_kwargs = common_kwargs | comment_and_siret
        venue_creation_info = venues_serialize.PostVenueBodyModel(**venue_kwargs)  # type: ignore [arg-type]
        venue = create_venue(venue_creation_info, strict_accessibility_compliance=False)
        create_venue_registration(venue.id, new_onboarding_info.target, new_onboarding_info.webPresence)

    # Send welcome email only in the case of offerer creation
    if user_offerer.validationStatus == ValidationStatus.VALIDATED:
        transactional_mails.send_welcome_to_pro_email(user, venue)

    return user_offerer


def suspend_offerer(offerer: models.Offerer, actor: users_models.User, comment: str | None) -> None:
    if not offerer.isActive:
        return

    if bookings_repository.offerer_has_ongoing_bookings(offerer.id):
        raise exceptions.CannotSuspendOffererWithBookingsException()

    offerer.isActive = False
    db.session.add(offerer)
    history_api.add_action(history_models.ActionType.OFFERER_SUSPENDED, author=actor, offerer=offerer, comment=comment)
    db.session.commit()

    _update_external_offerer(offerer)


def unsuspend_offerer(offerer: models.Offerer, actor: users_models.User, comment: str | None) -> None:
    if offerer.isActive:
        return

    offerer.isActive = True
    db.session.add(offerer)
    history_api.add_action(
        history_models.ActionType.OFFERER_UNSUSPENDED, author=actor, offerer=offerer, comment=comment
    )
    db.session.commit()

    _update_external_offerer(offerer)


def _update_external_offerer(offerer: models.Offerer) -> None:
    for email in offerers_repository.get_emails_by_offerer(offerer):
        external_attributes_api.update_external_pro(email)

    zendesk_sell.update_offerer(offerer)


def delete_offerer(offerer_id: int) -> None:
    offerer_has_bookings = db.session.query(
        bookings_models.Booking.query.filter(bookings_models.Booking.offererId == offerer_id).exists()
    ).scalar()

    offerer_has_collective_bookings = db.session.query(
        educational_models.CollectiveBooking.query.filter(
            educational_models.CollectiveBooking.offererId == offerer_id
        ).exists()
    ).scalar()

    if offerer_has_bookings or offerer_has_collective_bookings:
        raise exceptions.CannotDeleteOffererWithBookingsException()

    venue_ids_subquery = offerers_models.Venue.query.filter_by(managingOffererId=offerer_id).with_entities(
        offerers_models.Venue.id
    )
    venue_ids = [venue_id[0] for venue_id in venue_ids_subquery.all()]

    offer_ids_to_delete: dict = {
        "individual_offer_ids_to_delete": [],
        "collective_offer_ids_to_delete": [],
        "collective_offer_template_ids_to_delete": [],
    }
    for venue_id in venue_ids:
        venue_offer_ids_to_delete = _delete_objects_linked_to_venue(venue_id)
        offer_ids_to_delete["individual_offer_ids_to_delete"] += venue_offer_ids_to_delete[
            "individual_offer_ids_to_delete"
        ]
        offer_ids_to_delete["collective_offer_ids_to_delete"] += venue_offer_ids_to_delete[
            "collective_offer_ids_to_delete"
        ]

        offer_ids_to_delete["collective_offer_template_ids_to_delete"] += venue_offer_ids_to_delete[
            "collective_offer_template_ids_to_delete"
        ]

    finance_models.BankInformation.query.filter(finance_models.BankInformation.offererId == offerer_id).delete(
        synchronize_session=False
    )

    offerers_models.VenuePricingPointLink.query.filter(
        offerers_models.VenuePricingPointLink.venueId.in_(venue_ids_subquery)
        | offerers_models.VenuePricingPointLink.pricingPointId.in_(venue_ids_subquery),
    ).delete(synchronize_session=False)
    offerers_models.VenueReimbursementPointLink.query.filter(
        offerers_models.VenueReimbursementPointLink.venueId.in_(venue_ids_subquery)
        | offerers_models.VenueReimbursementPointLink.reimbursementPointId.in_(venue_ids_subquery),
    ).delete(synchronize_session=False)
    offerers_models.Venue.query.filter(offerers_models.Venue.managingOffererId == offerer_id).delete(
        synchronize_session=False
    )

    offerers_models.UserOfferer.query.filter(offerers_models.UserOfferer.offererId == offerer_id).delete(
        synchronize_session=False
    )

    offerers_models.ApiKey.query.filter(offerers_models.ApiKey.offererId == offerer_id).delete(
        synchronize_session=False
    )

    offerers_models.Offerer.query.filter(offerers_models.Offerer.id == offerer_id).delete()

    db.session.commit()

    search.unindex_offer_ids(offer_ids_to_delete["individual_offer_ids_to_delete"])
    search.unindex_collective_offer_ids(offer_ids_to_delete["collective_offer_ids_to_delete"])
    search.unindex_collective_offer_template_ids(offer_ids_to_delete["collective_offer_template_ids_to_delete"])
    search.unindex_venue_ids(venue_ids_subquery)


def invite_member(offerer: models.Offerer, email: str, current_user: users_models.User) -> None:
    existing_invited_email = (
        models.OffererInvitation.query.filter(models.OffererInvitation.offererId == offerer.id)
        .filter(models.OffererInvitation.email == email)
        .one_or_none()
    )

    if existing_invited_email:  # already invited
        raise exceptions.EmailAlreadyInvitedException()

    existing_user = (
        users_models.User.query.filter(users_models.User.email == email)
        .outerjoin(users_models.User.UserOfferers)
        .options(sa.orm.joinedload(users_models.User.UserOfferers).load_only(models.UserOfferer.offererId))
        .one_or_none()
    )

    if existing_user and next(
        (u_o for u_o in existing_user.UserOfferers if u_o.offererId == offerer.id), None
    ):  # User already attached to the offerer
        raise exceptions.UserAlreadyAttachedToOffererException()

    if existing_user and existing_user.isEmailValidated:  # User exists but not attached to the offerer
        offerer_invitation = models.OffererInvitation(
            user=current_user, offerer=offerer, email=email, status=models.InvitationStatus.ACCEPTED
        )
        new_user_offerer = models.UserOfferer(
            offerer=offerer, user=existing_user, validationStatus=ValidationStatus.NEW
        )
        db.session.add_all([offerer_invitation, new_user_offerer])
        history_api.add_action(
            history_models.ActionType.USER_OFFERER_NEW,
            current_user,
            user=existing_user,
            offerer=offerer_invitation.offerer,
            comment="Rattachement créé par invitation",
            inviter_user_id=current_user.id,
            offerer_invitation_id=offerer_invitation.id,
        )
        db.session.commit()
        logger.info(
            "Existing user invited to join offerer",
            extra={"offerer": offerer.id, "invited_user": existing_user.id, "invited_by": current_user.id},
        )
        external_attributes_api.update_external_pro(existing_user.email)
        zendesk_sell.create_offerer(offerer)
    else:  # User not exists or exists with not validated email yet
        offerer_invitation = models.OffererInvitation(
            offerer=offerer, email=email, user=current_user, status=models.InvitationStatus.PENDING
        )
        db.session.add(offerer_invitation)
        db.session.commit()
        logger.info(
            "New user invited to join offerer",
            extra={"offerer": offerer.id, "invited_user": email, "invited_by": current_user.id},
        )

    transactional_mails.send_offerer_attachment_invitation([email], offerer=offerer, user=existing_user)


def get_offerer_members(offerer: models.Offerer) -> list[tuple[str, OffererMemberStatus]]:
    users_offerers = (
        models.UserOfferer.query.filter(
            models.UserOfferer.offererId == offerer.id, sa.not_(models.UserOfferer.isRejected)
        )
        .options(sa.orm.joinedload(models.UserOfferer.user).load_only(users_models.User.email))
        .all()
    )
    invited_members = (
        models.OffererInvitation.query.filter_by(offererId=offerer.id)
        .filter_by(status=models.InvitationStatus.PENDING)
        .all()
    )
    members = [
        (
            user_offerer.user.email,
            OffererMemberStatus.VALIDATED if user_offerer.isValidated else OffererMemberStatus.PENDING,
        )
        for user_offerer in users_offerers
    ]
    members = members + [(invited_member.email, OffererMemberStatus.PENDING) for invited_member in invited_members]
    members.sort(key=lambda member: (member[1].value, member[0]))
    return members


def accept_offerer_invitation_if_exists(user: users_models.User) -> None:
    offerer_invitations = (
        models.OffererInvitation.query.filter_by(email=user.email)
        .filter_by(status=offerers_models.InvitationStatus.PENDING)
        .all()
    )
    if not offerer_invitations:
        return
    for offerer_invitation in offerer_invitations:
        inviter_user = offerer_invitation.user
        user_offerer = models.UserOfferer(
            offerer=offerer_invitation.offerer, user=user, validationStatus=ValidationStatus.NEW
        )
        history_api.add_action(
            history_models.ActionType.USER_OFFERER_NEW,
            user,
            user=user,
            offerer=offerer_invitation.offerer,
            comment="Rattachement créé par invitation",
            inviter_user_id=inviter_user.id,
            offerer_invitation_id=offerer_invitation.id,
        )
        offerer_invitation.status = offerers_models.InvitationStatus.ACCEPTED
        db.session.add_all([user_offerer, offerer_invitation])
        db.session.commit()
        external_attributes_api.update_external_pro(user.email)
        zendesk_sell.create_offerer(user_offerer.offerer)
        logger.info(
            "UserOfferer created from invitation",
            extra={"offerer": user_offerer.offerer, "invitedUserId": user.id, "inviterUserId": inviter_user.id},
        )


@dataclasses.dataclass
class OffererVenues:
    offerer: offerers_models.Offerer
    venues: typing.Sequence[offerers_models.Venue]


def get_providers_offerer_and_venues(
    provider: providers_models.Provider, siren: str | None = None
) -> typing.Generator[OffererVenues, None, None]:
    offerers_query = (
        db.session.query(offerers_models.Offerer, offerers_models.Venue)
        .join(offerers_models.Venue, offerers_models.Offerer.managedVenues)
        .join(providers_models.VenueProvider, offerers_models.Venue.venueProviders)
        .join(providers_models.Provider, providers_models.VenueProvider.provider)
        .filter(providers_models.VenueProvider.provider == provider)
        .filter(providers_models.VenueProvider.isActive)
        .order_by(offerers_models.Offerer.id, offerers_models.Venue.id)
    )

    if siren:
        offerers_query = offerers_query.filter(offerers_models.Offerer.siren == siren)

    for offerer, group in itertools.groupby(offerers_query, lambda row: row.Offerer):
        yield OffererVenues(offerer=offerer, venues=[row.Venue for row in group])


def get_offerer_stats_data(offerer_id: int) -> list[offerers_models.OffererStats]:
    return offerers_models.OffererStats.query.filter_by(offererId=offerer_id).all()


@dataclasses.dataclass
class OffererV2Stats:
    publishedPublicOffers: int
    publishedEducationalOffers: int
    pendingEducationalOffers: int
    pendingPublicOffers: int


def get_offerer_v2_stats(offerer_id: int) -> OffererV2Stats:
    offerer = offerers_repository.find_offerer_by_id(offerer_id)
    if not offerer:
        raise exceptions.CannotFindOffererForOfferId()
    return OffererV2Stats(
        publishedPublicOffers=offerers_repository.get_number_of_bookable_offers_for_offerer(offerer_id=offerer_id),
        publishedEducationalOffers=offerers_repository.get_number_of_bookable_collective_offers_for_offerer(
            offerer_id=offerer_id
        ),
        pendingPublicOffers=offerers_repository.get_number_of_pending_offers_for_offerer(offerer_id=offerer_id),
        pendingEducationalOffers=offerers_repository.get_number_of_pending_collective_offers_for_offerer(
            offerer_id=offerer_id
        ),
    )


def get_venues_by_ids(ids: typing.Collection[int]) -> BaseQuery:
    return offerers_models.Venue.query.filter(offerers_models.Venue.id.in_(ids)).options(
        sa.orm.joinedload(offerers_models.Venue.googlePlacesInfo)
    )


def add_timespan(opening_hours: models.OpeningHours, new_timespan: NumericRange) -> None:
    existing_timespan = opening_hours.timespan
    if existing_timespan:
        if len(existing_timespan) == 2:
            raise ValueError("Maximum size for opening hours reached")
        if existing_timespan[0].lower <= new_timespan.upper and existing_timespan[0].upper >= new_timespan.lower:
            raise ValueError("New opening hours overlaps existing one")
        existing_timespan.append(new_timespan)
        existing_timespan.sort()
    else:
        opening_hours.timespan = [new_timespan]
    db.session.commit()
