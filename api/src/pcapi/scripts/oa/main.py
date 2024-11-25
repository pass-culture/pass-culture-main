import argparse

from pcapi.app import app
import pcapi.core.geography.models as geography_models
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.models as offerers_models
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid


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
        venues = get_inconsistent_venue_addresses()
        print("Venues to correct: %s" % [venue.id for venue in venues])
        create_venue_address_as_manual(venues)

        if args.dry_run:
            mark_transaction_as_invalid()
