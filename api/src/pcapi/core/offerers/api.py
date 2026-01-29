import dataclasses
import decimal
import functools
import itertools
import logging
import re
import secrets
import time
import typing
from collections import defaultdict
from datetime import date
from datetime import datetime
from datetime import timedelta
from functools import partial
from math import ceil

import pytz
import schwifty
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects.postgresql import INTERVAL

import pcapi.connectors.acceslibre as accessibility_provider
import pcapi.connectors.thumb_storage as storage
import pcapi.core.educational.api.adage as adage_api
import pcapi.core.finance.models as finance_models
import pcapi.core.history.api as history_api
import pcapi.core.history.models as history_models
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.users.models as users_models
import pcapi.utils.date as date_utils
import pcapi.utils.db as db_utils
import pcapi.utils.email as email_utils
import pcapi.utils.string as string_utils
from pcapi import settings
from pcapi.connectors import api_adresse
from pcapi.connectors import virustotal
from pcapi.connectors.clickhouse import queries as clickhouse_queries
from pcapi.connectors.entreprise import api as api_entreprise
from pcapi.connectors.entreprise import exceptions as entreprise_exceptions
from pcapi.connectors.entreprise import models as sirene_models
from pcapi.core import search
from pcapi.core.bookings import api as bookings_api
from pcapi.core.bookings import constants as bookings_constants
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.categories import subcategories
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import booking as educational_booking_api
from pcapi.core.educational.api import dms as dms_api
from pcapi.core.external import zendesk_sell
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.geography import constants as geography_constants
from pcapi.core.geography import models as geography_models
from pcapi.core.geography import utils as geography_utils
from pcapi.core.offerers import constants as offerers_constants
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import utils as offerers_utils
from pcapi.core.opening_hours import api as opening_hours_api
from pcapi.core.opening_hours import schemas as opening_hours_schemas
from pcapi.core.search.models import IndexationReason
from pcapi.core.users import repository as users_repository
from pcapi.models import db
from pcapi.models import feature
from pcapi.models import offer_mixin
from pcapi.models import pc_object
from pcapi.models import validation_status_mixin
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.routes.serialization.offerers_serialize import OffererMemberStatus
from pcapi.utils import crypto
from pcapi.utils import human_ids
from pcapi.utils import image_conversion
from pcapi.utils import regions as utils_regions
from pcapi.utils import siren as siren_utils
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.repository import transaction
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import is_managed_transaction
from pcapi.utils.transaction_manager import mark_transaction_as_invalid
from pcapi.utils.transaction_manager import on_commit
from pcapi.workers.match_acceslibre_job import match_acceslibre_job

from . import exceptions
from . import models
from . import repository as offerers_repository
from . import schemas as offerers_schemas
from . import validation
from .tasks import CLOSED_OFFERER_TAG_NAME


logger = logging.getLogger(__name__)

# List of fields of `Venue` which, when changed, must trigger a
# reindexation of offers.
VENUE_ALGOLIA_INDEXED_FIELDS = ["name", "publicName", "postalCode", "city", "latitude", "longitude"]
API_KEY_SEPARATOR = "_"
APE_TAG_MAPPING = {"8411Z": "Collectivité"}
DMS_TOKEN_REGEX = r"^(?:PRO-)?([a-fA-F0-9]{12})$"


def link_cultural_domains_to_venue(
    cultural_domains: list[str] | None,
    venue: offerers_models.Venue | None,
    venue_type_code: str | None,
) -> None:
    if cultural_domains is None:
        return

    educational_domains = educational_repository.get_educational_domains_from_names(cultural_domains)
    missing_domains = set(cultural_domains) - {domain.name for domain in educational_domains}
    if missing_domains:
        raise exceptions.OffererException(
            {"culturalDomains": f"Unknown cultural domains: {', '.join(missing_domains)}"}
        )

    if venue:
        venue.collectiveDomains = educational_domains


def update_venue(
    venue: models.Venue,
    modifications: dict,
    location_modifications: dict,
    author: users_models.User,
    *,
    opening_hours: opening_hours_schemas.WeekdayOpeningHoursTimespans | None = None,
    contact_data: offerers_schemas.VenueContactModel | None = None,
    criteria: list[criteria_models.Criterion] | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    external_accessibility_url: str | None | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    cultural_domains: list[str] | None = None,
    is_manual_edition: bool = False,
) -> models.Venue:
    new_open_to_public = not venue.isOpenToPublic and modifications.get("isOpenToPublic")

    has_address_changed = (
        location_modifications.get("banId", offerers_constants.UNCHANGED) is not offerers_constants.UNCHANGED
        or location_modifications.get("postalCode", offerers_constants.UNCHANGED) is not offerers_constants.UNCHANGED
        or location_modifications.get("street", offerers_constants.UNCHANGED) is not offerers_constants.UNCHANGED
    )
    venue_snapshot = history_api.ObjectUpdateSnapshot(venue, author)
    if not venue.isVirtual:
        is_venue_location_updated = any(
            field in location_modifications
            for field in ("banId", "street", "city", "inseeCode", "postalCode", "latitude", "longitude")
        )

        if is_venue_location_updated:
            _update_venue_location(
                venue,
                location_modifications,
                venue_snapshot=venue_snapshot,
                is_manual_edition=is_manual_edition,
            )

    if contact_data:
        # target must not be None, otherwise contact_data fields will be compared to fields in Venue, which do not exist
        target = venue.contact if venue.contact is not None else offerers_models.VenueContact()
        venue_snapshot.trace_update(contact_data.dict(), target=target, field_name_template="contact.{}")
        upsert_venue_contact(venue, contact_data)

    if opening_hours:
        current = opening_hours_api.get_current_opening_hours(venue)
        updates = opening_hours_api.deprecated.get_venue_openings_hours_updates(opening_hours)
        changes = opening_hours_api.compute_upsert_changes(current, updates)

        opening_hours_api.deprecated.upsert_venue_opening_hours(venue, updates)

        raw_trace_data = {
            f"openingHours.{weekday.value}.timespan": {
                "old": date_utils.timespan_str_to_readable_str(change["old"]),
                "new": date_utils.timespan_str_to_readable_str(change["new"]),
            }
            for weekday, change in changes.items()
        }
        venue_snapshot.trace_update_raw(raw_trace_data)

    link_cultural_domains_to_venue(cultural_domains, venue, modifications.get("venueTypeCode"))

    if external_accessibility_url is not offerers_constants.UNCHANGED:
        external_accessibility_id = external_accessibility_url.split("/")[-2] if external_accessibility_url else None
        external_accessibility_infos = {
            "externalAccessibilityId": external_accessibility_id,
            "externalAccessibilityUrl": external_accessibility_url,
        }
        venue_snapshot.trace_update(
            external_accessibility_infos,
            target=venue.accessibilityProvider or offerers_models.AccessibilityProvider(),
            field_name_template="accessibilityProvider.{}",
        )
        if external_accessibility_id:
            set_accessibility_provider_id(venue, external_accessibility_id, external_accessibility_url)
            set_accessibility_infos_from_provider_id(venue)
        else:
            delete_venue_accessibility_provider(venue)

    if criteria is not offerers_constants.UNCHANGED:
        if set(venue.criteria) != set(criteria):
            modifications["criteria"] = criteria

    old_booking_email = venue.bookingEmail if modifications.get("bookingEmail") else None

    not_open_to_public_anymore = venue.isOpenToPublic and modifications.get("isOpenToPublic") is False

    if modifications:
        venue_snapshot.trace_update(modifications)
        if venue.is_soft_deleted():
            raise pc_object.DeletedRecordException()
        for key, value in modifications.items():
            if key == "venueTypeCode":
                value = models.VenueTypeCode[value]
            setattr(venue, key, value)
    elif venue_snapshot.is_empty:
        return venue
    venue_snapshot.add_action()

    if modifications.get("venueTypeCode", None) and not modifications.get("activity", None):
        venue.activity = offerers_utils.get_venue_activity_from_type_code(venue.isOpenToPublic, venue.venueTypeCode)
    if modifications.get("activity", None) and not modifications.get("venueTypeCode", None):
        assert venue.activity  # helps mypy, activity has been modified, is not null if we are here and set above
        venue.venueTypeCode = offerers_utils.get_venue_type_code_from_activity(venue.activity)

    db.session.add(venue)
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()

    if modifications or location_modifications:
        modifications_keys = set(modifications.keys()) | set(location_modifications.keys())

        on_commit(
            functools.partial(
                search.async_index_venue_ids,
                [venue.id],
                reason=IndexationReason.VENUE_UPDATE,
                log_extra={"changes": modifications_keys},
            )
        )

        indexing_modifications_fields = modifications_keys & set(VENUE_ALGOLIA_INDEXED_FIELDS)
        if indexing_modifications_fields:
            on_commit(
                functools.partial(
                    search.async_index_offers_of_venue_ids,
                    [venue.id],
                    reason=IndexationReason.VENUE_UPDATE,
                    log_extra={"changes": set(indexing_modifications_fields)},
                )
            )

        # Former booking email address shall no longer receive emails about data related to this venue.
        # If booking email was only in this object, this will clear all columns here and it will never be updated later.
        external_attributes_api.update_external_pro(old_booking_email)
        external_attributes_api.update_external_pro(venue.bookingEmail)

    zendesk_sell.update_venue(venue)

    if contact_data and contact_data.website:
        virustotal.request_url_scan(contact_data.website, skip_if_recent_scan=True)

    if new_open_to_public or (has_address_changed and venue.isOpenToPublic):
        on_commit(
            functools.partial(
                match_acceslibre_job.delay,
                venue.id,
            )
        )

    if not_open_to_public_anymore:
        delete_venue_accessibility_provider(venue)

    return venue


def _update_venue_location(
    venue: models.Venue,
    location_modifications: dict,
    venue_snapshot: history_api.ObjectUpdateSnapshot,
    is_manual_edition: bool = False,
) -> None:
    """
    Update the venue location and also populate the newly created Address & OffererAddress.
    You might want to skip the API Adresse call and force the location update with incoming data.
    If we receive untrusted user input, we want to double check data consistency using the API Adresse.
    On the other side, BO users might want to force a location to a venue, for example if the address is unknown
    for the API.
    """
    offerer_address = venue.offererAddress
    if not offerer_address:
        # In case of missing OA, backoffice user should be able to set an address
        offerer_address = offerers_models.OffererAddress(
            offererId=venue.managingOffererId,
            venueId=venue.id,
            type=offerers_models.LocationType.VENUE_LOCATION,
            address=geography_models.Address(),  # not saved, only used for comparison
            label=None,
        )

    # When street is cleared from the BO, location_modifications contains: {'street': None}
    street = location_modifications.get("street", offerer_address.address.street)
    city = location_modifications.get("city", offerer_address.address.city)
    insee_code = location_modifications.get("inseeCode", offerer_address.address.inseeCode)
    postal_code = location_modifications.get("postalCode", offerer_address.address.postalCode)
    latitude = location_modifications.get("latitude", offerer_address.address.latitude)
    longitude = location_modifications.get("longitude", offerer_address.address.longitude)
    ban_id = location_modifications.get("banId", offerer_address.address.banId)
    logger.info(
        "Updating venue location",
        extra={"venue_id": venue.id, "venue_street": street, "venue_city": city, "venue_postalCode": postal_code},
    )

    if is_manual_edition:
        ban_id = None
        try:
            insee_code = api_adresse.get_municipality_centroid(city=city, postcode=postal_code).citycode
        except api_adresse.NoResultException:
            insee_code = None
    location_data = LocationData(
        city=typing.cast(str, city),
        postal_code=typing.cast(str, postal_code),
        latitude=typing.cast(float, latitude),
        longitude=typing.cast(float, longitude),
        street=street,
        ban_id=ban_id,
        insee_code=insee_code,
    )

    address = get_or_create_address(location_data, is_manual_edition=is_manual_edition)
    snapshot_location_data = {
        "city": address.city,
        "postalCode": address.postalCode,
        "latitude": address.latitude,
        "longitude": address.longitude,
        "street": address.street,
        "inseeCode": address.inseeCode,
        "isManualEdition": is_manual_edition,
    }
    # Trace banId modification only if edition is not manual
    # In case of manual edition, banId is emptied with any action user
    # and we don’t that action to appears as user’s action
    if not is_manual_edition:
        snapshot_location_data["banId"] = address.banId

    venue_snapshot.trace_update(snapshot_location_data, offerer_address.address, "offererAddress.address.{}")

    assert offerer_address.type == offerers_models.LocationType.VENUE_LOCATION  # should never raise
    venue_snapshot.trace_update({"addressId": address.id}, offerer_address, "offererAddress.{}")
    offerer_address.address = address

    db.session.add(offerer_address)
    db.session.flush()


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

    db.session.add(venue)
    db.session.flush()

    zendesk_sell.update_venue(venue)

    return venue


def upsert_venue_contact(venue: models.Venue, contact_data: offerers_schemas.VenueContactModel) -> models.Venue:
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

    db.session.add(venue_contact)
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()
    return venue


