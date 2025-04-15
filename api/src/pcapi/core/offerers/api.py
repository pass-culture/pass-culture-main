import dataclasses
from datetime import date
from datetime import datetime
from datetime import timedelta
import decimal
import functools
import itertools
import logging
from math import ceil
import re
import secrets
import time
import typing

from flask_sqlalchemy import BaseQuery
import jwt
from psycopg2.extras import NumericRange
import pytz
import schwifty
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INTERVAL
import sqlalchemy.orm as sa_orm

from pcapi import settings
from pcapi.connectors import api_adresse
from pcapi.connectors import virustotal
import pcapi.connectors.acceslibre as accessibility_provider
from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.connectors.entreprise import models as sirene_models
from pcapi.connectors.entreprise import sirene
import pcapi.connectors.thumb_storage as storage
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
import pcapi.core.educational.api.adage as adage_api
import pcapi.core.educational.api.address as educational_address_api
from pcapi.core.external import zendesk_sell
from pcapi.core.external.attributes import api as external_attributes_api
import pcapi.core.finance.models as finance_models
from pcapi.core.geography import models as geography_models
import pcapi.core.history.api as history_api
import pcapi.core.history.models as history_models
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.offerers import constants as offerers_constants
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.models as providers_models
from pcapi.core.users import repository as users_repository
import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.models import feature
from pcapi.models import pc_object
from pcapi.models.feature import FeatureToggle
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.repository import atomic
from pcapi.repository import is_managed_transaction
from pcapi.repository import mark_transaction_as_invalid
from pcapi.repository import on_commit
from pcapi.repository import repository
from pcapi.repository import transaction
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
import pcapi.routes.serialization.base as serialize_base
from pcapi.routes.serialization.offerers_serialize import OffererMemberStatus
from pcapi.utils import crypto
from pcapi.utils import human_ids
from pcapi.utils import image_conversion
from pcapi.utils import regions as utils_regions
from pcapi.utils import siren as siren_utils
from pcapi.utils.clean_accents import clean_accents
import pcapi.utils.date as date_utils
import pcapi.utils.db as db_utils
import pcapi.utils.email as email_utils
from pcapi.workers.match_acceslibre_job import match_acceslibre_job

from . import exceptions
from . import models
from . import repository as offerers_repository
from . import schemas as offerers_schemas
from . import validation


logger = logging.getLogger(__name__)

# List of fields of `Venue` which, when changed, must trigger a
# reindexation of offers.
VENUE_ALGOLIA_INDEXED_FIELDS = ["name", "publicName", "postalCode", "city", "latitude", "longitude"]
API_KEY_SEPARATOR = "_"
APE_TAG_MAPPING = {"84.11Z": "Collectivité"}
DMS_TOKEN_REGEX = r"^(?:PRO-)?([a-fA-F0-9]{12})$"


