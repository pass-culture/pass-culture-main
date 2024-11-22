import argparse

from pcapi.app import app
import pcapi.core.geography.models as geography_models
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db


app.app_context().push()


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
        )
    )


def create_venue_address_as_manual(venues: list[offerers_models.Venue]):
    incorrect_oa_label = "Localisation erronée - Structure "
    for venue in venues:
        # Duplicate OA to keep the informations
        offerers_api.create_offerer_address(
            offerer_id=venue.offererAddress.offererId,
            address_id=venue.offererAddress.addressId,
            label=f"{incorrect_oa_label}{venue.id}",
        )
        # Create new address
        address = offerers_api.get_or_create_address(
            offerers_api.LocationData(
                postal_code=venue.postalCode,
                city=venue.city,
                latitude=venue.latitude,
                longitude=venue.longitude,
                street=venue.street,
                # insee_code=venue.citycode,
                # ban_id=venue.banId,
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

    try:
        venues = get_inconsistent_venue_addresses()
        create_venue_address_as_manual(venues)
    except:
        db.session.rollback()
        raise
    else:
        if args.dry_run:
            db.session.rollback()
        else:
            db.session.commit()