def create_venue(
    venue_data: venues_serialize.PostVenueBodyModel,
    author: users_models.User,
    address: geography_models.Address | None = None,
) -> models.Venue:
    # Call generate_dms_token() before objects creation to avoid autoflush which would trigger
    # _fill_departement_code_and_timezone and check constraints.
    dms_token = generate_dms_token()

    venue = models.Venue()
    venue_address = offerers_schemas.LocationModel(**venue_data.address.dict())

    if not address:
        address = create_offerer_address_from_address_api(venue_address)

    offerer_address = offerers_models.OffererAddress(
        offererId=venue_data.managingOffererId,
        addressId=address.id,
        type=offerers_models.LocationType.VENUE_LOCATION,
        label=venue_address.label or None,
    )
    db.session.add(offerer_address)
    db.session.flush()

    offerer_address.venue = venue

    data = venue_data.dict(by_alias=True)
    data["dmsToken"] = dms_token
    if not data["publicName"]:
        data["publicName"] = data["name"]
    if venue.is_soft_deleted():
        raise pc_object.DeletedRecordException()
    for key, value in data.items():
        if key in ("contact", "culturalDomains"):
            continue
        setattr(venue, key, value)

    if venue_data.contact:
        upsert_venue_contact(venue, venue_data.contact)

    if settings.IS_INTEGRATION:
        # Always enable collective features for new venues in integration
        # Update managing offerer now and not when it is created to avoid
        # some environment specific code spread here and there.
        offerer = db.session.get(offerers_models.Offerer, venue.managingOffererId)
        if offerer:
            # if no offerer is found, venue won't be saved because of invalid
            # foreign key id. No need to handle this here, let it fail later.
            offerer.allowedOnAdage = True
        venue.adageId = str(int(time.time()))
        venue.adageInscriptionDate = date_utils.get_naive_utc_now()

    assert data.get("venueTypeCode") or data.get("activity") or data.get("culturalDomains")
    if not data.get("activity") and data.get("venueTypeCode"):
        venue.activity = offerers_utils.get_venue_activity_from_type_code(
            data.get("isOpenToPublic"), data.get("venueTypeCode")
        )
    if not data.get("venueTypeCode") and data.get("activity"):
        venue.venueTypeCode = offerers_utils.get_venue_type_code_from_activity(data["activity"])

    db.session.add(venue)
    history_api.add_action(history_models.ActionType.VENUE_CREATED, author=author, venue=venue)

    db.session.flush()

    # Deal with cultural domains
    link_cultural_domains_to_venue(venue_data.culturalDomains, venue, venue_data.venueTypeCode)

    if venue.siret:
        link_venue_to_pricing_point(venue, pricing_point_id=venue.id)

    venue.isPermanent = True

    on_commit(functools.partial(search.async_index_venue_ids, [venue.id], reason=IndexationReason.VENUE_CREATION))
    external_attributes_api.update_external_pro(venue.bookingEmail)
    zendesk_sell.create_venue(venue)

    return venue


def delete_venue(venue_id: int, allow_delete_last_venue: bool = False) -> None:
    venue_has_bookings = db.session.query(
        db.session.query(bookings_models.Booking).filter(bookings_models.Booking.venueId == venue_id).exists()
    ).scalar()
    venue_has_collective_bookings = db.session.query(
        db.session.query(educational_models.CollectiveBooking)
        .filter(educational_models.CollectiveBooking.venueId == venue_id)
        .exists()
    ).scalar()

    if venue_has_bookings or venue_has_collective_bookings:
        raise exceptions.CannotDeleteVenueWithBookingsException()

    venue_used_as_pricing_point = db.session.query(
        db.session.query(offerers_models.VenuePricingPointLink)
        .filter(
            offerers_models.VenuePricingPointLink.venueId != venue_id,
            offerers_models.VenuePricingPointLink.pricingPointId == venue_id,
        )
        .exists()
    ).scalar()

    if venue_used_as_pricing_point:
        # Additional checks to allow removing a venue which is only a former pricing point for other venues but has
        # never been used for pricing, so that support team can handle misconfiguration by an offerer.
        venue_used_as_current_pricing_point = db.session.query(
            db.session.query(offerers_models.VenuePricingPointLink)
            .filter(
                offerers_models.VenuePricingPointLink.venueId != venue_id,
                offerers_models.VenuePricingPointLink.pricingPointId == venue_id,
                offerers_models.VenuePricingPointLink.timespan.contains(date_utils.get_naive_utc_now()),
            )
            .exists()
        ).scalar()

        if venue_used_as_current_pricing_point:
            raise exceptions.CannotDeleteVenueUsedAsPricingPointException()

        pricing_point_has_pricings = db.session.query(
            db.session.query(finance_models.Pricing).filter(finance_models.Pricing.pricingPointId == venue_id).exists()
        ).scalar()

        if pricing_point_has_pricings:
            raise exceptions.CannotDeleteVenueUsedAsPricingPointException()

        db.session.query(offerers_models.VenuePricingPointLink).filter(
            offerers_models.VenuePricingPointLink.venueId != venue_id,
            offerers_models.VenuePricingPointLink.pricingPointId == venue_id,
        ).delete(synchronize_session=False)

    # Because of regularization, FinanceEvent may still be linked to the venue even if the Booking has moved
    venue_linked_to_finance_event = db.session.query(
        db.session.query(finance_models.FinanceEvent)
        .filter(
            sa.or_(
                finance_models.FinanceEvent.venueId == venue_id,
                finance_models.FinanceEvent.pricingPointId == venue_id,
            )
        )
        .exists()
    ).scalar()
    if venue_linked_to_finance_event:
        raise exceptions.CannotDeleteVenueLinkedToFinanceEventException()

    venue_associated_with_reimbursement_rule = db.session.query(
        db.session.query(finance_models.CustomReimbursementRule)
        .filter(finance_models.CustomReimbursementRule.venueId == venue_id)
        .exists()
    ).scalar()
    if venue_associated_with_reimbursement_rule:
        raise exceptions.CannotDeleteVenueWithActiveOrFutureCustomReimbursementRule()

    if not allow_delete_last_venue:
        aliased_venue = sa_orm.aliased(offerers_models.Venue)
        offerer_has_other_venue = db.session.query(
            db.session.query(offerers_models.Venue)
            .join(aliased_venue, aliased_venue.managingOffererId == offerers_models.Venue.managingOffererId)
            .filter(
                aliased_venue.id == venue_id,
                offerers_models.Venue.id != venue_id,
                offerers_models.Venue.isSoftDeleted.is_not(True),
            )
            .exists()
        ).scalar()
        if not offerer_has_other_venue:
            raise exceptions.CannotDeleteLastVenue()

    offer_ids_to_delete = _delete_objects_linked_to_venue(venue_id)

    pivot = (
        db.session.query(providers_models.CinemaProviderPivot)
        .filter(providers_models.CinemaProviderPivot.venueId == venue_id)
        .one_or_none()
    )
    if pivot:
        if pivot.CDSCinemaDetails:
            db.session.query(providers_models.CDSCinemaDetails).filter(
                providers_models.CDSCinemaDetails.cinemaProviderPivotId == pivot.id
            ).delete(synchronize_session=False)
        if pivot.BoostCinemaDetails:
            db.session.query(providers_models.BoostCinemaDetails).filter(
                providers_models.BoostCinemaDetails.cinemaProviderPivotId == pivot.id
            ).delete(synchronize_session=False)
        if pivot.CGRCinemaDetails:
            db.session.query(providers_models.CGRCinemaDetails).filter(
                providers_models.CGRCinemaDetails.cinemaProviderPivotId == pivot.id
            ).delete(synchronize_session=False)
        if pivot.EMSCinemaDetails:
            db.session.query(providers_models.EMSCinemaDetails).filter(
                providers_models.EMSCinemaDetails.cinemaProviderPivotId == pivot.id
            ).delete(synchronize_session=False)
        db.session.query(providers_models.CinemaProviderPivot).filter(
            providers_models.CinemaProviderPivot.venueId == venue_id
        ).delete(synchronize_session=False)

    db.session.query(providers_models.AllocinePivot).filter(
        providers_models.CinemaProviderPivot.venueId == venue_id
    ).delete(synchronize_session=False)

    # Warning: we should only delete rows where the "venueId" is the
    # venue to delete. We should NOT delete rows where the
    # "pricingPointId" or the "reimbursementId" is the venue to
    # delete. If other venues still have the "venue to delete" as
    # their pricing/reimbursement point, the database will rightfully
    # raise an error. Either these venues should be deleted first, or
    # the "venue to delete" should not be deleted.
    db.session.query(offerers_models.VenuePricingPointLink).filter_by(
        venueId=venue_id,
    ).delete(synchronize_session=False)

    db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == venue_id).delete(
        synchronize_session=False
    )

    db.session.flush()

    on_commit(
        functools.partial(
            search.unindex_offer_ids,
            offer_ids_to_delete["individual_offer_ids_to_delete"],
        ),
    )
    on_commit(
        functools.partial(
            search.unindex_collective_offer_template_ids,
            offer_ids_to_delete["collective_offer_template_ids_to_delete"],
        ),
    )
    on_commit(
        functools.partial(
            search.unindex_venue_ids,
            [venue_id],
        ),
    )


def _delete_objects_linked_to_venue(venue_id: int) -> dict:
    STEP = 200

    offer_ids_to_delete: dict[str, list[int]] = {
        "individual_offer_ids_to_delete": [],
        "collective_offer_ids_to_delete": [],
        "collective_offer_template_ids_to_delete": [],
    }
    # delete offers and their dependencies
    packed_offers_id = db.session.query(offers_models.Offer.id).filter(offers_models.Offer.venueId == venue_id).all()
    offers_id = [i for (i,) in packed_offers_id]  # an iterable are not enough here we really need a list in memory
    offer_index = 0
    while offers_id_chunk := offers_id[offer_index : offer_index + STEP]:
        offer_index += STEP
        offer_ids_to_delete["individual_offer_ids_to_delete"].extend(offers_id_chunk)

        packed_stocks_id = (
            db.session.query(offers_models.Stock.id).filter(offers_models.Stock.offerId.in_(offers_id_chunk)).all()
        )
        stocks_id = [i for (i,) in packed_stocks_id]  # an iterable are not enough here we really need a list in memory
        stock_index = 0
        while stocks_id_chunk := stocks_id[stock_index : stock_index + STEP]:
            stock_index += STEP

            db.session.query(offers_models.ActivationCode).filter(
                offers_models.ActivationCode.stockId.in_(stocks_id_chunk),
                # All bookingId should be None if venue_has_bookings is False, keep condition to get an exception otherwise
                offers_models.ActivationCode.bookingId.is_(None),
            ).delete(synchronize_session=False)

        db.session.query(offers_models.Stock).filter(offers_models.Stock.offerId.in_(offers_id_chunk)).delete(
            synchronize_session=False
        )
        db.session.query(users_models.Favorite).filter(users_models.Favorite.offerId.in_(offers_id_chunk)).delete(
            synchronize_session=False
        )
        db.session.query(criteria_models.OfferCriterion).filter(
            criteria_models.OfferCriterion.offerId.in_(offers_id_chunk)
        ).delete(synchronize_session=False)
        db.session.query(offers_models.Mediation).filter(offers_models.Mediation.offerId.in_(offers_id_chunk)).delete(
            synchronize_session=False
        )
        db.session.query(offers_models.OfferReport).filter(
            offers_models.OfferReport.offerId.in_(offers_id_chunk)
        ).delete(synchronize_session=False)
    db.session.query(offers_models.Offer).filter(offers_models.Offer.venueId == venue_id).delete(
        synchronize_session=False
    )

    # delete all things providers related
    db.session.query(providers_models.AllocineVenueProvider).filter(
        providers_models.AllocineVenueProvider.id == providers_models.VenueProvider.id,
        providers_models.VenueProvider.venueId == venue_id,
        offerers_models.Venue.id == venue_id,
    ).delete(synchronize_session=False)
    db.session.query(providers_models.VenueProvider).filter(providers_models.VenueProvider.venueId == venue_id).delete(
        synchronize_session=False
    )
    db.session.query(providers_models.AllocinePivot).filter_by(venueId=venue_id).delete(synchronize_session=False)

    # delete collective offers and templates and their dependencies:
    packed_collective_offers_id = db.session.query(educational_models.CollectiveOffer.id).filter(
        educational_models.CollectiveOffer.venueId == venue_id
    )
    collective_offers_id = [i for (i,) in packed_collective_offers_id]
    collective_offer_index = 0
    while collective_offers_id_chunk := collective_offers_id[collective_offer_index : collective_offer_index + STEP]:
        collective_offer_index += STEP
        offer_ids_to_delete["collective_offer_ids_to_delete"].extend(collective_offers_id_chunk)
        db.session.query(educational_models.CollectiveStock).filter(
            educational_models.CollectiveStock.collectiveOfferId.in_(collective_offers_id_chunk)
        ).delete(synchronize_session=False)

    db.session.query(educational_models.CollectiveOffer).filter(
        educational_models.CollectiveOffer.venueId == venue_id
    ).delete(synchronize_session=False)

    packed_collective_offer_templates_id = db.session.query(educational_models.CollectiveOfferTemplate.id).filter(
        educational_models.CollectiveOfferTemplate.venueId == venue_id
    )
    collective_offer_templates_id = [i for (i,) in packed_collective_offer_templates_id]
    collective_offer_template_index = 0
    while collective_offer_templates_id_chunk := collective_offer_templates_id[
        collective_offer_template_index : collective_offer_template_index + STEP
    ]:
        collective_offer_template_index += STEP
        offer_ids_to_delete["collective_offer_template_ids_to_delete"].extend(collective_offer_templates_id_chunk)
        db.session.query(educational_models.CollectiveOffer).filter(
            educational_models.CollectiveOffer.templateId.in_(collective_offer_templates_id_chunk)
        ).update({"templateId": None}, synchronize_session=False)
        db.session.query(educational_models.CollectiveOfferTemplateEducationalRedactor).filter(
            educational_models.CollectiveOfferTemplateEducationalRedactor.collectiveOfferTemplateId.in_(
                collective_offer_templates_id_chunk
            )
        ).delete(synchronize_session=False)
        db.session.query(educational_models.CollectiveOfferRequest).filter(
            educational_models.CollectiveOfferRequest.collectiveOfferTemplateId.in_(collective_offer_templates_id_chunk)
        ).delete(synchronize_session=False)

    db.session.query(educational_models.CollectivePlaylist).filter(
        sa.or_(
            educational_models.CollectivePlaylist.venueId == venue_id,
            educational_models.CollectivePlaylist.collectiveOfferTemplateId.in_(
                db.session.query(educational_models.CollectiveOfferTemplate.id).filter(
                    educational_models.CollectiveOfferTemplate.venueId == venue_id
                )
            ),
        )
    ).delete(synchronize_session=False)
    db.session.query(educational_models.CollectiveOfferTemplate).filter(
        educational_models.CollectiveOfferTemplate.venueId == venue_id
    ).delete(synchronize_session=False)

    return offer_ids_to_delete