def update_venue(
    venue: models.Venue,
    modifications: dict,
    location_modifications: dict,
    author: users_models.User,
    *,
    opening_hours: list[serialize_base.OpeningHoursModel] | None = None,
    contact_data: offerers_schemas.VenueContactModel | None = None,
    criteria: list[criteria_models.Criterion] | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    external_accessibility_url: str | None | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    is_manual_edition: bool = False,
) -> models.Venue:
    new_open_to_public = not venue.isOpenToPublic and modifications.get("isOpenToPublic")

    # TODO: (pcharlet 2025-04-02) Remove the next 5 lines when regularisation is done.
    # We need consistent informations between isPermanent and isOpenToPublic during regularisation. isPermanent will be removed.
    not_permanent_anymore = venue.isPermanent and modifications.get("isPermanent") is False
    if new_open_to_public and not venue.isPermanent:
        modifications["isPermanent"] = True
    elif not_permanent_anymore and venue.isOpenToPublic:
        modifications["isOpenToPublic"] = False

    has_address_changed = (
        modifications.get("banId", offerers_constants.UNCHANGED) is not offerers_constants.UNCHANGED
        or modifications.get("postalCode", offerers_constants.UNCHANGED) is not offerers_constants.UNCHANGED
        or modifications.get("street", offerers_constants.UNCHANGED) is not offerers_constants.UNCHANGED
    )
    venue_snapshot = history_api.ObjectUpdateSnapshot(venue, author)
    if not venue.isVirtual:
        assert venue.offererAddress is not None  # helps mypy
        assert venue.offererAddress.address is not None  # helps mypy
        is_venue_location_updated = any(
            field in location_modifications
            for field in (
                "street",
                "city",
                "postalCode",
                "latitude",
                "longitude",
            )
        )
        is_manual_edition_updated = is_venue_location_updated and (
            is_manual_edition != venue.offererAddress.address.isManualEdition
        )

        old_oa = venue.offererAddress
        new_oa = models.OffererAddress(offerer=venue.managingOfferer)
        if is_venue_location_updated:
            update_venue_location(
                venue,
                modifications,
                location_modifications,
                venue_snapshot=venue_snapshot,
                new_oa=new_oa,
                is_manual_edition=is_manual_edition,
            )
        elif is_manual_edition_updated:
            duplicate_oa(
                venue=venue,
                old_oa=old_oa,
                new_oa=new_oa,
                is_manual_edition=is_manual_edition,
                venue_snapshot=venue_snapshot,
            )
        if is_manual_edition_updated or is_venue_location_updated:
            switch_old_oa_label(old_oa=old_oa, label=venue.common_name, venue_snapshot=venue_snapshot)

    if contact_data:
        # target must not be None, otherwise contact_data fields will be compared to fields in Venue, which do not exist
        target = venue.contact if venue.contact is not None else offerers_models.VenueContact()
        venue_snapshot.trace_update(contact_data.dict(), target=target, field_name_template="contact.{}")
        upsert_venue_contact(venue, contact_data)

    for daily_opening_hours in opening_hours or []:
        weekday = models.Weekday(daily_opening_hours.weekday)
        target = get_venue_opening_hours_by_weekday(venue, weekday)
        target.timespan = date_utils.numranges_to_readble_str(target.timespan)
        opening_hours_readable = {
            "weekday": daily_opening_hours.weekday,
            "timespan": date_utils.numranges_to_readble_str(daily_opening_hours.timespan),
        }
        venue_snapshot.trace_update(
            opening_hours_readable,
            target=target,
            field_name_template=f"openingHours.{daily_opening_hours.weekday}.{{}}",
        )
        upsert_venue_opening_hours(venue, daily_opening_hours)

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
            setattr(venue, key, value)
    elif venue_snapshot.is_empty:
        return venue

    venue_snapshot.add_action()

    # keep commit with repository.save() as long as venue is validated in pcapi.validation.models.venue
    repository.save(venue)

    if modifications:
        on_commit(
            functools.partial(
                search.async_index_venue_ids,
                [venue.id],
                reason=search.IndexationReason.VENUE_UPDATE,
                log_extra={"changes": set(modifications.keys())},
            )
        )

        indexing_modifications_fields = set(modifications.keys()) & set(VENUE_ALGOLIA_INDEXED_FIELDS)
        if indexing_modifications_fields:
            on_commit(
                functools.partial(
                    search.async_index_offers_of_venue_ids,
                    [venue.id],
                    reason=search.IndexationReason.VENUE_UPDATE,
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

    if new_open_to_public or has_address_changed:
        match_acceslibre_job.delay(venue.id)

    if not_open_to_public_anymore:
        delete_venue_accessibility_provider(venue)

    return venue


def update_venue_location(  # pylint: disable=too-many-positional-arguments
    venue: models.Venue,
    modifications: dict,
    location_modifications: dict,
    venue_snapshot: history_api.ObjectUpdateSnapshot,
    new_oa: models.OffererAddress,
    is_manual_edition: bool = False,
) -> None:
    """
    Update the venue location and also populate the newly created Address & OffererAddress.
    You might want to skip the API Adresse call and force the location update with incoming data.
    If we receive untrusted user input, we want to double check data consistency using the API Adresse.
    On the other side, BO users might want to force a location to a venue, for example if the address is unknown
    for the API.
    """
    assert venue.offererAddress is not None
    # When street is cleared from the BO, location_modifications contains: {'street': None}
    street = location_modifications.get("street", venue.offererAddress.address.street)
    city = location_modifications.get("city", venue.offererAddress.address.city)
    postal_code = location_modifications.get("postalCode", venue.offererAddress.address.postalCode)
    latitude = location_modifications.get("latitude", venue.offererAddress.address.latitude)
    longitude = location_modifications.get("longitude", venue.offererAddress.address.longitude)
    ban_id = location_modifications.get("banId", venue.offererAddress.address.banId)
    logger.info(
        "Updating venue location",
        extra={"venue_id": venue.id, "venue_street": street, "venue_city": city, "venue_postalCode": postal_code},
    )

    if not is_manual_edition:
        address_info = api_adresse.get_address(address=street, postcode=postal_code, city=city)
        location_data = LocationData(
            city=address_info.city,
            postal_code=address_info.postcode,
            latitude=address_info.latitude,
            longitude=address_info.longitude,
            street=address_info.street,
            insee_code=address_info.citycode,
            ban_id=address_info.id,
        )
    else:
        insee_code = None
        if city and postal_code:
            # Address entered manually does not provide INSEE code, find it
            try:
                insee_code = api_adresse.get_municipality_centroid(city, postal_code).citycode
            except api_adresse.AdresseException:
                pass

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

    new_oa.address = address
    db.session.add(new_oa)
    db.session.flush()  # flush to get the new_oa.id
    target = venue.offererAddress.address
    old_oa = venue.offererAddress
    venue_snapshot.trace_update(snapshot_location_data, target=target, field_name_template="offererAddress.address.{}")
    venue_snapshot.trace_update(
        {"id": new_oa.id, "addressId": new_oa.addressId, "label": new_oa.label},
        old_oa,
        "offererAddress.{}",
    )
    venue.offererAddress = new_oa
    db.session.add(venue)
    db.session.flush()

    if modifications.get("street"):
        modifications["street"] = address.street
    if modifications.get("city"):
        modifications["city"] = address.city
    if modifications.get("postalCode"):
        modifications["postalCode"] = address.postalCode
    if modifications.get("latitude"):
        modifications["latitude"] = address.latitude
    if modifications.get("longitude"):
        modifications["longitude"] = address.longitude


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

    repository.save(venue_contact)
    return venue


def upsert_venue_opening_hours(venue: models.Venue, opening_hours: serialize_base.OpeningHoursModel) -> models.Venue:
    """
    Create and attach OpeningHours for a given weekday to a Venue if it has none.
    Update (replace) an existing OpeningHours list otherwise.
    """
    weekday = models.Weekday(opening_hours.weekday)
    venue_opening_hours = get_venue_opening_hours_by_weekday(venue, weekday)

    modifications = {
        field: value
        for field, value in opening_hours.dict().items()
        if venue_opening_hours.field_exists_and_has_changed(field, value)
    }
    if not modifications:
        return venue
    venue_opening_hours.venue = venue
    venue_opening_hours.timespan = opening_hours.timespan
    repository.save(venue_opening_hours)
    return venue


def create_venue(venue_data: venues_serialize.PostVenueBodyModel, author: users_models.User) -> models.Venue:
    venue = models.Venue()
    address = venue_data.address

    if utils_regions.NON_DIFFUSIBLE_TAG in address.street:
        address_info = api_adresse.get_municipality_centroid(address.city, address.postalCode)
        address_info.street = utils_regions.NON_DIFFUSIBLE_TAG
        address = get_or_create_address(
            LocationData(
                city=address_info.city,
                postal_code=address_info.postcode,
                latitude=address_info.latitude,
                longitude=address_info.longitude,
                street=address_info.street,
                insee_code=address_info.citycode,
                ban_id=address_info.id,
            )
        )
        offerer_address = create_offerer_address(venue_data.managingOffererId, address.id)
    else:
        offerer_address = get_offerer_address_from_address(venue_data.managingOffererId, address)

    venue.offererAddressId = offerer_address.id

    data = venue_data.dict(by_alias=True)
    data["dmsToken"] = generate_dms_token()
    if venue.is_soft_deleted():
        raise pc_object.DeletedRecordException()
    for key, value in data.items():
        if key == "contact":
            continue
        setattr(venue, key, value)

    # FIXME (dramelet, 05-12-2024) Until those columns are dropped
    # we still have to maintain the historic behavior
    venue.street = data["address"]["street"]  # type: ignore [method-assign]
    venue.city = data["address"]["city"]
    venue.postalCode = data["address"]["postalCode"]
    venue.latitude = data["address"]["latitude"]
    venue.longitude = data["address"]["longitude"]
    venue.banId = data["address"]["banId"]

    if venue_data.contact:
        upsert_venue_contact(venue, venue_data.contact)

    if settings.IS_INTEGRATION:
        # Always enable collective features for new venues in integration
        # Update managing offerer now and not when it is created to avoid
        # some environment specific code spread here and there.
        offerer = offerers_models.Offerer.query.get(venue.managingOffererId)
        if offerer:
            # if no offerer is found, venue won't be saved because of invalid
            # foreign key id. No need to handle this here, let it fail later.
            offerer.allowedOnAdage = True
        venue.adageId = str(int(time.time()))
        venue.adageInscriptionDate = datetime.utcnow()

    adage_venue_address = educational_address_api.new_venue_address(venue)

    history_api.add_action(history_models.ActionType.VENUE_CREATED, author=author, venue=venue)

    db.session.add_all([venue, adage_venue_address])
    db.session.flush()

    if venue.siret:
        link_venue_to_pricing_point(venue, pricing_point_id=venue.id)
    if FeatureToggle.WIP_IS_OPEN_TO_PUBLIC.is_active() and (venue.siret or venue.isOpenToPublic):
        venue.isPermanent = True

    on_commit(
        functools.partial(search.async_index_venue_ids, [venue.id], reason=search.IndexationReason.VENUE_CREATION)
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
        # Additional checks to allow removing a venue which is only a former pricing point for other venues but has
        # never been used for pricing, so that support team can handle misconfiguration by an offerer.
        venue_used_as_current_pricing_point = db.session.query(
            offerers_models.VenuePricingPointLink.query.filter(
                offerers_models.VenuePricingPointLink.venueId != venue_id,
                offerers_models.VenuePricingPointLink.pricingPointId == venue_id,
                offerers_models.VenuePricingPointLink.timespan.contains(datetime.utcnow()),
            ).exists()
        ).scalar()

        if venue_used_as_current_pricing_point:
            raise exceptions.CannotDeleteVenueUsedAsPricingPointException()

        pricing_point_has_pricings = db.session.query(
            finance_models.Pricing.query.filter(finance_models.Pricing.pricingPointId == venue_id).exists()
        ).scalar()

        if pricing_point_has_pricings:
            raise exceptions.CannotDeleteVenueUsedAsPricingPointException()

        offerers_models.VenuePricingPointLink.query.filter(
            offerers_models.VenuePricingPointLink.venueId != venue_id,
            offerers_models.VenuePricingPointLink.pricingPointId == venue_id,
        ).delete(synchronize_session=False)

    venue_associated_with_reimbursement_rule = db.session.query(
        finance_models.CustomReimbursementRule.query.filter(
            finance_models.CustomReimbursementRule.venueId == venue_id
        ).exists()
    ).scalar()
    if venue_associated_with_reimbursement_rule:
        raise exceptions.CannotDeleteVenueWithActiveOrFutureCustomReimbursementRule()

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

    offerers_models.Venue.query.filter(offerers_models.Venue.id == venue_id).delete(synchronize_session=False)

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
        offers_models.OfferReport.query.filter(offers_models.OfferReport.offerId.in_(offers_id_chunk)).delete(
            synchronize_session=False
        )
    offers_models.Offer.query.filter(offers_models.Offer.venueId == venue_id).delete(synchronize_session=False)

    # delete all things providers related
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
        educational_models.CollectiveOfferRequest.query.filter(
            educational_models.CollectiveOfferRequest.collectiveOfferTemplateId.in_(collective_offer_templates_id_chunk)
        ).delete(synchronize_session=False)

    educational_models.CollectivePlaylist.query.filter(
        sa.or_(
            educational_models.CollectivePlaylist.venueId == venue_id,
            educational_models.CollectivePlaylist.collectiveOfferTemplateId.in_(
                db.session.query(educational_models.CollectiveOfferTemplate.id).filter(
                    educational_models.CollectiveOfferTemplate.venueId == venue_id
                )
            ),
        )
    ).delete(synchronize_session=False)
    educational_models.CollectiveOfferTemplate.query.filter(
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
            "updated_finance_events": ppoint_update_result.rowcount,
        },
    )


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
    key = models.ApiKey(offererId=offerer_id, prefix=prefix, secret=crypto.hash_public_api_key(clear_secret))

    return key, f"{prefix}{API_KEY_SEPARATOR}{clear_secret}"


def generate_provider_api_key(provider: providers_models.Provider) -> tuple[models.ApiKey, str]:
    offerer = provider.offererProvider.offerer if provider.offererProvider else None
    if offerer is None:
        raise exceptions.CannotFindProviderOfferer()

    clear_secret = secrets.token_hex(32)
    prefix = _generate_api_key_prefix()
    key = models.ApiKey(
        offerer=offerer, provider=provider, prefix=prefix, secret=crypto.hash_public_api_key(clear_secret)
    )

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

    if not users_repository.has_access(user, api_key.offererId):
        raise exceptions.ApiKeyDeletionDenied()

    db.session.delete(api_key)


def _fill_in_offerer(
    offerer: offerers_models.Offerer, offerer_informations: offerers_serialize.CreateOffererQueryModel
) -> None:
    offerer.street = offerer_informations.street  # type: ignore[method-assign]
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
    offerer: offerers_models.Offerer, siren_info: sirene_models.SirenInfo | None, user: users_models.User
) -> None:
    tag_names_to_apply = set()

    if siren_info:
        if siren_info.ape_code:
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
        # The user can have his attachment rejected or deleted to the offerer,
        # in this case it is passed to NEW if the offerer is not rejected
        user_offerer = offerers_models.UserOfferer.query.filter_by(userId=user.id, offererId=offerer.id).one_or_none()
        if not user_offerer:
            user_offerer = models.UserOfferer(offerer=offerer, user=user, validationStatus=ValidationStatus.NEW)
            db.session.add(user_offerer)
            db.session.flush()

        if offerer.isRejected:
            # When offerer was rejected, it is considered as a new offerer in validation process;
            # history is kept with same id and siren
            is_new = True
            _fill_in_offerer(offerer, offerer_informations)
            comment = (comment + "\n" if comment else "") + "Nouvelle demande sur un SIREN précédemment rejeté"
            user_offerer.validationStatus = ValidationStatus.VALIDATED
        elif not user_offerer.isValidated:
            user_offerer.validationStatus = ValidationStatus.NEW
            user_offerer.dateCreated = datetime.utcnow()
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
        _fill_in_offerer(offerer, offerer_informations)
        user_offerer = grant_user_offerer_access(offerer, user)
        db.session.add_all([offerer, user_offerer])
        db.session.flush()

    if is_new:
        assert offerer.siren  # helps mypy until Offerer.siren is set as NOT NULL
        try:
            siren_info = sirene.get_siren(offerer.siren, raise_if_non_public=False)
        except sirene_exceptions.SireneException as exc:
            logger.info("Could not fetch info from Sirene API", extra={"exc": exc})
            siren_info = None

        auto_tag_new_offerer(offerer, siren_info, user)

        extra_data = {}
        if siren_info:
            extra_data = {"sirene_info": dict(siren_info)}
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

    # keep commit with repository.save() as long as siren is validated in pcapi.validation.models.offerer
    repository.save(offerer)

    if FeatureToggle.WIP_2025_SIGN_UP.is_active() and offerer_informations.phoneNumber:
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
        models.UserOfferer.query.join(models.UserOfferer.offerer)
        .filter(models.UserOfferer.user == user, models.Offerer.siren == siren)
        .exists()
    ).scalar()


