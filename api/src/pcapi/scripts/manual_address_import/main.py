import datetime
import decimal
import math
import time

import sqlalchemy as sa
from sqlalchemy import text

from pcapi.app import app
from pcapi.connectors import api_adresse
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils import regions as utils_regions


app.app_context().push()


def get_or_create_offerer_address(offerer_id: int, address_id: int) -> offerers_models.OffererAddress:
    if not (
        offerer_address := offerers_models.OffererAddress.query.filter_by(
            offererId=offerer_id, addressId=address_id
        ).one_or_none()
    ):
        offerer_address = offerers_models.OffererAddress(offererId=offerer_id, addressId=address_id)
        db.session.add(offerer_address)
        db.session.flush()
    return offerer_address


def get_or_create_address(
    ban_id: str | None,
    street: str | None,
    city: str,
    postal_code: str,
    insee_code: str | None,
    latitude: float,
    longitude: float,
    is_manual: bool = False,
) -> geography_models.Address:
    """look a like offerers.api.get_or_create_address without internal rollback
    We also consider all writing as not manual
    """
    departmentCode = None
    timezone = None
    if insee_code:
        departmentCode = utils_regions.get_department_code_from_city_code(insee_code)
        timezone = date_utils.get_department_timezone(departmentCode)
    if not (
        address := geography_models.Address.query.filter(
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
                    geography_models.Address.latitude == decimal.Decimal(latitude),
                    geography_models.Address.longitude == decimal.Decimal(longitude),
                ),
            ),
        ).one_or_none()
    ):

        address = geography_models.Address(
            banId=ban_id,
            street=street,
            city=city,
            postalCode=postal_code,
            inseeCode=insee_code,
            latitude=decimal.Decimal(latitude),
            longitude=decimal.Decimal(longitude),
            departmentCode=departmentCode,
            timezone=timezone,
            isManualEdition=is_manual,
        )
        db.session.add(address)
        db.session.flush()
    return address


def populate_tables(dry_run: bool) -> None:

    addresses = db.session.execute(
        text(
            """
         SELECT venue."id", venue."managingOffererId",  venue."street", venue."city", venue."postalCode", venue."latitude", venue."longitude"
            FROM venue WHERE venue."offererAddressId" is NULL AND venue."isVirtual" is false
        """
        )
    )
    addresses = list(addresses)  # 246 in staging

    how_many_addresses = len(addresses)

    print(f"Processing {how_many_addresses} addresses")

    for i, venue_address in enumerate(addresses):

        postal_code = venue_address.postalCode
        city = venue_address.city
        try:
            insee_code = api_adresse.get_municipality_centroid(city, postal_code).citycode
        except api_adresse.NoResultException:
            insee_code = None
        address = get_or_create_address(
            ban_id=None,
            street=venue_address.street,
            city=city,
            postal_code=postal_code,
            insee_code=insee_code,
            latitude=float(venue_address.latitude),
            longitude=float(venue_address.longitude),
            is_manual=True,
        )

        offerer_address = get_or_create_offerer_address(int(venue_address.managingOffererId), address.id)

        offerers_models.Venue.query.filter_by(id=venue_address.id).update({"offererAddressId": offerer_address.id})
        db.session.flush()
        if not dry_run:
            db.session.commit()

        print(f"Processed {math.ceil(i/how_many_addresses*100)} % of the file at venue id {venue_address.id}", end="\r")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Populate tables with manual addresses")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    try:
        start = time.time()
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

        populate_tables(args.dry_run)
    except:
        db.session.rollback()
        raise
    else:
        if args.dry_run:
            db.session.rollback()
    finally:
        end = time.time()
        print(f"Duration: {end - start}")