def link_venue_to_pricing_point(
    venue: models.Venue,
    pricing_point_id: int,
    timestamp: datetime | None = None,
    force_link: bool = False,
) -> None:
    """
    Creates a VenuePricingPointLink if the venue had not been previously linked to a pricing point.
    If it had, then it will raise an error, unless the force_link parameter is True, in exceptional circumstances.
    """
    validation.check_venue_can_be_linked_to_pricing_point(venue, pricing_point_id)
    collective_stock_datetime = educational_models.CollectiveStock.endDatetime.name
    if not timestamp:
        timestamp = date_utils.get_naive_utc_now()
    current_link = (
        db.session.query(models.VenuePricingPointLink)
        .filter(
            models.VenuePricingPointLink.venueId == venue.id,
            models.VenuePricingPointLink.timespan.contains(timestamp),
        )
        .one_or_none()
    )
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
    for from_tables, where_clauses, stock_datetime in (
        (
            "booking, stock",
            'finance_event."bookingId" is not null '
            'and booking.id = finance_event."bookingId" '
            'and stock.id = booking."stockId"',
            "beginningDatetime",
        ),
        (
            # use aliases to have the same `set` clause
            "collective_booking as booking, collective_stock as stock",
            'finance_event."collectiveBookingId" is not null '
            'and booking.id = finance_event."collectiveBookingId" '
            'and stock.id = booking."collectiveStockId"',
            collective_stock_datetime,
        ),
    ):
        ppoint_update_result = db.session.execute(
            sa.text(
                f"""
              update finance_event
              set
                "pricingPointId" = :pricing_point_id,
                status = :finance_event_status_ready,
                "pricingOrderingDate" = greatest(
                  booking."dateUsed",
                  stock."{stock_datetime}",
                  :new_link_start
                )
              from {from_tables}
              where
                {where_clauses}
                and finance_event.status = :finance_event_status_pending
                and finance_event."pricingPointId" IS NULL
                and finance_event."venueId" = :venue_id
            """
            ),
            {
                "venue_id": venue.id,
                "pricing_point_id": pricing_point_id,
                "finance_event_status_pending": finance_models.FinanceEventStatus.PENDING.value,
                "finance_event_status_ready": finance_models.FinanceEventStatus.READY.value,
                "new_link_start": timestamp,
            },
        )
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()

    logger.info(
        "Linked venue to pricing point",
        extra={
            "venue": venue.id,
            "new_pricing_point": pricing_point_id,
            "previous_pricing_point": current_link.pricingPointId if current_link else None,
            "updated_finance_events": typing.cast(sa.engine.cursor.CursorResult, ppoint_update_result).rowcount,
        },
    )


def generate_provider_api_key(provider: providers_models.Provider) -> tuple[models.ApiKey, str]:
    offerer = provider.offererProvider.offerer if provider.offererProvider else None
    if offerer is None:
        raise exceptions.CannotFindProviderOfferer()

    clear_secret = secrets.token_hex(32)
    prefix = _generate_api_key_prefix()
    key = models.ApiKey(provider=provider, prefix=prefix, secret=crypto.hash_public_api_key(clear_secret))

    return key, f"{prefix}{API_KEY_SEPARATOR}{clear_secret}"


def _generate_api_key_prefix() -> str:
    for _ in range(100):
        prefix_identifier = secrets.token_hex(6)
        prefix = _create_prefix(settings.ENV, prefix_identifier)
        if not db.session.query(db.session.query(models.ApiKey).filter_by(prefix=prefix).exists()).scalar():
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
        db.session.query(models.ApiKey)
        .filter_by(prefix=prefix)
        .options(sa_orm.joinedload(models.ApiKey.provider))
        .one_or_none()
    )

    if not api_key:
        return None

    return api_key if api_key.check_secret(clear_secret) else None


def _create_prefix(env: str, prefix_identifier: str) -> str:
    return f"{env}{API_KEY_SEPARATOR}{prefix_identifier}"


def _initialize_offerer(offerer: offerers_models.Offerer) -> None:
    if settings.IS_INTEGRATION:
        offerer.validationStatus = ValidationStatus.VALIDATED
    else:
        offerer.validationStatus = ValidationStatus.NEW
    offerer.isActive = True
    offerer.dateCreated = date_utils.get_naive_utc_now()


def auto_tag_new_offerer(
    offerer: offerers_models.Offerer,
    siren_info: sirene_models.SirenInfo | sirene_models.SiretInfo | None,
    user: users_models.User,
) -> None:
    tag_names_to_apply = set()

    if siren_info:
        if siren_info.ape_code:
            tag_label = APE_TAG_MAPPING.get(siren_info.ape_code)
            if tag_label:
                tag = db.session.query(offerers_models.OffererTag).filter_by(label=tag_label).one_or_none()
                if not tag:
                    logger.error(
                        "Could not assign tag to offerer: tag not found in DB",
                        extra={"offerer": offerer.id, "tag_label": tag_label},
                    )
                else:
                    offerer.tags.append(tag)

    if user.email.split("@")[-1] in set(settings.NATIONAL_PARTNERS_EMAIL_DOMAINS.split(",")):
        tag_names_to_apply.add("partenaire-national")

    if tag_names_to_apply:
        tags = (
            db.session.query(offerers_models.OffererTag)
            .filter(offerers_models.OffererTag.name.in_(tag_names_to_apply))
            .all()
        )
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
    activity: models.Activity | None
    target: models.Target
    venueTypeCode: str | None
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
    insee_data: sirene_models.SirenInfo | sirene_models.SiretInfo | None = None,
    **kwargs: typing.Any,
) -> models.UserOfferer:
    offerer = offerers_repository.find_offerer_by_siren(offerer_informations.siren)
    if not insee_data:
        insee_data = api_entreprise.get_siren_open_data(offerer_informations.siren)
    is_new = False

    if author is None:
        author = user

    if offerer is not None:
        # The user can have his attachment rejected or deleted to the offerer,
        # in this case it is passed to NEW if the offerer is not rejected
        user_offerer = (
            db.session.query(offerers_models.UserOfferer).filter_by(userId=user.id, offererId=offerer.id).one_or_none()
        )
        if not user_offerer:
            user_offerer = models.UserOfferer(offerer=offerer, user=user, validationStatus=ValidationStatus.NEW)
            db.session.add(user_offerer)
            db.session.flush()

        if offerer.isRejected:
            # When offerer was rejected, it is considered as a new offerer in validation process;
            # history is kept with same id and siren
            is_new = True
            update_offerer(offerer, author, name=offerer_informations.name)
            _initialize_offerer(offerer)
            comment = (comment + "\n" if comment else "") + "Nouvelle demande sur un SIREN précédemment rejeté"
            user_offerer.validationStatus = ValidationStatus.VALIDATED
            # Delete venues of rejected offerer so that a new one is created from onboarding data.
            # Rejected venue should not have any booking, pricing, reimbursement rule, so it should not raise exception.
            # Pricing point must be deleted AFTER venues without SIRET which reference them.
            venues_to_delete = (
                db.session.query(models.Venue)
                .filter(models.Venue.managingOffererId == offerer.id)
                .order_by(models.Venue.siret.nulls_first())
                .with_entities(models.Venue.id)
            )
            for venue_to_delete in venues_to_delete:
                delete_venue(venue_to_delete.id, allow_delete_last_venue=True)
        elif not user_offerer.isValidated:
            user_offerer.validationStatus = ValidationStatus.NEW
            user_offerer.dateCreated = date_utils.get_naive_utc_now()
            extra_data: dict[str, typing.Any] = {}
            _add_new_onboarding_info_to_extra_data(new_onboarding_info, extra_data)
            history_api.add_action(
                history_models.ActionType.USER_OFFERER_NEW,
                author=author,
                user=user,
                offerer=offerer,
                comment=comment,
                **extra_data,
            )
    else:
        is_new = True
        offerer = models.Offerer()
        offerer.name = offerer_informations.name
        offerer.siren = offerer_informations.siren
        _initialize_offerer(offerer)
        user_offerer = grant_user_offerer_access(offerer, user)
        db.session.add_all([offerer, user_offerer])
        db.session.flush()

    if is_new:
        try:
            insee_data = api_entreprise.get_siren_open_data(offerer.siren)
        except entreprise_exceptions.EntrepriseException as exc:
            logger.info("Could not fetch info from Entreprise API", extra={"exc": exc})

        auto_tag_new_offerer(offerer, insee_data, user)

        extra_data = {}
        _add_new_onboarding_info_to_extra_data(new_onboarding_info, extra_data)
        extra_data.update(kwargs)

        history_api.add_action(
            history_models.ActionType.OFFERER_NEW,
            author=author,
            user=user,
            offerer=offerer,
            comment=comment,
            **extra_data,
        )

    db.session.add(offerer)
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()

    if offerer_informations.phoneNumber:
        users_repository.fill_phone_number_on_all_users_offerer_without_any(
            offerer.id, offerer_informations.phoneNumber
        )

    external_attributes_api.update_external_pro(user.email)
    zendesk_sell.create_offerer(offerer)

    return user_offerer


def grant_user_offerer_access(offerer: models.Offerer, user: users_models.User) -> models.UserOfferer:
    user_offerer = models.UserOfferer(offerer=offerer, user=user, validationStatus=ValidationStatus.VALIDATED)
    db.session.add(user_offerer)
    db.session.flush()
    return user_offerer


def is_user_offerer_already_exist(user: users_models.User, siren: str) -> bool:
    return db.session.query(
        db.session.query(models.UserOfferer)
        .join(models.UserOfferer.offerer)
        .filter(
            models.UserOfferer.userId == user.id,
            models.Offerer.siren == siren,
            models.UserOfferer.validationStatus.not_in((ValidationStatus.REJECTED, ValidationStatus.DELETED)),
        )
        .exists()
    ).scalar()


def _format_tags(tags: typing.Iterable[models.OffererTag]) -> str:
    return ", ".join(sorted(tag.label for tag in tags if tag.label))


def update_offerer(
    offerer: models.Offerer,
    author: users_models.User,
    *,
    name: str | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    tags: list[models.OffererTag] | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
) -> None:
    modified_info: dict[str, dict[str, str | None]] = {}

    if name is not offerers_constants.UNCHANGED and offerer.name != name:
        modified_info["name"] = {"old_info": offerer.name, "new_info": name}
        offerer.name = name
    if tags is not offerers_constants.UNCHANGED:
        if set(offerer.tags) != set(tags):
            modified_info["tags"] = {
                "old_info": _format_tags(offerer.tags) or None,
                "new_info": _format_tags(tags) or None,
            }
            offerer.tags = tags

    if modified_info:
        history_api.add_action(
            history_models.ActionType.INFO_MODIFIED, author=author, offerer=offerer, modified_info=modified_info
        )

    db.session.add(offerer)
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()

    _update_external_offerer(offerer)