def _format_tags(tags: typing.Iterable[models.OffererTag]) -> str:
    return ", ".join(sorted(tag.label for tag in tags))


def update_offerer(
    offerer: models.Offerer,
    author: users_models.User,
    *,
    name: str | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    city: str | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    postal_code: str | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    street: str | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
    tags: list[models.OffererTag] | offerers_constants.T_UNCHANGED = offerers_constants.UNCHANGED,
) -> None:
    modified_info: dict[str, dict[str, str | None]] = {}

    if name is not offerers_constants.UNCHANGED and offerer.name != name:
        modified_info["name"] = {"old_info": offerer.name, "new_info": name}
        offerer.name = name
    if city is not offerers_constants.UNCHANGED and offerer.city != city:
        modified_info["city"] = {"old_info": offerer.city, "new_info": city}
        offerer.city = city
    if postal_code is not offerers_constants.UNCHANGED and offerer.postalCode != postal_code:
        modified_info["postalCode"] = {"old_info": offerer.postalCode, "new_info": postal_code}
        offerer.postalCode = postal_code
    if street is not offerers_constants.UNCHANGED and offerer.street != street:
        modified_info["street"] = {"old_info": offerer.street, "new_info": street}
        offerer.street = street  # type: ignore[method-assign]
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

    # keep commit with repository.save() as long as postal code is validated in pcapi.validation.models.offerer
    repository.save(offerer)

    _update_external_offerer(offerer)


