import argparse
import decimal
import logging
import math
from unittest.mock import patch

import sqlalchemy as sa

from pcapi.app import app
import pcapi.core.geography.models as geography_models
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.exceptions as offerers_exceptions
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.repository import is_managed_transaction
from pcapi.repository import mark_transaction_as_invalid
from pcapi.repository import transaction
from pcapi.utils import regions as utils_regions
import pcapi.utils.date as date_utils


app.app_context().push()
logger = logging.getLogger(__name__)


def patched_get_or_create_address(
    location_data: offerers_api.LocationData, is_manual_edition: bool = False
) -> geography_models.Address:
    assert location_data["city"]
    department_code = None
    timezone = None
    # Workaround mypy :(
    insee_code = location_data.get("insee_code")
    insee_code = insee_code.strip() if insee_code is not None else insee_code
    postal_code = location_data["postal_code"].strip()
    latitude = decimal.Decimal(location_data["latitude"]).quantize(decimal.Decimal("1.00000"))
    longitude = decimal.Decimal(location_data["longitude"]).quantize(decimal.Decimal("1.00000"))
    street = location_data.get("street")
    city = location_data["city"].strip()
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
            geography_models.Address.street == street,
            geography_models.Address.inseeCode == insee_code,
            sa.or_(
                geography_models.Address.isManualEdition.is_not(True),  # false or null
                sa.and_(
                    geography_models.Address.banId == ban_id,
                    geography_models.Address.inseeCode == insee_code,
                    geography_models.Address.street == street,
                    geography_models.Address.postalCode == postal_code,
                    geography_models.Address.city == city,
                    geography_models.Address.latitude == decimal.Decimal(latitude).quantize(decimal.Decimal("1.00000")),
                    geography_models.Address.longitude
                    == decimal.Decimal(longitude).quantize(decimal.Decimal("1.00000")),
                ),
            ),
        ).one()
        if not math.isclose(float(address.latitude), float(latitude), rel_tol=0.00001) or not math.isclose(
            float(address.longitude), float(longitude), rel_tol=0.00001
        ):
            logger.error(
                "Unique constraint over street and inseeCode matched different coordinates",
                extra={
                    "address_id": address.id,
                    "incoming_banId": ban_id,
                    "address_latitude": address.latitude,
                    "address_longitude": address.longitude,
                    "incoming_latitude": latitude,
                    "incoming_longitude": longitude,
                },
            )

    return address


def patched_create_offerer_address(
    offerer_id: int, address_id: int | None, label: str | None = None
) -> offerers_models.OffererAddress:
    with transaction():
        try:
            offerer_address = offerers_models.OffererAddress(offererId=offerer_id, addressId=address_id, label=label)
            db.session.add(offerer_address)
            db.session.flush()
        except sa.exc.IntegrityError:
            if is_managed_transaction():
                mark_transaction_as_invalid()
            else:
                db.session.rollback()
            raise (offerers_exceptions.OffererAddressCreationError())
    return offerer_address


def get_inconsistent_venue_addresses() -> list[offerers_models.Venue]:
    # SELECT venue.id, venue.city, venue."postalCode", address.city, address."postalCode"
    # FROM venue
    # JOIN offerer_address ON offerer_address.id = venue."offererAddressId"
    # JOIN address ON address.id = offerer_address."addressId"
    # WHERE NOT venue."postalCode" = address."postalCode"
    # AND NOT venue.city = address.city
    return (
        offerers_models.Venue.query.join(offerers_models.Venue.offererAddress).join(
            offerers_models.OffererAddress.address
        )
        # I left an AND condition between city and postalCode to
        # leave upper/lower case and/or CEDEX postalCode modifications
        .filter(
            offerers_models.Venue.city != geography_models.Address.city,
            offerers_models.Venue.postalCode != geography_models.Address.postalCode,
            # ignore venues with low quality address that are correct in the address table
            offerers_models.Venue.id.not_in((6884,)),
        )
    )


def create_venue_address_as_manual(existing_venues: list[offerers_models.Venue]) -> None:
    incorrect_oa_label = "Localisation erronée - Structure "
    for venue in existing_venues:
        if venue.offererAddress is None:
            return
        print(
            "Altering OA #%s for venue #%s (%s) with offerer #%s"
            % (venue.offererAddressId, venue.id, venue.common_name, venue.managingOffererId)
        )
        # Duplicate OA to keep the informations
        if venue.offererAddress.offererId is not None and venue.offererAddress.addressId is not None:
            offerers_api.create_offerer_address(
                offerer_id=venue.offererAddress.offererId,
                address_id=venue.offererAddress.addressId,
                label=f"{incorrect_oa_label}{venue.id}",
            )
        # Create new address
        address = offerers_api.get_or_create_address(
            offerers_api.LocationData(
                postal_code=str(venue.postalCode),
                city=str(venue.city),
                latitude=float(venue.latitude) if venue.latitude is not None else 0,
                longitude=float(venue.longitude) if venue.longitude is not None else 0,
                street=venue.street,
                insee_code=None,
                ban_id=None,
            ),
            is_manual_edition=True,
        )
        # link current OA to the new address
        offerer_address = venue.offererAddress
        offerer_address.address = address
        db.session.add(offerer_address)
        db.session.flush()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script pour créer manuellement des adresses")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    with atomic():
        with patch("pcapi.core.offerers.api.get_or_create_address", patched_get_or_create_address):
            with patch("pcapi.core.offerers.api.create_offerer_address", patched_create_offerer_address):
                venues = get_inconsistent_venue_addresses()
                print("Venues to correct: %s" % [venue.id for venue in venues])
                create_venue_address_as_manual(venues)

                if args.dry_run:
                    mark_transaction_as_invalid()