def remove_pro_role_and_add_non_attached_pro_role(users: list[users_models.User]) -> None:
    users_with_offerers = (
        db.session.query(users_models.User)
        .filter(users_models.User.id.in_([user.id for user in users]))
        .options(
            sa_orm.load_only(users_models.User.roles),
            sa_orm.joinedload(users_models.User.UserOfferers)
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

    db.session.flush()

    external_attributes_api.update_external_pro(user_offerer.user.email)

    transactional_mails.send_offerer_attachment_validation_email_to_pro(user_offerer)

    offerer_invitation = (
        db.session.query(models.OffererInvitation)
        .filter_by(offererId=user_offerer.offererId)
        .filter_by(email=user_offerer.user.email)
        .one_or_none()
    )
    if offerer_invitation:
        transactional_mails.send_offerer_attachment_invitation_accepted(
            user_offerer.user,
            offerer_invitation.user.email,
        )


def set_offerer_attachment_pending(
    user_offerer: offerers_models.UserOfferer, author_user: users_models.User, comment: str | None = None
) -> None:
    user_offerer.validationStatus = ValidationStatus.PENDING
    remove_pro_role_and_add_non_attached_pro_role([user_offerer.user])
    db.session.add(user_offerer)
    history_api.add_action(
        history_models.ActionType.USER_OFFERER_PENDING,
        author=author_user,
        user=user_offerer.user,
        offerer=user_offerer.offerer,
        comment=comment,
    )
    db.session.flush()


def reject_offerer_attachment(
    user_offerer: offerers_models.UserOfferer,
    author_user: users_models.User | None,
    comment: str | None = None,
    send_email: bool = True,
) -> None:
    user_offerer.validationStatus = ValidationStatus.REJECTED
    db.session.add(user_offerer)

    history_api.add_action(
        history_models.ActionType.USER_OFFERER_REJECTED,
        author=author_user,
        user=user_offerer.user,
        offerer=user_offerer.offerer,
        comment=comment,
    )

    if send_email:
        transactional_mails.send_offerer_attachment_rejection_email_to_pro(user_offerer)

    remove_pro_role_and_add_non_attached_pro_role([user_offerer.user])
    db.session.flush()


def delete_offerer_attachment(
    user_offerer: offerers_models.UserOfferer,
    author_user: users_models.User | None,
    comment: str | None = None,
) -> None:
    user_offerer.validationStatus = ValidationStatus.DELETED
    db.session.add(user_offerer)

    history_api.add_action(
        history_models.ActionType.USER_OFFERER_DELETED,
        author=author_user,
        user=user_offerer.user,
        offerer=user_offerer.offerer,
        comment=comment,
    )

    remove_pro_role_and_add_non_attached_pro_role([user_offerer.user])
    db.session.flush()


def validate_offerer(
    offerer: models.Offerer, author_user: users_models.User, review_all_offers: bool = False, **action_args: typing.Any
) -> None:
    if offerer.isValidated:
        raise exceptions.OffererAlreadyValidatedException()

    applicants = users_repository.get_users_with_validated_attachment_by_offerer(offerer)
    offerer.validationStatus = ValidationStatus.VALIDATED
    offerer.dateValidated = date_utils.get_naive_utc_now()
    offerer.isActive = True
    db.session.add(offerer)

    for applicant in applicants:
        applicant.add_pro_role()
    db.session.add_all(applicants)

    if review_all_offers:
        action_args |= _internal_update_fraud_info(
            offerer=offerer, confidence_level=offerers_models.OffererConfidenceLevel.MANUAL_REVIEW
        )

        # Offers created before validation should be reviewed
        db.session.query(offers_models.Offer).filter(
            offerers_models.Venue.managingOffererId == offerer.id,
            offers_models.Offer.venueId.in_(
                db.session.query(offerers_models.Venue)
                .filter_by(managingOffererId=offerer.id)
                .with_entities(offerers_models.Venue.id)
            ),
            offers_models.Offer.lastValidationType == offer_mixin.OfferValidationType.AUTO,
            offers_models.Offer.validation == offer_mixin.OfferValidationStatus.APPROVED,
        ).update(
            {
                "validation": offer_mixin.OfferValidationStatus.PENDING,
                "lastValidationType": None,
                "lastValidationDate": None,
                "lastValidationPrice": None,
            },
            synchronize_session=False,
        )

    history_api.add_action(
        history_models.ActionType.OFFERER_VALIDATED,
        author=author_user,
        offerer=offerer,
        user=applicants[0] if applicants else None,  # before validation we should have only one applicant
        **action_args,
    )

    db.session.flush()

    _update_external_offerer(offerer, index_with_reason=IndexationReason.OFFERER_VALIDATION)

    if applicants:
        transactional_mails.send_new_offerer_validation_email_to_pro(offerer)
    for managed_venue in offerer.managedVenues:
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
        author=author_user,
        offerer=offerer,
        user=first_user_to_register_offerer,
        **action_args,
    )

    if applicants:
        transactional_mails.send_new_offerer_rejection_email_to_pro(
            offerer,
            action_args.get("rejection_reason"),
        )

    users_offerer = db.session.query(offerers_models.UserOfferer).filter_by(offererId=offerer.id).all()
    for user_offerer in users_offerer:
        reject_offerer_attachment(
            user_offerer,
            author_user,
            "Compte pro rejeté suite au rejet de l'entité juridique",
            send_email=(user_offerer.user not in applicants),  # do not send a second email
        )

    remove_pro_role_and_add_non_attached_pro_role(applicants)

    db.session.flush()

    if was_validated:
        _update_external_offerer(offerer, index_with_reason=IndexationReason.OFFERER_DEACTIVATION)


# We do not want to cancel bookings on events which took place on the last 3 days, because they automatically become
# USED after AUTO_USE_AFTER_EVENT_TIME_DELAY (+ one day margin because marking as used is a daily cron).
USED_EVENT_DELAY = bookings_constants.AUTO_USE_AFTER_EVENT_TIME_DELAY + timedelta(days=1)


def close_offerer(
    offerer: offerers_models.Offerer,
    *,
    is_manual: bool = False,
    closure_date: date | None = None,
    author_user: users_models.User | None = None,
    **action_args: typing.Any,
) -> None:
    if offerer.isClosed:
        raise exceptions.OffererAlreadyClosedException()

    if closure_date is not None and closure_date > date.today():
        # Future closure currently not supported because transactional email tells "cessé depuis le XXX à l'INSEE"
        raise exceptions.FutureClosureDate()

    was_validated = offerer.isValidated
    offerer.validationStatus = ValidationStatus.CLOSED
    db.session.add(offerer)
    history_api.add_action(
        history_models.ActionType.OFFERER_CLOSED,
        author=author_user,
        offerer=offerer,
        closure_date=closure_date.isoformat() if closure_date else None,  # may be used to check programmatically
        **action_args,
    )

    applicants = users_repository.get_users_with_validated_attachment(offerer)
    remove_pro_role_and_add_non_attached_pro_role(applicants)

    if applicants:
        transactional_mails.send_offerer_closed_email_to_pro(offerer, is_manual, closure_date)

    db.session.flush()

    author_id = author_user.id if author_user else None

    _cancel_individual_bookings_on_offerer_closure(offerer.id, author_id)
    _cancel_collective_bookings_on_offerer_closure(offerer.id, author_id)

    if was_validated:
        _update_external_offerer(offerer, index_with_reason=IndexationReason.OFFERER_DEACTIVATION)


def auto_delete_attachments_on_closed_offerers() -> None:
    last_closed_date_subquery = (
        db.session.query(history_models.ActionHistory.actionDate)
        .filter(
            history_models.ActionHistory.offererId == offerers_models.Offerer.id,
            history_models.ActionHistory.actionType == history_models.ActionType.OFFERER_CLOSED,
        )
        .order_by(history_models.ActionHistory.actionDate.desc())
        .limit(1)
        .correlate(offerers_models.Offerer)
        .scalar_subquery()
    )

    rows = (
        db.session.query(
            offerers_models.UserOfferer,
            last_closed_date_subquery.label("offererClosedDate"),
        )
        .join(offerers_models.UserOfferer.offerer)
        .filter(
            offerers_models.Offerer.isClosed,
            offerers_models.UserOfferer.validationStatus.in_(
                [ValidationStatus.NEW, ValidationStatus.PENDING, ValidationStatus.VALIDATED]
            ),
        )
        .all()
    )

    for row in rows:
        if row.offererClosedDate <= date_utils.get_naive_utc_now() - timedelta(
            days=settings.CLOSED_OFFERER_PRO_USER_DELETION_DELAY
        ):
            user_offerer = row.UserOfferer
            comment = (
                f"Délai de {settings.CLOSED_OFFERER_PRO_USER_DELETION_DELAY} jours expiré "
                f"après fermeture de l'entité juridique sur la plateforme le {row.offererClosedDate.strftime('%d/%m/%Y')}"
            )
            if user_offerer.isWaitingForValidation:
                reject_offerer_attachment(user_offerer, author_user=None, comment=comment, send_email=False)
            else:
                delete_offerer_attachment(user_offerer, author_user=None, comment=comment)


def get_individual_bookings_to_cancel_on_offerer_closure(offerer_id: int) -> list[bookings_models.Booking]:
    now = date_utils.get_naive_utc_now()
    event_subcategory_ids = subcategories.EVENT_SUBCATEGORIES.keys()

    ongoing_bookings = (
        db.session.query(bookings_models.Booking)
        .filter(
            bookings_models.Booking.offererId == offerer_id,
            bookings_models.Booking.status == bookings_models.BookingStatus.CONFIRMED,
        )
        .options(
            sa_orm.joinedload(bookings_models.Booking.stock)
            .load_only(offers_models.Stock.beginningDatetime)
            .joinedload(offers_models.Stock.offer)
            .load_only(offers_models.Offer.subcategoryId)
        )
        .all()
    )

    # Do not cancel bookings which will become USED in auto_mark_as_used_after_event()
    bookings = []
    for booking in ongoing_bookings:
        if booking.stock.offer.subcategoryId in event_subcategory_ids:
            if booking.stock.beginningDatetime and (now - USED_EVENT_DELAY) <= booking.stock.beginningDatetime <= now:
                continue

        bookings.append(booking)
    return bookings


def _cancel_individual_bookings_on_offerer_closure(offerer_id: int, author_id: int | None) -> None:
    bookings = get_individual_bookings_to_cancel_on_offerer_closure(offerer_id)

    for booking in bookings:
        with atomic():
            try:
                bookings_api.cancel_booking_on_closed_offerer(booking, author_id=author_id)
            except Exception as exc:
                mark_transaction_as_invalid()
                logger.exception(
                    "Failed to cancel booking when closing offerer",
                    extra={"exc": exc, "booking_id": booking.id, "offerer_id": offerer_id},
                )

    db.session.flush()


def get_collective_bookings_to_cancel_on_offerer_closure(offerer_id: int) -> list[educational_models.CollectiveBooking]:
    now = date_utils.get_naive_utc_now()

    ongoing_collective_bookings = (
        db.session.query(educational_models.CollectiveBooking)
        .filter(
            educational_models.CollectiveBooking.offererId == offerer_id,
            educational_models.CollectiveBooking.status.in_(
                (
                    educational_models.CollectiveBookingStatus.CONFIRMED,
                    educational_models.CollectiveBookingStatus.PENDING,
                )
            ),
        )
        .options(
            sa_orm.joinedload(educational_models.CollectiveBooking.collectiveStock).load_only(
                educational_models.CollectiveStock.endDatetime
            )
        )
        .all()
    )

    # Do not cancel bookings which will become USED in auto_mark_as_used_after_event()
    return [
        collective_booking
        for collective_booking in ongoing_collective_bookings
        if not (
            collective_booking.status == educational_models.CollectiveBookingStatus.CONFIRMED
            and (now - USED_EVENT_DELAY <= collective_booking.collectiveStock.endDatetime <= now)
        )
    ]


def _cancel_collective_bookings_on_offerer_closure(offerer_id: int, author_id: int | None) -> None:
    collective_bookings = get_collective_bookings_to_cancel_on_offerer_closure(offerer_id)

    for collective_booking in collective_bookings:
        try:
            educational_booking_api.cancel_collective_booking(
                collective_booking,
                educational_models.CollectiveBookingCancellationReasons.OFFERER_CLOSED,
                author_id=author_id,
            )
        except Exception as exc:
            logger.exception(
                "Failed to cancel collective booking when closing offerer",
                extra={"exc": exc, "collective_booking_id": collective_booking.id, "offerer_id": offerer_id},
            )

    db.session.flush()


def handle_closed_offerer(offerer: offerers_models.Offerer, closure_date: date | None) -> None:
    action_kwargs: dict[str, typing.Any] = {
        "comment": "L'entité juridique est détectée comme fermée "
        + (closure_date.strftime("le %d/%m/%Y ") if closure_date else "")
        + "au répertoire Sirene (INSEE)"
    }
    with transaction():
        logger.info("SIREN is no longer active", extra={"offerer_id": offerer.id, "siren": offerer.siren})
        # Offerer may have been tagged in the past, but not closed
        if CLOSED_OFFERER_TAG_NAME not in (tag.name for tag in offerer.tags):
            # .one() raises an exception if the tag does not exist -- ensures that a potential issue is tracked
            tag = (
                db.session.query(offerers_models.OffererTag)
                .filter(offerers_models.OffererTag.name == CLOSED_OFFERER_TAG_NAME)
                .one()
            )
            action_kwargs["modified_info"] = {"tags": {"new_info": tag.label}}
            db.session.add(offerers_models.OffererTagMapping(offererId=offerer.id, tagId=tag.id))
        if offerer.isWaitingForValidation:
            reject_offerer(
                offerer=offerer,
                author_user=None,
                rejection_reason=offerers_models.OffererRejectionReason.CLOSED_BUSINESS,
                **action_kwargs,
            )
        elif offerer.isValidated and FeatureToggle.ENABLE_AUTO_CLOSE_CLOSED_OFFERERS.is_active():
            close_offerer(
                offerer,
                closure_date=closure_date,
                author_user=None,
                **action_kwargs,
            )
        elif "modified_info" in action_kwargs:
            history_api.add_action(
                history_models.ActionType.INFO_MODIFIED,
                author=None,
                offerer=offerer,
                **action_kwargs,
            )


def set_offerer_pending(
    offerer: offerers_models.Offerer,
    author_user: users_models.User,
    comment: str | None = None,
    tags_to_add: typing.Iterable[offerers_models.OffererTag] | None = None,
    tags_to_remove: typing.Iterable[offerers_models.OffererTag] | None = None,
) -> None:
    was_validated = offerer.isValidated
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
        author=author_user,
        offerer=offerer,
        venue=None,  # otherwise mypy does not accept extra_data dict
        user=None,  # otherwise mypy does not accept extra_data dict
        finance_incident=None,  # otherwise mypy does not accept extra_data dict
        bank_account=None,  # otherwise mypy does not accept extra_data dict
        rule=None,  # otherwise mypy does not accept extra_data dict
        chronicle=None,  # otherwise mypy does not accept extra_data dict
        user_profile_refresh_campaign=None,
        comment=comment,
        **extra_data,
    )

    db.session.flush()

    if was_validated:  # in case it was validated by mistake, then moved to PENDING state again
        _update_external_offerer(offerer, index_with_reason=IndexationReason.OFFERER_DEACTIVATION)


def add_comment_to_offerer(offerer: offerers_models.Offerer, author_user: users_models.User, comment: str) -> None:
    history_api.add_action(history_models.ActionType.COMMENT, author=author_user, offerer=offerer, comment=comment)
    db.session.flush()


def add_comment_to_venue(venue: offerers_models.Venue, author_user: users_models.User, comment: str) -> None:
    history_api.add_action(history_models.ActionType.COMMENT, author=author_user, venue=venue, comment=comment)


def get_timestamp_from_url(image_url: str) -> str:
    return image_url.split("_")[-1]