def remove_pro_role_and_add_non_attached_pro_role(users: list[users_models.User]) -> None:
    users_with_offerers = (
        users_models.User.query.filter(users_models.User.id.in_([user.id for user in users]))
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

    on_commit(
        functools.partial(
            external_attributes_api.update_external_pro,
            user_offerer.user.email,
        ),
    )

    transactional_mails.send_offerer_attachment_validation_email_to_pro(user_offerer)

    offerer_invitation = (
        models.OffererInvitation.query.filter_by(offererId=user_offerer.offererId)
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
    author_user: users_models.User,
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
    offerer.dateValidated = datetime.utcnow()
    offerer.isActive = True
    db.session.add(offerer)

    for applicant in applicants:
        applicant.add_pro_role()
    db.session.add_all(applicants)

    if review_all_offers:
        action_args |= _internal_update_fraud_info(
            offerer=offerer, confidence_level=offerers_models.OffererConfidenceLevel.MANUAL_REVIEW
        )

    history_api.add_action(
        history_models.ActionType.OFFERER_VALIDATED,
        author=author_user,
        offerer=offerer,
        user=applicants[0] if applicants else None,  # before validation we should have only one applicant
        **action_args,
    )

    db.session.flush()

    _update_external_offerer(offerer, index_with_reason=search.IndexationReason.OFFERER_VALIDATION)

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

    users_offerer = offerers_models.UserOfferer.query.filter_by(offererId=offerer.id).all()
    for user_offerer in users_offerer:
        reject_offerer_attachment(
            user_offerer,
            author_user,
            "Compte pro rejeté suite au rejet de l'entité juridique",
            send_email=(user_offerer.user not in applicants),  # do not send a second email
        )

    remove_pro_role_and_add_non_attached_pro_role(applicants)

    # Remove any API key which could have been created when user was waiting for validation
    models.ApiKey.query.filter(models.ApiKey.offererId == offerer.id).delete()

    db.session.flush()

    if was_validated:
        _update_external_offerer(offerer, index_with_reason=search.IndexationReason.OFFERER_DEACTIVATION)


# We do not want to cancel bookings on events which took place on the last 3 days, because they automatically become
# USED after AUTO_USE_AFTER_EVENT_TIME_DELAY (+ one day margin because marking as used is a daily cron).
USED_EVENT_DELAY = bookings_constants.AUTO_USE_AFTER_EVENT_TIME_DELAY + timedelta(days=1)


def close_offerer(
    offerer: offerers_models.Offerer,
    closure_date: date | None,
    author_user: users_models.User | None,
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
        transactional_mails.send_offerer_closed_email_to_pro(offerer, closure_date)

    db.session.flush()

    author_id = author_user.id if author_user else None

    _cancel_individual_bookings_on_offerer_closure(offerer.id, author_id)
    _cancel_collective_bookings_on_offerer_closure(offerer.id, author_id)

    if was_validated:
        _update_external_offerer(offerer, index_with_reason=search.IndexationReason.OFFERER_DEACTIVATION)


def _cancel_individual_bookings_on_offerer_closure(offerer_id: int, author_id: int | None) -> None:
    now = datetime.utcnow()
    event_subcategory_ids = subcategories.EVENT_SUBCATEGORIES.keys()

    ongoing_bookings = (
        bookings_models.Booking.query.filter(
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

    for booking in ongoing_bookings:
        if booking.stock.offer.subcategoryId in event_subcategory_ids and (
            now - USED_EVENT_DELAY <= booking.stock.beginningDatetime <= now
        ):
            # Do not cancel booking which will become USED in auto_mark_as_used_after_event()
            logger.info(
                "Event booking not cancelled when closing offerer",
                extra={"booking_id": booking.id, "offerer_id": offerer_id},
            )
            continue
        with atomic():
            try:
                bookings_api.cancel_booking_on_closed_offerer(booking, author_id=author_id)
            except Exception as exc:  # pylint: disable=broad-except
                mark_transaction_as_invalid()
                logger.exception(
                    "Failed to cancel booking when closing offerer",
                    extra={"exc": exc, "booking_id": booking.id, "offerer_id": offerer_id},
                )

    db.session.flush()


def _cancel_collective_bookings_on_offerer_closure(offerer_id: int, author_id: int | None) -> None:
    now = datetime.utcnow()

    ongoing_collective_bookings = (
        educational_models.CollectiveBooking.query.filter(
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

    for collective_booking in ongoing_collective_bookings:
        if collective_booking.status == educational_models.CollectiveBookingStatus.CONFIRMED and (
            now - USED_EVENT_DELAY <= collective_booking.collectiveStock.endDatetime <= now
        ):
            # Do not cancel booking which will become USED in auto_mark_as_used_after_event()
            logger.info(
                "Collective booking not cancelled when closing offerer",
                extra={"collective_booking_id": collective_booking.id, "offerer_id": offerer_id},
            )
            continue
        try:
            educational_booking_api.cancel_collective_booking(
                collective_booking,
                educational_models.CollectiveBookingCancellationReasons.OFFERER_CLOSED,
                author_id=author_id,
            )
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                "Failed to cancel collective booking when closing offerer",
                extra={"exc": exc, "collective_booking_id": collective_booking.id, "offerer_id": offerer_id},
            )

    db.session.flush()


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
        comment=comment,
        **extra_data,
    )

    db.session.flush()

    if was_validated:  # in case it was validated by mistake, then moved to PENDING state again
        _update_external_offerer(offerer, index_with_reason=search.IndexationReason.OFFERER_DEACTIVATION)


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
    timestamp = get_timestamp_from_url(venue.bannerUrl) if "_" in venue.bannerUrl else ""
    storage.remove_thumb(venue, storage_id_suffix=str(timestamp), ignore_thumb_count=True)

    # some older venues might have a banner but not the original file
    # note: if bannerUrl is not None, bannerMeta should not be either.
    assert venue.bannerMeta is not None
    if original_image_url := venue.bannerMeta.get("original_image_url"):
        original_image_timestamp = get_timestamp_from_url(original_image_url)
        storage.remove_thumb(venue, storage_id_suffix=original_image_timestamp)

    venue.bannerUrl = None  # type: ignore[method-assign]
    venue.bannerMeta = None  # type: ignore[method-assign]
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

    venue.bannerUrl = f"{venue.thumbUrl}_{banner_timestamp}"  # type: ignore[method-assign]
    venue.bannerMeta = {  # type: ignore[method-assign]
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


def can_offerer_create_educational_offer(offerer_id: int) -> bool:
    import pcapi.core.educational.adage_backends as adage_client

    if settings.CAN_COLLECTIVE_OFFERER_IGNORE_ADAGE:
        return True

    if offerers_repository.offerer_has_venue_with_adage_id(offerer_id):
        return True

    siren = offerers_repository.find_siren_by_offerer_id(offerer_id)
    try:
        response = adage_client.get_adage_offerer(siren)
        return len(response) != 0
    except educational_exceptions.CulturalPartnerNotFoundException:
        return False


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
            .options(sa_orm.joinedload(models.Offerer.managedVenues))
            .all()
        )
    else:
        offerers = (
            offerers_repository.get_all_offerers_for_user(
                user=current_user,
                validated=True,
            )
            .options(sa_orm.joinedload(models.Offerer.managedVenues))
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
        offers_models.Stock.query.join(offers_models.Offer)
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


def get_venue_by_id(venue_id: int) -> offerers_models.Venue:
    return offerers_repository.get_venue_by_id(venue_id)


def search_offerer(search_query: str, departments: typing.Iterable[str] = ()) -> BaseQuery:
    offerers = models.Offerer.query

    search_query = search_query.strip()
    if not search_query:
        return offerers.filter(False)

    if departments:
        offerers = offerers.filter(models.Offerer.departementCode.in_(departments))  # type: ignore[attr-defined]

    if search_query.isnumeric():
        numeric_filter = models.Offerer.id == int(search_query)
        if len(search_query) == siren_utils.SIREN_LENGTH:
            numeric_filter = sa.or_(numeric_filter, models.Offerer.siren == search_query)
        elif len(search_query) == siren_utils.RID7_LENGTH:
            numeric_filter = sa.or_(numeric_filter, models.Offerer.siren == siren_utils.rid7_to_siren(search_query))
        offerers = offerers.filter(numeric_filter)
    else:
        search_words = f'%{clean_accents(search_query).replace(" ", "%").replace("-", "%")}%'
        offerers = offerers.filter(sa.func.immutable_unaccent(offerers_models.Offerer.name).ilike(search_words))

        # Always order by similarity when searching by name
        offerers = offerers.order_by(sa.desc(sa.func.similarity(models.Offerer.name, search_query)))

    # At the end, order by id, in case of equal similarity score
    offerers = offerers.order_by(models.Offerer.id)

    return offerers


def get_offerer_base_query(offerer_id: int) -> BaseQuery:
    return models.Offerer.query.filter(models.Offerer.id == offerer_id)


def search_venue(search_query: str, departments: typing.Iterable[str] = ()) -> BaseQuery:
    venues = models.Venue.query.outerjoin(models.VenueContact).options(
        sa_orm.joinedload(models.Venue.contact),
        sa_orm.joinedload(models.Venue.managingOfferer),
    )

    search_query = search_query.strip()
    if not search_query:
        return venues.filter(False)

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
            search_words = f'%{clean_accents(search_query).replace(" ", "%").replace("-", "%")}%'
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


def get_venue_base_query(venue_id: int) -> BaseQuery:
    return models.Venue.query.outerjoin(offerers_models.VenueContact).filter(models.Venue.id == venue_id)


def get_bank_account_base_query(bank_account_id: int) -> BaseQuery:
    return finance_models.BankAccount.filter(finance_models.BankAccount.id == bank_account_id)


def search_bank_account(search_query: str, *_: typing.Any) -> BaseQuery:
    bank_accounts_query = finance_models.BankAccount.query.options(
        sa_orm.joinedload(finance_models.BankAccount.offerer)
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

    if re.match(r"^[AF]\d{9}$", search_query):
        bank_accounts_query = bank_accounts_query.join(finance_models.Invoice)
        filters.append(finance_models.Invoice.reference == search_query)

    if not filters:
        return bank_accounts_query.filter(False)

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


def get_offerer_offers_stats(offerer_id: int, max_offer_count: int = 0) -> dict:
    def _get_query(offer_class: type[offers_api.AnyOffer]) -> BaseQuery:
        return sa.select(sa.func.jsonb_object_agg(sa.text("status"), sa.text("number"))).select_from(
            sa.select(
                sa.case(
                    (sa.and_(offer_class.isActive, sa.not_(offer_class.is_expired)), "active"),
                    else_="inactive",
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
                        offer_class.isActive,
                        offer_class.validation == offers_models.OfferValidationStatus.APPROVED.value,
                    ),
                    sa.and_(
                        sa.not_(offer_class.isActive),
                        offer_class.validation.in_(  # type: ignore[attr-defined]
                            [
                                offers_models.OfferValidationStatus.APPROVED.value,
                                offers_models.OfferValidationStatus.PENDING.value,
                                offers_models.OfferValidationStatus.DRAFT.value,
                            ]
                        ),
                    ),
                ),
            )
            .group_by("status")
            .subquery()
        )

    def _max_count_query(offer_class: type[offers_api.AnyOffer]) -> BaseQuery:
        return sa.select(sa.func.count(sa.text("offer_id"))).select_from(
            sa.select(offer_class.id.label("offer_id"))
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
                    (sa.and_(offer_class.isActive, sa.not_(offer_class.is_expired)), "active"),
                    else_="inactive",
                ).label("status"),
                sa.func.count(offer_class.id).label("number"),
            )
            .select_from(offerers_models.Venue)
            .outerjoin(offer_class)
            .filter(
                # TODO: remove filter on isActive when all DRAFT and PENDING collective_offers are effectively at isActive = False
                sa.or_(
                    sa.and_(
                        offer_class.isActive,
                        offer_class.venueId == venue_id,
                        offer_class.validation == offers_models.OfferValidationStatus.APPROVED.value,
                    ),
                    sa.and_(
                        sa.not_(offer_class.isActive),
                        offer_class.venueId == venue_id,
                        offer_class.validation.in_(  # type: ignore[attr-defined]
                            [
                                offers_models.OfferValidationStatus.APPROVED.value,
                                offers_models.OfferValidationStatus.PENDING.value,
                                offers_models.OfferValidationStatus.DRAFT.value,
                            ]
                        ),
                    ),
                ),
            )
            .group_by("status")
            .subquery()
        )

    def _max_count_query(offer_class: type[offers_api.AnyOffer]) -> BaseQuery:
        return sa.select(sa.func.count(sa.text("offer_id"))).select_from(
            sa.select(offer_class.id.label("offer_id"))
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
        # dashboard (e.g. to export content).
        "exp": round(time.time()) + (60 * 10),
    }
    token = jwt.encode(payload, settings.METABASE_SECRET_KEY, algorithm="HS256")
    return f"{settings.METABASE_SITE_URL}/embed/dashboard/{token}#bordered=false&titled=false"


def create_venue_registration(venue_id: int, target: offerers_models.Target, web_presence: str | None) -> None:
    venue_registration = offerers_models.VenueRegistration(venueId=venue_id, target=target, webPresence=web_presence)
    repository.save(venue_registration)

    if web_presence:
        for url in web_presence.split(", "):
            virustotal.request_url_scan(url, skip_if_recent_scan=True)


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
        street=onboarding_data.address.street,
        city=onboarding_data.address.city,
        latitude=float(onboarding_data.address.latitude),
        longitude=float(onboarding_data.address.longitude),
        name=name,
        postalCode=onboarding_data.address.postalCode,
        siren=onboarding_data.siret[:9],
        phoneNumber=onboarding_data.phoneNumber,
    )
    new_onboarding_info = NewOnboardingInfo(
        target=onboarding_data.target,
        venueTypeCode=onboarding_data.venueTypeCode,
        webPresence=onboarding_data.webPresence,
    )
    user_offerer = create_offerer(user, offerer_creation_info, new_onboarding_info)

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
            address=address,
            bookingEmail=user.email,
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

    _update_external_offerer(offerer, index_with_reason=search.IndexationReason.OFFERER_DEACTIVATION)


def unsuspend_offerer(offerer: models.Offerer, actor: users_models.User, comment: str | None) -> None:
    if offerer.isActive:
        return

    offerer.isActive = True
    db.session.add(offerer)
    history_api.add_action(
        history_models.ActionType.OFFERER_UNSUSPENDED, author=actor, offerer=offerer, comment=comment
    )
    db.session.flush()

    _update_external_offerer(offerer, index_with_reason=search.IndexationReason.OFFERER_ACTIVATION)


def _update_external_offerer(
    offerer: models.Offerer, *, index_with_reason: search.IndexationReason | None = None
) -> None:
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
            {i for i, in packed_collective_ids},
            reason=index_with_reason,
        )
    )


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

    offerer_associated_with_reimbursement_rule = db.session.query(
        finance_models.CustomReimbursementRule.query.outerjoin(finance_models.CustomReimbursementRule.venue)
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

    venue_ids_query = offerers_models.Venue.query.filter_by(managingOffererId=offerer_id).with_entities(
        offerers_models.Venue.id
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

    offerers_models.VenuePricingPointLink.query.filter(
        offerers_models.VenuePricingPointLink.venueId.in_(venue_ids)
        | offerers_models.VenuePricingPointLink.pricingPointId.in_(venue_ids),
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

    offerers_models.Offerer.query.filter(offerers_models.Offerer.id == offerer_id).delete(synchronize_session=False)

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
        models.OffererInvitation.query.filter(models.OffererInvitation.offererId == offerer.id)
        .filter(models.OffererInvitation.email == email)
        .one_or_none()
    )

    if existing_invited_email:  # already invited
        raise exceptions.EmailAlreadyInvitedException()

    existing_user = (
        users_models.User.query.filter(users_models.User.email == email)
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


def get_offerer_members(offerer: models.Offerer) -> list[tuple[str, OffererMemberStatus]]:
    users_offerers = (
        models.UserOfferer.query.filter(
            models.UserOfferer.offererId == offerer.id,
            sa.not_(models.UserOfferer.isRejected),
            sa.not_(models.UserOfferer.isDeleted),
        )
        .options(sa_orm.joinedload(models.UserOfferer.user).load_only(users_models.User.email))
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


def get_venue_opening_hours_by_weekday(venue: models.Venue, weekday: models.Weekday) -> models.OpeningHours:
    for opening_hours in venue.openingHours:
        if opening_hours.weekday == weekday:
            return opening_hours
    return models.OpeningHours(weekday=weekday)


def delete_venue_accessibility_provider(venue: models.Venue) -> None:
    models.AccessibilityProvider.query.filter_by(venueId=venue.id).delete(synchronize_session=False)
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
        venue.accessibilityProvider.externalAccessibilityData = (
            accessibility_data.dict() if accessibility_data else None
        )
        venue.accessibilityProvider.lastUpdateAtProvider = last_update
        db.session.add(venue.accessibilityProvider)


def count_open_to_public_venues_with_accessibility_provider() -> int:
    return (
        offerers_models.Venue.query.join(offerers_models.AccessibilityProvider)
        .filter(
            sa.or_(offerers_models.Venue.isOpenToPublic.is_(True)),
            offerers_models.Venue.isVirtual.is_(False),
        )
        .count()
    )


def get_open_to_public_venues_with_accessibility_provider(batch_size: int, batch_num: int) -> list[models.Venue]:
    return (
        offerers_models.Venue.query.join(offerers_models.Venue.accessibilityProvider)
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
        offerers_models.Venue.query.outerjoin(offerers_models.Venue.accessibilityProvider)
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
        "street": str | None,
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
    latitude = decimal.Decimal(location_data["latitude"]).quantize(decimal.Decimal("1.00000"))
    longitude = decimal.Decimal(location_data["longitude"]).quantize(decimal.Decimal("1.00000"))
    street = location_data.get("street")
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
        address = geography_models.Address.query.filter(
            geography_models.Address.banId == ban_id,
            geography_models.Address.inseeCode == insee_code,
            geography_models.Address.street == street,
            geography_models.Address.postalCode == postal_code,
            geography_models.Address.city == city,
            geography_models.Address.latitude == latitude,
            geography_models.Address.longitude == longitude,
        ).one()

    return address


def get_or_create_offerer_address(offerer_id: int, address_id: int, label: str | None = None) -> models.OffererAddress:
    with transaction():
        try:
            offerer_address = models.OffererAddress(offererId=offerer_id, addressId=address_id, label=label)
            db.session.add(offerer_address)
            db.session.flush()
        except sa.exc.IntegrityError:
            if is_managed_transaction():
                mark_transaction_as_invalid()
            else:
                db.session.rollback()

    offerer_address = (
        models.OffererAddress.query.filter(
            models.OffererAddress.offererId == offerer_id,
            models.OffererAddress.label == label,
            models.OffererAddress.addressId == address_id,
        )
        .options(sa_orm.joinedload(models.OffererAddress.address))
        .first()
    )

    return offerer_address


def create_offerer_address(offerer_id: int, address_id: int | None, label: str | None = None) -> models.OffererAddress:
    assert offerer_id
    try:
        offerer_address = models.OffererAddress(offererId=offerer_id, addressId=address_id, label=label)
        db.session.add(offerer_address)
        db.session.flush()
    except sa.exc.IntegrityError:
        db.session.rollback()
        raise (exceptions.OffererAddressCreationError())
    return offerer_address


def switch_old_oa_label(
    old_oa: models.OffererAddress, label: str, venue_snapshot: history_api.ObjectUpdateSnapshot
) -> None:
    venue_snapshot.trace_update(
        {"label": label},
        target=old_oa,
        field_name_template="old_oa_label",
    )
    old_oa.label = label
    db.session.add(old_oa)
    db.session.flush()


def duplicate_oa(
    venue: models.Venue,
    old_oa: models.OffererAddress,
    new_oa: models.OffererAddress,
    is_manual_edition: bool,
    venue_snapshot: history_api.ObjectUpdateSnapshot,
) -> None:
    new_oa.label = old_oa.label
    if old_oa.address.isManualEdition != is_manual_edition:
        new_oa.address = get_or_create_address(
            {
                "street": old_oa.address.street,
                "city": old_oa.address.city,
                "postal_code": old_oa.address.postalCode,
                "insee_code": old_oa.address.inseeCode,
                "latitude": typing.cast(float, old_oa.address.latitude),
                "longitude": typing.cast(float, old_oa.address.longitude),
                "ban_id": old_oa.address.banId,
            },
            is_manual_edition,
        )
        venue_snapshot.trace_update(
            {"isManualEdition": is_manual_edition},
            target=old_oa.address,
            field_name_template="offererAddress.address.isManualEdition",
        )
    else:
        new_oa.address = old_oa.address
    venue_snapshot.trace_update(
        {"id": new_oa.id, "addressId": new_oa.addressId, "label": new_oa.label},
        old_oa,
        "offererAddress.{}",
    )
    db.session.add(new_oa)
    db.session.flush()
    venue.offererAddressId = new_oa.id
    db.session.add(venue)
    db.session.flush()


def create_offerer_address_from_address_api(address: offerers_schemas.AddressBodyModel) -> geography_models.Address:
    if address.isManualEdition:
        try:
            address_info = api_adresse.get_municipality_centroid(city=address.city, postcode=address.postalCode)
            location_data = LocationData(
                city=address.city,
                postal_code=address.postalCode,
                latitude=float(address.latitude),
                longitude=float(address.longitude),
                street=address.street,
                insee_code=address_info.citycode,
                ban_id=None,
            )
        except api_adresse.NoResultException:
            location_data = LocationData(
                city=address.city,
                postal_code=address.postalCode,
                latitude=float(address.latitude),
                longitude=float(address.longitude),
                street=address.street,
                insee_code=None,
                ban_id=None,
            )
    else:
        address_info = api_adresse.get_address(address=address.street, postcode=address.postalCode, city=address.city)
        location_data = LocationData(
            city=address_info.city,
            postal_code=address_info.postcode,
            latitude=address_info.latitude,
            longitude=address_info.longitude,
            street=address_info.street,
            insee_code=address_info.citycode,
            ban_id=address_info.id,
        )
    return get_or_create_address(location_data, is_manual_edition=address.isManualEdition)


def get_offerer_address_from_address(
    offerer_id: int, address: offerers_schemas.AddressBodyModel
) -> offerers_models.OffererAddress:
    assert offerer_id
    if not address.label:
        address.label = None
    address_from_api = create_offerer_address_from_address_api(address)
    return get_or_create_offerer_address(
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
            query = offerers_models.OffererConfidenceRule.query.filter_by(id=offerer_or_venue.confidenceRule.id)
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
            offerers_models.Offerer.query.join(
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
    # FIXME: to be modified when adage sync cron frequency is updated
    since_date = datetime.utcnow() - timedelta(days=2)
    adage_api.synchronize_adage_ids_on_venues(debug=True, since_date=since_date)
    return offerers_repository.offerer_has_venue_with_adage_id(offerer_id)


def synchronize_from_ds_and_check_application(offerer_id: int) -> bool:
    dms_api.import_dms_applications_for_all_eac_procedures(ignore_previous=False)
    query = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.managingOffererId == offerer_id)
        .filter(offerers_models.Venue.collectiveDmsApplications.any())
    )
    return db.session.query(query.exists()).scalar()


def create_action_history_when_move_offers(
    origin_venue_id: int,
    destination_venue_id: int,
    offer_ids: list[int] | None,
    offers_type: typing.Literal["individual", "collective"],
) -> None:
    """
    Simple action history entry, in both origin and destination venues, when moving
    all offers (individual or collective) from one venue to another.
    One entry is made by offer type.
    """
    action_history_origin_extra_data = {
        offers_type + "_offer_ids": offer_ids,
        "destination_venue_id": destination_venue_id,
    }
    action_history_origin = history_models.ActionHistory(
        venueId=origin_venue_id,
        actionType=history_models.ActionType.MOVE_ALL_OFFER,
        extraData=action_history_origin_extra_data,
    )

    action_history_destination_extra_data = {
        offers_type + "_offer_ids": offer_ids,
        "origin_venue_id": origin_venue_id,
    }
    action_history_destination = history_models.ActionHistory(
        venueId=destination_venue_id,
        actionType=history_models.ActionType.MOVE_ALL_OFFER,
        extraData=action_history_destination_extra_data,
    )
    db.session.add_all([action_history_origin, action_history_destination])