def rm_previous_venue_thumbs(venue: models.Venue) -> None:
    if not venue._bannerUrl:  # bannerUrl (with no underscore) always returns an url (potentially a default one)
        return

    # handle old banner urls that did not have a timestamp
    timestamp = get_timestamp_from_url(venue._bannerUrl) if "_" in venue._bannerUrl else ""
    storage.remove_thumb(venue, storage_id_suffix=str(timestamp), ignore_thumb_count=True)

    # some older venues might have a banner but not the original file
    # note: if bannerUrl is not None, bannerMeta should not be either.
    assert venue.bannerMeta is not None
    if original_image_url := venue.bannerMeta.get("original_image_url"):
        original_image_timestamp = get_timestamp_from_url(original_image_url)
        storage.remove_thumb(venue, storage_id_suffix=original_image_timestamp)

    venue.bannerUrl = None
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

    updated_at = date_utils.get_naive_utc_now()
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

    venue.bannerUrl = f"{venue.thumbUrl}_{banner_timestamp}"
    venue.bannerMeta = {
        "image_credit": image_credit,
        "author_id": user.id,
        "original_image_url": f"{venue.thumbUrl}_{original_image_timestamp}",
        "crop_params": crop_params,
        "updated_at": updated_at.isoformat(),
    }

    db.session.add(venue)
    db.session.flush()

    on_commit(
        partial(
            search.async_index_venue_ids,
            [venue.id],
            reason=IndexationReason.VENUE_BANNER_UPDATE,
        )
    )


def delete_venue_banner(venue: models.Venue) -> None:
    rm_previous_venue_thumbs(venue)

    db.session.add(venue)
    on_commit(
        partial(
            search.async_index_venue_ids,
            [venue.id],
            reason=IndexationReason.VENUE_BANNER_DELETION,
        )
    )


def can_offerer_create_educational_offer(offerer_id: int) -> bool:
    import pcapi.core.educational.adage_backends as adage_client

    if settings.CAN_COLLECTIVE_OFFERER_IGNORE_ADAGE:
        return True

    offerer: models.Offerer | None = db.session.query(models.Offerer).filter_by(id=offerer_id).one_or_none()
    if offerer is None:
        return False

    if offerer.allowedOnAdage:
        return True

    if offerers_repository.offerer_has_venue_with_adage_id(offerer_id):
        return True

    try:
        response = adage_client.get_adage_offerer(offerer.siren)
        return len(response) != 0
    except educational_exceptions.CulturalPartnerNotFoundException:
        return False


def get_educational_offerers(offerer_id: int | None, current_user: users_models.User) -> list[models.Offerer]:
    if current_user.has_admin_role and not offerer_id:
        logger.info("Admin user must provide offerer_id as a query parameter")
        raise exceptions.MissingOffererIdQueryParameter

    if offerer_id and current_user.has_admin_role:
        offerers = (
            db.session.query(models.Offerer)
            .filter(
                models.Offerer.isValidated,
                models.Offerer.isActive.is_(True),
                models.Offerer.id == offerer_id,
            )
            .options(
                sa_orm.joinedload(models.Offerer.managedVenues)
                .joinedload(models.Venue.offererAddress)
                .joinedload(models.OffererAddress.address),
            )
            .all()
        )
    else:
        offerers = (
            offerers_repository.get_all_offerers_for_user(
                user=current_user,
                validated=True,
            )
            .join(models.Offerer.managedVenues)
            .options(
                sa_orm.joinedload(models.Offerer.managedVenues)
                .joinedload(models.Venue.offererAddress)
                .joinedload(models.OffererAddress.address)
            )
            .distinct(models.Offerer.id)
            .all()
        )
    return offerers


def get_venues_by_batch(
    max_venues: int | None = None,
) -> typing.Generator[models.Venue, None, None]:
    query = db.session.query(models.Venue).order_by(models.Venue.id)

    if max_venues:
        query = query.limit(max_venues)

    yield from query.yield_per(1_000)


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
        db.session.query(offers_models.Stock)
        .join(offers_models.Offer)
        .filter(offers_models.Offer.venueId == venue.id)
        .filter(offers_models.Offer.is_released_and_bookable)
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


def get_venue_by_id(venue_id: int) -> offerers_models.Venue | None:
    return offerers_repository.get_venue_by_id(venue_id)


def search_offerer(search_query: str, departments: typing.Iterable[str] = ()) -> sa_orm.Query:
    offerers = db.session.query(models.Offerer).options(
        sa_orm.with_expression(
            offerers_models.Offerer.department_codes, offerers_models.Offerer.department_codes_expression()
        ),
        sa_orm.with_expression(offerers_models.Offerer.cities, offerers_models.Offerer.cities_expression()),
    )

    search_query = search_query.strip()
    if not search_query:
        return offerers.filter(sa.false())

    if departments:
        # At least one managed venue with SIRET in selected departments
        offerers = offerers.filter(
            sa.exists()
            .where(models.Venue.managingOffererId == models.Offerer.id)
            .where(models.Venue.siret.is_not(None))
            .where(models.OffererAddress.venueId == models.Venue.id)
            .where(models.OffererAddress.type == models.LocationType.VENUE_LOCATION)
            .where(geography_models.Address.id == models.OffererAddress.addressId)
            .where(geography_models.Address.departmentCode.in_(departments))
        )

    if search_query.isnumeric():
        numeric_filter = models.Offerer.id == int(search_query)
        if len(search_query) == siren_utils.SIREN_LENGTH:
            numeric_filter = sa.or_(numeric_filter, models.Offerer.siren == search_query)
        elif len(search_query) == siren_utils.RID7_LENGTH:
            numeric_filter = sa.or_(numeric_filter, models.Offerer.siren == siren_utils.rid7_to_siren(search_query))
        offerers = offerers.filter(numeric_filter)
    else:
        search_words = f"%{clean_accents(search_query).replace(' ', '%').replace('-', '%')}%"
        offerers = offerers.filter(sa.func.immutable_unaccent(offerers_models.Offerer.name).ilike(search_words))

        # Always order by similarity when searching by name
        offerers = offerers.order_by(sa.desc(sa.func.similarity(models.Offerer.name, search_query)))

    # At the end, order by id, in case of equal similarity score
    offerers = offerers.order_by(models.Offerer.id)

    return offerers


def search_venue(search_query: str, departments: typing.Iterable[str] = ()) -> sa_orm.Query:
    venues = (
        db.session.query(models.Venue)
        .outerjoin(models.VenueContact)
        .options(
            sa_orm.joinedload(models.Venue.contact),
            sa_orm.joinedload(models.Venue.managingOfferer),
        )
    )

    search_query = search_query.strip()
    if not search_query:
        return venues.filter(sa.false())

    if departments:
        venues = (
            venues.outerjoin(models.Venue.offererAddress)
            .outerjoin(models.OffererAddress.address)
            .filter(geography_models.Address.departmentCode.in_(departments))
        )

    if search_query.isnumeric():
        numeric_filter = models.Venue.id == int(search_query)
        if len(search_query) == siren_utils.SIRET_LENGTH:
            numeric_filter = sa.or_(numeric_filter, models.Venue.siret == search_query)
        elif len(search_query) == 12:
            # for dmsToken containing digits only
            numeric_filter = sa.or_(numeric_filter, models.Venue.dmsToken == search_query)
        elif len(search_query) == siren_utils.RIDET_LENGTH:
            numeric_filter = sa.or_(numeric_filter, models.Venue.siret == siren_utils.ridet_to_siret(search_query))
        venues = venues.filter(numeric_filter)
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
            search_words = f"%{clean_accents(search_query).replace(' ', '%').replace('-', '%')}%"
            venues = venues.filter(
                sa.or_(
                    sa.func.immutable_unaccent(offerers_models.Venue.name).ilike(search_words),
                    sa.func.immutable_unaccent(offerers_models.Venue.publicName).ilike(search_words),
                )
            )

        # Always order by similarity when searching by name
        venues = venues.order_by(
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


def search_bank_account(search_query: str, *_: typing.Any) -> sa_orm.Query:
    bank_accounts_query = db.session.query(finance_models.BankAccount).options(
        sa_orm.joinedload(finance_models.BankAccount.offerer)
    )

    search_query = search_query.strip()
    if not search_query:
        return bank_accounts_query.filter(sa.false())

    filters = []

    try:
        dehumanized_id = human_ids.dehumanize(search_query)
    except human_ids.NonDehumanizableId:
        pass
    else:
        filters.append(finance_models.BankAccount.id == dehumanized_id)

    if string_utils.is_numeric(search_query):
        filters.append(finance_models.BankAccount.id == int(search_query))

    try:
        iban = schwifty.IBAN(search_query)
    except ValueError:  # All SchwiftyException are ValueError
        pass
    else:
        filters.append(finance_models.BankAccount.iban == iban.compact)

    if re.match(r"^[AF]\d{9}$", search_query):
        bank_accounts_query = bank_accounts_query.join(finance_models.Invoice)
        filters.append(finance_models.Invoice.reference == search_query)

    if not filters:
        return bank_accounts_query.filter(sa.false())

    return bank_accounts_query.filter(sa.or_(*filters) if len(filters) > 0 else filters[0])


def get_offerer_total_revenue(offerer_id: int, only_current_year: bool = False) -> decimal.Decimal | float:
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

    if only_current_year:
        # Bookings used this year or still with status CONFIRMED
        time_delta = sa.func.cast(sa.func.concat(1, " HOUR"), INTERVAL)  # UTC -> CET conversion on January 1st
        current_year = sa.func.date_part("YEAR", sa.func.now() + time_delta)
        individual_revenue_query = individual_revenue_query.filter(
            sa.or_(
                bookings_models.Booking.dateUsed.is_(None),
                sa.func.date_part("YEAR", bookings_models.Booking.dateUsed + time_delta) == current_year,
            )
        )
        collective_revenue_query = collective_revenue_query.filter(
            sa.or_(
                educational_models.CollectiveBooking.dateUsed.is_(None),
                sa.func.date_part("YEAR", educational_models.CollectiveBooking.dateUsed + time_delta) == current_year,
            )
        )

    total_revenue_query = sa.select(
        individual_revenue_query.scalar_subquery() + collective_revenue_query.scalar_subquery()
    )

    return db.session.execute(total_revenue_query).scalar() or 0.0


def get_venues_stats(venue_ids: typing.Iterable[int]) -> dict[str, int | float | None]:
    tuple_venue_ids = tuple(venue_ids)
    stats: dict[str, int | float | None] = defaultdict(lambda: None)

    if not tuple_venue_ids:
        return stats

    try:
        if bookings_count := clickhouse_queries.CountBookingsQuery().execute({"venue_ids": tuple_venue_ids}):
            stats |= bookings_count[0].dict()
        if offers_data := clickhouse_queries.CountOffersQuery().execute({"venue_ids": tuple_venue_ids}):
            stats |= offers_data[0].dict()
        revenues = clickhouse_queries.AggregatedTotalRevenueQuery().execute({"venue_ids": tuple_venue_ids})
        stats["total_revenue"] = sum([r.expected_revenue.total for r in revenues])
    except ApiErrors as e:
        logger.exception(
            "An error occurred while requesting clickhouse for venues %s stats. Error %s",
            venue_ids,
            e.errors["clickhouse"],
        )

    stats["total_collective_offer_templates"] = (
        db.session.query(
            sa.func.count(educational_models.CollectiveOfferTemplate.id),
        )
        .filter(
            educational_models.CollectiveOfferTemplate.venueId.in_(tuple_venue_ids),
        )
        .scalar()
    )

    return stats


@dataclasses.dataclass
class OfferConsultationModel:
    offer_id: str
    consultation_count: int


@dataclasses.dataclass
class VenueOffersStatisticsModel:
    offers_consultation_count: int
    top_offers_by_consultation: list[OfferConsultationModel]


def get_venue_offers_statistics(venue_id: int) -> VenueOffersStatisticsModel:
    offers_consultation_count = clickhouse_queries.OfferConsultationCountQuery().execute({"venue_id": venue_id})
    top_offers_by_consultation = clickhouse_queries.TopOffersByConsultationQuery().execute({"venue_id": venue_id})

    return VenueOffersStatisticsModel(
        offers_consultation_count=offers_consultation_count[0].total_views_6_months if offers_consultation_count else 0,
        top_offers_by_consultation=[
            OfferConsultationModel(
                offer_id=offer.offer_id,
                consultation_count=offer.total_views_last_30_days,
            )
            for offer in top_offers_by_consultation
        ],
    )


def count_offerers_by_validation_status() -> dict[str, int]:
    stats: dict[validation_status_mixin.ValidationStatus, int] = dict(
        db.session.query(  # type: ignore [arg-type]
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
    name: str | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    label: str | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    description: str | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    categories: list[models.OffererTagCategory] | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
) -> None:
    if name is not offerers_constants.UNCHANGED:
        offerer_tag.name = name
    if label is not offerers_constants.UNCHANGED:
        offerer_tag.label = label
    if description is not offerers_constants.UNCHANGED:
        offerer_tag.description = description
    if categories is not offerers_constants.UNCHANGED:
        if set(offerer_tag.categories) != set(categories):
            offerer_tag.categories = categories

    db.session.add(offerer_tag)
    db.session.flush()


def create_venue_registration(venue_id: int, target: offerers_models.Target, web_presence: str | None) -> None:
    venue_registration = offerers_models.VenueRegistration(venueId=venue_id, target=target, webPresence=web_presence)
    db.session.add(venue_registration)
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()

    if web_presence:
        for url in web_presence.split(", "):
            virustotal.request_url_scan(url, skip_if_recent_scan=True)


def create_from_onboarding_data(
    user: users_models.User,
    onboarding_data: offerers_serialize.SaveNewOnboardingDataQueryModel,
) -> models.UserOfferer:
    # Get name (raison sociale) from Sirene API
    siret_info = find_structure_data(onboarding_data.siret)
    if not siret_info.diffusible:
        if onboarding_data.publicName:
            name = onboarding_data.publicName
        else:
            raise exceptions.publicNameRequiredException("missing mandatory value for public name")
    else:
        name = siret_info.name

    link_cultural_domains_to_venue(onboarding_data.culturalDomains, None, None)

    # Create Offerer or attach user to existing Offerer
    offerer_creation_info = offerers_serialize.CreateOffererQueryModel(
        street=onboarding_data.address.street,
        city=onboarding_data.address.city,
        latitude=float(onboarding_data.address.latitude),
        longitude=float(onboarding_data.address.longitude),
        name=name,
        postalCode=onboarding_data.address.postalCode,
        inseeCode=onboarding_data.address.inseeCode,
        siren=onboarding_data.siret[:9],
        phoneNumber=onboarding_data.phoneNumber,
    )
    new_onboarding_info = NewOnboardingInfo(
        activity=offerers_models.Activity[onboarding_data.activity.name] if onboarding_data.activity else None,
        target=onboarding_data.target,
        venueTypeCode=onboarding_data.venueTypeCode,
        webPresence=onboarding_data.webPresence,
    )
    user_offerer = create_offerer(user, offerer_creation_info, new_onboarding_info, insee_data=siret_info)

    # Create Venue with siret if it's not in DB yet, or Venue without siret if requested
    venue = offerers_repository.find_venue_by_siret(onboarding_data.siret)
    if (
        venue
        and onboarding_data.createVenueWithoutSiret
        and siret_info.ape_code
        and not APE_TAG_MAPPING.get(siret_info.ape_code, False)
        and FeatureToggle.WIP_RESTRICT_VENUE_CREATION_TO_COLLECTIVITY.is_active()
    ):
        raise exceptions.NotACollectivity()
    if not venue or onboarding_data.createVenueWithoutSiret:
        address = onboarding_data.address
        if not address.street:
            address = address.copy(update={"street": "n/d"})
        common_kwargs = dict(
            activity=offerers_models.Activity[onboarding_data.activity.name] if onboarding_data.activity else None,
            address=address,
            bookingEmail=user.email,
            culturalDomains=onboarding_data.culturalDomains,
            contact=None,
            description=None,
            isOpenToPublic=onboarding_data.isOpenToPublic,
            managingOffererId=user_offerer.offererId,
            name=name,
            publicName=onboarding_data.publicName,
            venueLabelId=None,
            venueTypeCode=onboarding_data.venueTypeCode,
            withdrawalDetails=None,
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
        venue_creation_info = venues_serialize.PostVenueBodyModel(**venue_kwargs)  # type: ignore[arg-type]
        venue = create_venue(venue_creation_info, user)
        create_venue_registration(venue.id, new_onboarding_info.target, new_onboarding_info.webPresence)

    # Send welcome email only in the case of offerer creation
    if user_offerer.validationStatus == ValidationStatus.VALIDATED:
        transactional_mails.send_welcome_to_pro_email(user, venue)

    logger.info(
        "Creating new Offerer and Venue",
        extra={
            "user_id": user.id,
            "offerer_id": user_offerer.offerer.id,
            "venue_id": venue.id,
            "siret": venue.siret,
            "is_diffusible": siret_info.diffusible,
        },
        technical_message_id="structure_creation",
    )

    return user_offerer


def suspend_offerer(offerer: models.Offerer, actor: users_models.User, comment: str | None) -> None:
    if not offerer.isActive:
        return

    if bookings_repository.offerer_has_ongoing_bookings(offerer.id):
        raise exceptions.CannotSuspendOffererWithBookingsException()

    offerer.isActive = False
    db.session.add(offerer)
    history_api.add_action(history_models.ActionType.OFFERER_SUSPENDED, author=actor, offerer=offerer, comment=comment)
    db.session.flush()

    _update_external_offerer(offerer, index_with_reason=IndexationReason.OFFERER_DEACTIVATION)


def unsuspend_offerer(offerer: models.Offerer, actor: users_models.User, comment: str | None) -> None:
    if offerer.isActive:
        return

    offerer.isActive = True
    db.session.add(offerer)
    history_api.add_action(
        history_models.ActionType.OFFERER_UNSUSPENDED, author=actor, offerer=offerer, comment=comment
    )
    db.session.flush()

    _update_external_offerer(offerer, index_with_reason=IndexationReason.OFFERER_ACTIVATION)


def _update_external_offerer(offerer: models.Offerer, *, index_with_reason: IndexationReason | None = None) -> None:
    for email in offerers_repository.get_emails_by_offerer(offerer):
        external_attributes_api.update_external_pro(email)

    zendesk_sell.update_offerer(offerer)

    if not index_with_reason:
        return

    venue_ids = {venue.id for venue in offerer.managedVenues}
    if not venue_ids:
        return

    # _reindex_* unindexes venues and offers which are not eligible for search (including offerer no longer active)
    on_commit(functools.partial(search.async_index_venue_ids, venue_ids, reason=index_with_reason))
    on_commit(functools.partial(search.async_index_offers_of_venue_ids, venue_ids, reason=index_with_reason))

    packed_collective_ids = db.session.query(educational_models.CollectiveOfferTemplate.id).filter(
        educational_models.CollectiveOfferTemplate.venueId.in_(venue_ids)
    )
    on_commit(
        functools.partial(
            search.async_index_collective_offer_template_ids,
            {i for (i,) in packed_collective_ids},
            reason=index_with_reason,
        )
    )


def delete_offerer(offerer_id: int) -> None:
    offerer_has_bookings = db.session.query(
        db.session.query(bookings_models.Booking).filter(bookings_models.Booking.offererId == offerer_id).exists()
    ).scalar()

    offerer_has_collective_bookings = db.session.query(
        db.session.query(educational_models.CollectiveBooking)
        .filter(educational_models.CollectiveBooking.offererId == offerer_id)
        .exists()
    ).scalar()

    if offerer_has_bookings or offerer_has_collective_bookings:
        raise exceptions.CannotDeleteOffererWithBookingsException()

    offerer_is_linked_to_provider = db.session.query(
        db.session.query(models.OffererProvider).filter(models.OffererProvider.offererId == offerer_id).exists()
    ).scalar()

    if offerer_is_linked_to_provider:
        raise exceptions.CannotDeleteOffererLinkedToProvider()

    offerer_associated_with_reimbursement_rule = db.session.query(
        db.session.query(finance_models.CustomReimbursementRule)
        .outerjoin(finance_models.CustomReimbursementRule.venue)
        .filter(
            sa.or_(
                finance_models.CustomReimbursementRule.offererId == offerer_id,
                offerers_models.Venue.managingOffererId == offerer_id,
            )
        )
        .exists()
    ).scalar()
    if offerer_associated_with_reimbursement_rule:
        raise exceptions.CannotDeleteOffererWithActiveOrFutureCustomReimbursementRule()

    venue_ids_query = (
        db.session.query(offerers_models.Venue)
        .filter_by(managingOffererId=offerer_id)
        .with_entities(offerers_models.Venue.id)
    )
    venue_ids = [venue_id[0] for venue_id in venue_ids_query.all()]

    offer_ids_to_delete: dict = {
        "individual_offer_ids_to_delete": [],
        "collective_offer_template_ids_to_delete": [],
    }
    for venue_id in venue_ids:
        venue_offer_ids_to_delete = _delete_objects_linked_to_venue(venue_id)
        offer_ids_to_delete["individual_offer_ids_to_delete"] += venue_offer_ids_to_delete[
            "individual_offer_ids_to_delete"
        ]

        offer_ids_to_delete["collective_offer_template_ids_to_delete"] += venue_offer_ids_to_delete[
            "collective_offer_template_ids_to_delete"
        ]

    db.session.query(offerers_models.VenuePricingPointLink).filter(
        offerers_models.VenuePricingPointLink.venueId.in_(venue_ids)
        | offerers_models.VenuePricingPointLink.pricingPointId.in_(venue_ids),
    ).delete(synchronize_session=False)

    db.session.query(offerers_models.Venue).filter(offerers_models.Venue.managingOffererId == offerer_id).delete(
        synchronize_session=False
    )

    db.session.query(offerers_models.NonPaymentNotice).filter(
        offerers_models.NonPaymentNotice.offererId == offerer_id
    ).delete(synchronize_session=False)

    db.session.query(offerers_models.UserOfferer).filter(offerers_models.UserOfferer.offererId == offerer_id).delete(
        synchronize_session=False
    )

    db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.id == offerer_id).delete(
        synchronize_session=False
    )

    db.session.flush()

    on_commit(
        functools.partial(
            search.unindex_offer_ids,
            offer_ids_to_delete["individual_offer_ids_to_delete"],
        ),
    )
    on_commit(
        functools.partial(
            search.unindex_collective_offer_template_ids,
            offer_ids_to_delete["collective_offer_template_ids_to_delete"],
        ),
    )
    on_commit(
        functools.partial(
            search.unindex_venue_ids,
            venue_ids,
        ),
    )


def invite_member(offerer: models.Offerer, email: str, current_user: users_models.User) -> None:
    existing_invited_email = (
        db.session.query(models.OffererInvitation)
        .filter(models.OffererInvitation.offererId == offerer.id)
        .filter(models.OffererInvitation.email == email)
        .one_or_none()
    )

    if existing_invited_email:  # already invited
        raise exceptions.EmailAlreadyInvitedException()

    existing_user = (
        db.session.query(users_models.User)
        .filter(users_models.User.email == email)
        .outerjoin(users_models.User.UserOfferers)
        .options(sa_orm.joinedload(users_models.User.UserOfferers).load_only(models.UserOfferer.offererId))
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
            author=current_user,
            user=existing_user,
            offerer=offerer_invitation.offerer,
            comment="Rattachement créé par invitation",
            inviter_user_id=current_user.id,
            offerer_invitation_id=offerer_invitation.id,
        )
        db.session.flush()
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
        db.session.flush()
        logger.info(
            "New user invited to join offerer",
            extra={"offerer": offerer.id, "invited_user": email, "invited_by": current_user.id},
        )

    transactional_mails.send_offerer_attachment_invitation([email], offerer, existing_user)


def invite_member_again(offerer: models.Offerer, email: str) -> None:
    existing_invited_email = (
        db.session.query(models.OffererInvitation)
        .filter(models.OffererInvitation.offererId == offerer.id)
        .filter(models.OffererInvitation.email == email)
        .one_or_none()
    )

    if not existing_invited_email or existing_invited_email.status == models.InvitationStatus.ACCEPTED:
        raise exceptions.InviteAgainImpossibleException()

    existing_user = (
        db.session.query(users_models.User)
        .filter(users_models.User.email == email)
        .outerjoin(users_models.User.UserOfferers)
        .options(sa_orm.joinedload(users_models.User.UserOfferers).load_only(models.UserOfferer.offererId))
        .one_or_none()
    )

    transactional_mails.send_offerer_attachment_invitation([email], offerer, user=existing_user)


def get_offerer_members(offerer: models.Offerer) -> list[tuple[str, OffererMemberStatus]]:
    users_offerers = (
        db.session.query(models.UserOfferer)
        .filter(
            models.UserOfferer.offererId == offerer.id,
            sa.not_(models.UserOfferer.isRejected),
            sa.not_(models.UserOfferer.isDeleted),
        )
        .options(sa_orm.joinedload(models.UserOfferer.user).load_only(users_models.User.email))
        .all()
    )
    invited_members = (
        db.session.query(models.OffererInvitation)
        .filter_by(offererId=offerer.id)
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
        db.session.query(models.OffererInvitation)
        .filter_by(email=user.email)
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
            author=user,
            user=user,
            offerer=offerer_invitation.offerer,
            comment="Rattachement créé par invitation",
            inviter_user_id=inviter_user.id,
            offerer_invitation_id=offerer_invitation.id,
        )
        offerer_invitation.status = offerers_models.InvitationStatus.ACCEPTED
        db.session.add_all([user_offerer, offerer_invitation])
        if is_managed_transaction():
            db.session.flush()
        else:
            db.session.commit()
        external_attributes_api.update_external_pro(user.email)
        zendesk_sell.create_offerer(user_offerer.offerer)
        logger.info(
            "UserOfferer created from invitation",
            extra={"offerer": user_offerer.offerer, "invitedUserId": user.id, "inviterUserId": inviter_user.id},
        )


def delete_expired_offerer_invitations() -> None:
    count = (
        db.session.query(offerers_models.OffererInvitation)
        .filter(
            offerers_models.OffererInvitation.status == offerers_models.InvitationStatus.PENDING,
            offerers_models.OffererInvitation.dateCreated
            < date_utils.get_naive_utc_now() - timedelta(days=settings.OFFERER_INVITATION_EXPIRATION_DELAY),
        )
        .delete(synchronize_session=False)
    )
    logger.info("%s offerer invitations deleted", count)


@dataclasses.dataclass
class OffererVenues:
    offerer: offerers_models.Offerer
    venues: typing.Sequence[offerers_models.Venue]


def get_providers_offerer_and_venues(
    provider: providers_models.Provider, siren: str | None = None
) -> typing.Generator[OffererVenues, None, None]:
    offerers_query = (
        db.session.query(offerers_models.Offerer, offerers_models.Venue)
        .options(
            sa_orm.joinedload(offerers_models.Venue.offererAddress).joinedload(offerers_models.OffererAddress.address)
        )
        .join(offerers_models.Venue, offerers_models.Offerer.managedVenues)
        .join(providers_models.VenueProvider, offerers_models.Venue.venueProviders)
        .join(providers_models.Provider, providers_models.VenueProvider.provider)
        .filter(providers_models.VenueProvider.providerId == provider.id)
        .filter(providers_models.VenueProvider.isActive)
        .order_by(offerers_models.Offerer.id, offerers_models.Venue.id)
    )

    if siren:
        offerers_query = offerers_query.filter(offerers_models.Offerer.siren == siren)

    for offerer, group in itertools.groupby(offerers_query, lambda row: row.Offerer):
        yield OffererVenues(offerer=offerer, venues=[row.Venue for row in group])


def get_offerer_stats_data(offerer_id: int) -> list[offerers_models.OffererStats]:
    return db.session.query(offerers_models.OffererStats).filter_by(offererId=offerer_id).all()


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


@dataclasses.dataclass
class OffersStatsByVenue:
    published_public_offers: int
    published_educational_offers: int
    pending_educational_offers: int
    pending_public_offers: int


def get_offers_stats_by_venue(venue_id: int) -> OffersStatsByVenue:
    return OffersStatsByVenue(
        published_public_offers=offerers_repository.get_number_of_bookable_offers_for_venue(venue_id=venue_id),
        published_educational_offers=offerers_repository.get_number_of_bookable_collective_offers_for_venue(
            venue_id=venue_id
        ),
        pending_public_offers=offerers_repository.get_number_of_pending_offers_for_venue(venue_id=venue_id),
        pending_educational_offers=offerers_repository.get_number_of_pending_collective_offers_for_venue(
            venue_id=venue_id
        ),
    )


def delete_venue_accessibility_provider(venue: models.Venue) -> None:
    db.session.query(models.AccessibilityProvider).filter_by(venueId=venue.id).delete(synchronize_session=False)
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()


def set_accessibility_provider_id(
    venue: models.Venue, id_at_provider: str | None = None, url_at_provider: str | None = None
) -> None:
    assert venue.offererAddress and venue.offererAddress.address  # helps mypy, shouldn't happen
    if not (id_at_provider and url_at_provider):
        if id_and_url_at_provider := accessibility_provider.get_id_at_accessibility_provider(
            name=venue.name,
            public_name=venue.publicName,
            siret=venue.siret,
            ban_id=venue.offererAddress.address.banId,
            city=venue.offererAddress.address.city,
            postal_code=venue.offererAddress.address.postalCode,
            address=venue.offererAddress.address.street,
        ):
            id_at_provider = id_and_url_at_provider["slug"]
            url_at_provider = id_and_url_at_provider["url"]
    if id_at_provider and url_at_provider:
        if not venue.accessibilityProvider:
            venue.accessibilityProvider = models.AccessibilityProvider(
                externalAccessibilityId=id_at_provider,
                externalAccessibilityUrl=url_at_provider,
            )
        else:
            venue.accessibilityProvider.externalAccessibilityId = id_at_provider
            venue.accessibilityProvider.externalAccessibilityUrl = url_at_provider
        db.session.add(venue.accessibilityProvider)


def set_accessibility_infos_from_provider_id(venue: models.Venue) -> None:
    if venue.accessibilityProvider:
        last_update, accessibility_data = accessibility_provider.get_accessibility_infos(
            slug=venue.accessibilityProvider.externalAccessibilityId
        )
        if last_update and accessibility_data:
            venue.accessibilityProvider.externalAccessibilityData = accessibility_data.dict()
            venue.accessibilityProvider.lastUpdateAtProvider = last_update
            db.session.add(venue.accessibilityProvider)


def count_open_to_public_venues_with_accessibility_provider() -> int:
    return (
        db.session.query(offerers_models.Venue)
        .join(offerers_models.AccessibilityProvider)
        .filter(
            sa.or_(offerers_models.Venue.isOpenToPublic.is_(True)),
            offerers_models.Venue.isVirtual.is_(False),
        )
        .count()
    )


def get_open_to_public_venues_with_accessibility_provider(batch_size: int, batch_num: int) -> list[models.Venue]:
    return (
        db.session.query(offerers_models.Venue)
        .join(offerers_models.Venue.accessibilityProvider)
        .filter(
            sa.or_(offerers_models.Venue.isOpenToPublic.is_(True)),
            offerers_models.Venue.isVirtual.is_(False),
        )
        .options(sa_orm.contains_eager(offerers_models.Venue.accessibilityProvider))
        .order_by(offerers_models.Venue.id.asc())
        .limit(batch_size)
        .offset(batch_num * batch_size)
        .all()
    )


def get_open_to_public_venues_without_accessibility_provider() -> list[models.Venue]:
    return (
        db.session.query(offerers_models.Venue)
        .outerjoin(offerers_models.Venue.accessibilityProvider)
        .filter(
            sa.or_(offerers_models.Venue.isOpenToPublic.is_(True)),
            offerers_models.Venue.isVirtual.is_(False),
            offerers_models.AccessibilityProvider.id.is_(None),
        )
        .options(
            sa_orm.load_only(
                offerers_models.Venue.name,
                offerers_models.Venue.publicName,
                offerers_models.Venue.siret,
            ),
            sa_orm.joinedload(offerers_models.Venue.offererAddress)
            .joinedload(offerers_models.OffererAddress.address)
            .load_only(
                geography_models.Address.street,
                geography_models.Address.banId,
            ),
        )
        .order_by(offerers_models.Venue.id.asc())
        .all()
    )


def synchronize_accessibility_provider(venue: models.Venue, force_sync: bool = False) -> None:
    assert venue.accessibilityProvider  # helps mypy, ensured by caller
    assert venue.offererAddress and venue.offererAddress.address  # helps mypy, shouldn't happen
    slug = venue.accessibilityProvider.externalAccessibilityId
    try:
        last_update, accessibility_data = accessibility_provider.get_accessibility_infos(slug=slug)
    except accessibility_provider.AccesLibreApiException as e:
        logger.exception("An error occurred while requesting Acceslibre widget for venue: %s, Error: %s", venue, e)
        return

    # If last_update is not None: match still exist
    # Then we update accessibility data if :
    # 1. accessibility data is None
    # 2. we have forced the synchronization
    # 3. accessibility data has been updated on acceslibre side
    if last_update and (
        not venue.accessibilityProvider.externalAccessibilityData
        or force_sync
        or venue.accessibilityProvider.lastUpdateAtProvider.astimezone(pytz.utc) < last_update.astimezone(pytz.utc)
    ):
        venue.accessibilityProvider.lastUpdateAtProvider = last_update
        venue.accessibilityProvider.externalAccessibilityData = (
            accessibility_data.dict() if accessibility_data else None
        )
        db.session.add(venue.accessibilityProvider)

    # if last_update is None, the slug has been removed from acceslibre, we try a new match
    # and save accessibility data to DB
    elif not last_update:
        try:
            id_and_url_at_provider = accessibility_provider.get_id_at_accessibility_provider(
                name=venue.name,
                public_name=venue.publicName,
                siret=venue.siret,
                ban_id=venue.offererAddress.address.banId,
                city=venue.offererAddress.address.city,
                postal_code=venue.offererAddress.address.postalCode,
                address=venue.offererAddress.address.street,
            )
        except accessibility_provider.AccesLibreApiException as e:
            logger.exception("An error occurred while requesting Acceslibre for venue: %s, Error: %s", venue, e)
            return
        if id_and_url_at_provider:
            new_slug = id_and_url_at_provider["slug"]
            new_url = id_and_url_at_provider["url"]
            try:
                last_update, accessibility_data = accessibility_provider.get_accessibility_infos(slug=new_slug)
            except accessibility_provider.AccesLibreApiException as e:
                logger.exception(
                    "An error occurred while requesting Acceslibre widget for venue: %s, Error: %s", venue, e
                )
                return
            if last_update and accessibility_data:
                venue.accessibilityProvider.externalAccessibilityId = new_slug
                venue.accessibilityProvider.externalAccessibilityUrl = new_url
                venue.accessibilityProvider.lastUpdateAtProvider = last_update
                venue.accessibilityProvider.externalAccessibilityData = (
                    accessibility_data.dict() if accessibility_data else None
                )
                db.session.add(venue.accessibilityProvider)
        else:
            logger.info(
                "Acceslibre synchronisation loss",
                extra={
                    "analyticsSource": "app-pro",
                    "venue_id": venue.id,
                    "acceslibre_slug": slug,
                    "slug_loss_message": "Slug not found at acceslibre, AccessibilityProvider removed for this venue",
                },
                technical_message_id="acceslibre.synchronisation",
            )
            db.session.delete(venue.accessibilityProvider)

    # In case a venue is synchronized but has no data, we want to be informed
    if venue.accessibilityProvider and not venue.accessibilityProvider.externalAccessibilityData:
        logger.error(
            "Venue %s is synchronized with Acceslibre at %s but has no data",
            venue.id,
            venue.accessibilityProvider.externalAccessibilityData,
        )


def synchronize_accessibility_with_acceslibre(
    dry_run: bool, force_sync: bool, batch_size: int, start_from_batch: int = 1
) -> None:
    """
    For all venues synchronized with acceslibre, we fetch on a weekly basis the
    last_update_at and update their accessibility information.

    If we use the --force_sync flag, it will not check for last_update_at

    If we use the --start-from-batch option, it will start synchronization from the given batch number
    Use case: synchronization has failed with message "Could not update batch <n>"

    If externalAccessibilityId can't be found at acceslibre, we try to find a new match, cf. synchronize_accessibility_provider()
    """
    venues_count = count_open_to_public_venues_with_accessibility_provider()
    num_batches = ceil(venues_count / batch_size)
    if start_from_batch > num_batches:
        logger.error("Start from batch must be less than %d", num_batches)
        return

    start_batch_index = start_from_batch - 1
    for i in range(start_batch_index, num_batches):
        venues_list = get_open_to_public_venues_with_accessibility_provider(batch_size=batch_size, batch_num=i)
        for venue in venues_list:
            synchronize_accessibility_provider(venue, force_sync)

        if not dry_run:
            try:
                db.session.commit()
            except sa.exc.SQLAlchemyError:
                logger.exception("Could not update batch %d", i + 1)
                db.session.rollback()
        else:
            db.session.rollback()
    logger.info("Accessibility data synchronization with acceslibre complete successfully")


def match_acceslibre(venue: offerers_models.Venue) -> None:
    old_slug = venue.external_accessibility_id
    old_url = venue.external_accessibility_url
    delete_venue_accessibility_provider(venue)
    # TODO(xordoquy): see why delete_venue_accessibility_provider doesn't synchronize session
    db.session.refresh(venue)
    set_accessibility_provider_id(venue)

    if not venue.accessibilityProvider:
        logger.info("No match found at acceslibre for Venue %s ", venue.id)
        return
    if old_slug != venue.accessibilityProvider.externalAccessibilityId:
        history_api.add_action(
            history_models.ActionType.INFO_MODIFIED,
            author=None,
            venue=venue,
            comment="Recherche automatisée du lieu permanent avec Acceslibre",
            modified_info={
                "accessibilityProvider.externalAccessibilityId": {
                    "old_info": old_slug,
                    "new_info": venue.accessibilityProvider.externalAccessibilityId,
                },
                "accessibilityProvider.externalAccessibilityUrl": {
                    "old_info": old_url,
                    "new_info": venue.accessibilityProvider.externalAccessibilityUrl,
                },
            },
        )

    set_accessibility_infos_from_provider_id(venue)
    db.session.add(venue)
    db.session.commit()


def match_venue_with_new_entries(
    venues_list: list[models.Venue],
    results: list[accessibility_provider.AcceslibreResult],
) -> None:
    for venue in venues_list:
        assert venue.offererAddress and venue.offererAddress.address  # helps mypy, shouldn't happen
        if matching_venue := accessibility_provider.match_venue_with_acceslibre(
            acceslibre_results=results,
            venue_name=venue.name,
            venue_public_name=venue.publicName,
            venue_address=venue.offererAddress.address.street,
            venue_city=venue.offererAddress.address.city,
            venue_postal_code=venue.offererAddress.address.postalCode,
            venue_ban_id=venue.offererAddress.address.banId,
            venue_siret=venue.siret,
        ):
            venue.accessibilityProvider = offerers_models.AccessibilityProvider(
                externalAccessibilityId=matching_venue.slug,
                externalAccessibilityUrl=matching_venue.web_url,
            )
            db.session.add(venue.accessibilityProvider)


def acceslibre_matching(batch_size: int, dry_run: bool, start_from_batch: int, n_days_to_fetch: int = 7) -> None:
    """
    For all venues opened to public, we are looking for a match at acceslibre

    If we use the --start-from-batch option, it will start synchronization from the given batch number
    Use case: synchronization has failed with message "Could not update batch <n>"
    """
    synchronized_venues_count_before_matching = count_open_to_public_venues_with_accessibility_provider()
    venues_list = get_open_to_public_venues_without_accessibility_provider()
    num_batches = ceil(len(venues_list) / batch_size)
    if start_from_batch > num_batches:
        logger.info("Start from batch must be less than %d", num_batches)
        return

    results_list = []

    for activity in accessibility_provider.AcceslibreActivity:
        if results_by_activity := accessibility_provider.find_new_entries_by_activity(activity, n_days_to_fetch):
            results_list.extend(results_by_activity)

    start_batch_index = start_from_batch - 1
    for i in range(start_batch_index, num_batches):
        batch_start = i * batch_size
        batch_end = (i + 1) * batch_size
        match_venue_with_new_entries(venues_list[batch_start:batch_end], results_list)

        if not dry_run:
            try:
                db.session.commit()
            except sa.exc.SQLAlchemyError:
                logger.exception("Could not update batch %d", i + 1)
                db.session.rollback()
    new_match_found = (
        count_open_to_public_venues_with_accessibility_provider() - synchronized_venues_count_before_matching
    )
    logger.info("%d new match found over last %d days", new_match_found, n_days_to_fetch)
    if dry_run:
        logger.info("Matching with acceslibre as dry run complete")
        db.session.rollback()
    else:
        logger.info("Matching with acceslibre complete")


LocationData = typing.TypedDict(
    "LocationData",
    {
        "street": str,
        "city": str,
        "postal_code": str,
        "insee_code": str | None,
        # TODO(xordoquy): change lat/long to decimal
        "latitude": float,
        "longitude": float,
        "ban_id": str | None,
    },
)


def get_or_create_address(location_data: LocationData, is_manual_edition: bool = False) -> geography_models.Address:
    insee_code = location_data.get("insee_code")
    postal_code = location_data["postal_code"]
    latitude = geography_utils.format_coordinate(location_data["latitude"])
    longitude = geography_utils.format_coordinate(location_data["longitude"])
    street = location_data["street"]
    city = location_data["city"]
    ban_id = None if is_manual_edition else location_data.get("ban_id")
    city_code = insee_code or postal_code

    department_code = utils_regions.get_department_code_from_city_code(city_code)
    timezone = date_utils.get_department_timezone(department_code)

    with transaction():
        try:
            address = geography_models.Address(
                banId=ban_id,
                inseeCode=insee_code,
                street=street,
                postalCode=postal_code,
                city=city,
                latitude=latitude,
                longitude=longitude,
                departmentCode=department_code,
                timezone=timezone,
                isManualEdition=is_manual_edition,
            )
            db.session.add(address)
            db.session.flush()
        except sa.exc.IntegrityError:
            address = None
            if is_managed_transaction():
                mark_transaction_as_invalid()
            else:
                db.session.rollback()

    if address is None:
        address = (
            db.session.query(geography_models.Address)
            .filter(
                geography_models.Address.banId == ban_id,
                geography_models.Address.inseeCode == insee_code,
                geography_models.Address.street == street,
                geography_models.Address.postalCode == postal_code,
                geography_models.Address.city == city,
                geography_models.Address.latitude == latitude,
                geography_models.Address.longitude == longitude,
            )
            .one()
        )

    return address


def get_or_create_offer_location(offerer_id: int, address_id: int, label: str | None = None) -> models.OffererAddress:
    offerer_address: models.OffererAddress | None = (
        db.session.query(models.OffererAddress)
        .filter(
            models.OffererAddress.offererId == offerer_id,
            models.OffererAddress.label == label,
            models.OffererAddress.addressId == address_id,
            # TODO (prouzet, 2025-11-13) CLEAN_OA When data is migrated, only filter on OFFER_LOCATION
            sa.or_(
                models.OffererAddress.type.is_(None),
                models.OffererAddress.type == models.LocationType.OFFER_LOCATION,
            ),
        )
        .options(sa_orm.joinedload(models.OffererAddress.address))
        .order_by(models.OffererAddress.type.nulls_last())
        .first()
    )

    if not offerer_address:
        offerer_address = models.OffererAddress(offererId=offerer_id, addressId=address_id, label=label)
        db.session.add(offerer_address)
        db.session.flush()

    return offerer_address


def get_offerer_address(offerer_id: int, address_id: int, label: str | None = None) -> models.OffererAddress | None:
    return (
        db.session.query(models.OffererAddress)
        .filter(
            models.OffererAddress.offererId == offerer_id,
            models.OffererAddress.label == label,
            models.OffererAddress.addressId == address_id,
        )
        .options(sa_orm.joinedload(models.OffererAddress.address))
        .first()
    )


def create_offerer_address(offerer_id: int, address_id: int, label: str | None = None) -> models.OffererAddress:
    assert offerer_id
    try:
        offerer_address = models.OffererAddress(offererId=offerer_id, addressId=address_id, label=label)
        db.session.add(offerer_address)
        db.session.flush()
    except sa.exc.IntegrityError:
        db.session.rollback()
        raise (exceptions.OffererAddressCreationError())
    return offerer_address


def create_offerer_address_from_address_api(address: offerers_schemas.LocationModel) -> geography_models.Address:
    try:
        insee_code = (
            address.inseeCode
            if not address.isManualEdition
            else api_adresse.get_municipality_centroid(city=address.city, postcode=address.postalCode).citycode
        )
    except api_adresse.NoResultException:
        insee_code = None
    _ban_id = address.banId if not address.isManualEdition else None
    location_data = LocationData(
        city=address.city,
        postal_code=address.postalCode,
        latitude=float(address.latitude),
        longitude=float(address.longitude),
        street=address.street,
        insee_code=insee_code,
        ban_id=_ban_id,
    )
    return get_or_create_address(location_data, is_manual_edition=address.isManualEdition)


def get_offer_location_from_address(
    offerer_id: int, address: offerers_schemas.LocationModel
) -> offerers_models.OffererAddress:
    assert offerer_id
    if not address.label:
        address.label = None
    address_from_api = create_offerer_address_from_address_api(address)
    return get_or_create_offer_location(
        offerer_id,
        address_from_api.id,
        label=address.label,
    )


def _internal_update_fraud_info(
    *,
    offerer: offerers_models.Offerer | None = None,
    venue: offerers_models.Venue | None = None,
    confidence_level: offerers_models.OffererConfidenceLevel | None = None,
) -> dict[str, typing.Any]:
    offerer_or_venue = offerer or venue
    assert offerer_or_venue  # helps mypy

    current_confidence_level = offerer_or_venue.confidenceLevel
    is_confidence_level_changed = current_confidence_level != confidence_level
    action_kwargs: dict[str, typing.Any] = {}

    if is_confidence_level_changed:
        action_kwargs["modified_info"] = {
            "confidenceRule.confidenceLevel": {"old_info": current_confidence_level, "new_info": confidence_level}
        }

        if not current_confidence_level:
            assert confidence_level  # helps mypy
            db.session.add(
                offerers_models.OffererConfidenceRule(offerer=offerer, venue=venue, confidenceLevel=confidence_level)
            )
        else:
            assert offerer_or_venue.confidenceRule
            query = db.session.query(offerers_models.OffererConfidenceRule).filter_by(
                id=offerer_or_venue.confidenceRule.id
            )
            if not confidence_level:
                query.delete(synchronize_session=False)
            else:
                query.update({"confidenceLevel": confidence_level})

    return action_kwargs


def update_fraud_info(
    *,
    offerer: offerers_models.Offerer | None = None,
    venue: offerers_models.Venue | None = None,
    author_user: users_models.User | None = None,
    confidence_level: offerers_models.OffererConfidenceLevel | None = None,
    comment: str | None = None,
) -> bool:
    action_kwargs = _internal_update_fraud_info(offerer=offerer, venue=venue, confidence_level=confidence_level)

    if not (action_kwargs or comment):
        return False

    if comment:
        action_kwargs["comment"] = comment

    history_api.add_action(
        history_models.ActionType.FRAUD_INFO_MODIFIED, author=author_user, offerer=offerer, venue=venue, **action_kwargs
    )

    return True


def get_offer_confidence_level(
    venue: offerers_models.Venue,
) -> offerers_models.OffererConfidenceLevel | None:
    venue_confidence_level = venue.confidenceLevel
    offerer_confidence_level = venue.managingOfferer.confidenceLevel

    if offerer_confidence_level and venue_confidence_level and offerer_confidence_level != venue_confidence_level:
        logger.error(
            "Incompatible offerer rule detected",
            extra={"offerer_id": venue.managingOfferer.id, "venue_id": venue.id},
        )

    return offerer_confidence_level or venue_confidence_level


# The max number of reminders is defined with homologation team, to ensure that they can handle replies
MAX_REMINDER_EMAILS_PER_DAY = 80


def send_reminder_email_to_individual_offerers() -> None:
    offerers = (
        (
            db.session.query(offerers_models.Offerer)
            .join(
                offerers_models.IndividualOffererSubscription,
                offerers_models.IndividualOffererSubscription.offererId == offerers_models.Offerer.id,
            )
            .options(
                sa_orm.load_only(offerers_models.Offerer.id),
                sa_orm.contains_eager(offerers_models.Offerer.individualSubscription).load_only(
                    offerers_models.IndividualOffererSubscription.dateReminderEmailSent
                ),
                sa_orm.joinedload(offerers_models.Offerer.UserOfferers)
                .load_only(offerers_models.UserOfferer.userId)
                .joinedload(offerers_models.UserOfferer.user)
                .load_only(users_models.User.email),
            )
            .filter(
                offerers_models.IndividualOffererSubscription.isEmailSent.is_(True),
                offerers_models.IndividualOffererSubscription.dateEmailSent.between(
                    date.today() - timedelta(days=365),
                    date.today() - timedelta(days=31),
                ),
                sa.not_(offerers_models.IndividualOffererSubscription.isReminderEmailSent),
                sa.or_(
                    # same as for column and filter "Documents reçus"
                    offerers_models.IndividualOffererSubscription.isCriminalRecordReceived.is_(False),
                    offerers_models.IndividualOffererSubscription.isExperienceReceived.is_(False),
                ),
                offerers_models.Offerer.isPending,
            )
        )
        .order_by(offerers_models.IndividualOffererSubscription.dateEmailSent)
        .limit(MAX_REMINDER_EMAILS_PER_DAY)
        .all()
    )

    logger.info(
        "send_reminder_email_to_individual_offerers will send reminder emails to %s individual offerers", len(offerers)
    )

    for offerer in offerers:
        assert offerer.individualSubscription  # helps mypy
        offerer.individualSubscription.dateReminderEmailSent = date.today()
        transactional_mails.send_offerer_individual_subscription_reminder(offerer.UserOfferers[0].user.email)

    db.session.commit()


def update_offerer_address(offerer_address_id: int, address_id: int, label: str | None = None) -> None:
    try:
        db.session.query(offerers_models.OffererAddress).filter_by(id=offerer_address_id).update(
            {"addressId": address_id, "label": label}
        )
        db.session.flush()
    except sa.exc.IntegrityError as exc:
        # We shouldn't enp up here, but if so log the exception so we can investigate
        db.session.rollback()
        logger.exception(exc)


def synchronize_from_adage_and_check_registration(offerer_id: int) -> bool:
    since_date = date_utils.get_naive_utc_now() - timedelta(days=2)
    adage_cultural_partners = adage_api.get_cultural_partners(force_update=True, since_date=since_date)
    adage_api.synchronize_adage_ids_on_venues(adage_cultural_partners)
    return offerers_repository.offerer_has_venue_with_adage_id(offerer_id)


def synchronize_from_ds_and_check_application(offerer_id: int) -> bool:
    dms_api.import_dms_applications_for_all_eac_procedures(ignore_previous=False)
    query = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.managingOffererId == offerer_id)
        .filter(offerers_models.Venue.collectiveDmsApplications.any())
    )
    return db.session.query(query.exists()).scalar()


def is_allowed_on_adage(offerer_id: int) -> bool:
    query = (
        db.session.query(models.Offerer)
        .filter(offerers_models.Offerer.id == offerer_id)
        .filter(offerers_models.Offerer.allowedOnAdage.is_(True))
    )
    return db.session.query(query.exists()).scalar()


def find_structure_data(search_input: str) -> sirene_models.SiretInfo:
    data = api_entreprise.get_siret_open_data(search_input)

    if not data.active:
        raise offerers_exceptions.InactiveSirenException("Ce SIRET n'est pas actif.")

    return data


def find_ban_address_from_insee_address(
    diffusible: bool, insee_address: sirene_models.SireneAddress
) -> offerers_schemas.LocationModel | None:
    try:
        is_manual_address = False
        if diffusible:
            # search for precise address in BAN database
            address_to_query = f"{insee_address.street} {insee_address.postal_code} {insee_address.city}"
            ban_address = api_adresse.find_ban_address(address=address_to_query, enforce_reliability=True)
        else:
            # search for imprecise address (municipality or locality centroid) in BAN database using publicly available info
            postal_code_to_query = (  # postal_code is public info but still often masked in results
                insee_address.postal_code
                if api_entreprise.PROTECTED_DATA_PLACEHOLDER not in insee_address.postal_code
                else None
            )
            insee_code_to_query = (  # limit search with insee_code if no postal_code is available
                insee_address.insee_code
                if (
                    api_entreprise.PROTECTED_DATA_PLACEHOLDER not in insee_address.insee_code
                    and postal_code_to_query is None
                )
                else None
            )
            ban_address = api_adresse.find_ban_city(
                city=insee_address.city,
                postal_code=postal_code_to_query,
                insee_code=insee_code_to_query,
                enforce_reliability=False,
            )
            if ban_address:
                ban_address.street = geography_constants.NON_DISCLOSED_ADDRESS
                is_manual_address = True

        return (
            None
            if ban_address is None
            else offerers_schemas.LocationModel(
                isManualEdition=is_manual_address,
                banId=offerers_schemas.VenueBanId(ban_address.id) if not is_manual_address else None,
                city=offerers_schemas.VenueCity(ban_address.city),
                inseeCode=offerers_schemas.VenueInseeCode(ban_address.citycode),
                label=ban_address.label,
                latitude=ban_address.latitude,
                longitude=ban_address.longitude,
                postalCode=offerers_schemas.VenuePostalCode(ban_address.postcode),
                street=offerers_schemas.VenueAddress(ban_address.street),
            )
        )
    except api_adresse.AdresseException:
        logger.warning(
            "No BAN address found corresponding to Insee address",
            extra={
                "insee_street": insee_address.street,
                "insee_city": insee_address.city,
                "insee_postal_code": insee_address.postal_code,
                "insee_city_code": insee_address.insee_code,
            },
        )
        return None


def clean_unused_offerer_address() -> None:
    offerer_address_usage = db.session.query(
        offerers_models.OffererAddress.id.label("offerer_address_id"),
        sa.or_(
            sa.and_(
                offerers_models.OffererAddress.type == offerers_models.LocationType.VENUE_LOCATION,
                offerers_models.OffererAddress.venueId.is_not(None),
            ),
            sa.select(1)
            .where(educational_models.CollectiveOffer.offererAddressId == offerers_models.OffererAddress.id)
            .exists(),
            sa.select(1)
            .where(educational_models.CollectiveOfferTemplate.offererAddressId == offerers_models.OffererAddress.id)
            .exists(),
            sa.select(1).where(offers_models.Offer.offererAddressId == offerers_models.OffererAddress.id).exists(),
        ).label("is_used"),
    ).cte()

    count = (
        db.session.query(offerers_models.OffererAddress)
        .filter(
            offerers_models.OffererAddress.id.in_(
                sa.select(offerer_address_usage.c.offerer_address_id)
                .select_from(offerer_address_usage)
                .filter(offerer_address_usage.c.is_used.is_(False))
                .scalar_subquery()
            )
        )
        .delete(synchronize_session=False)
    )

    logger.info("%s unused rows to delete in offerer_address", count)
