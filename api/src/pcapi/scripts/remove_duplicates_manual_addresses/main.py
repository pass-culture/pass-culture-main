import argparse
import logging

from pcapi import settings
from pcapi.app import app
from pcapi.core.geography.models import Address
from pcapi.core.offerers.models import OffererAddress
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()


def is_main_offerer_address_exists(main_id: int, offerer_addresses: dict) -> bool:
    return main_id in offerer_addresses["address_ids"]


def get_or_create_main_offerer_address(main_id: int, offerer_addresses: dict, duplicated_ids: list[int]) -> int:
    offerer_id = offerer_addresses["offerer_id"]
    if main_id in offerer_addresses["address_ids"]:
        offerer_address_id = (
            OffererAddress.query.filter(
                OffererAddress.offererId == offerer_addresses["offerer_id"], OffererAddress.addressId == main_id
            )
            .with_entities(OffererAddress.id)
            .one()
        )
        print(f"Found already exiting main offererAddress {offerer_address_id[0]} for addressId {main_id}")
        return offerer_address_id[0]

    offerer_address = OffererAddress.query.filter(
        OffererAddress.offererId == offerer_id,
        OffererAddress.addressId.in_(duplicated_ids),
    ).first()
    offerer_address.addressId = main_id
    db.session.flush()
    print(
        f"Only found duplicates offererAddress, promoting offererAddressId {offerer_address.id} to main (main addressId {main_id})"
    )
    return offerer_address.id


def switch_offers_to_main_offerer_address(
    main_offerer_address_id: int, offerer_addresses: dict, duplicated_ids: list[int]
) -> None:
    offerer_id = offerer_addresses["offerer_id"]
    duplicates_offerer_addresses = OffererAddress.query.filter(
        OffererAddress.offererId == offerer_id, OffererAddress.addressId.in_(duplicated_ids)
    ).with_entities(OffererAddress.id)
    offers_query = (
        Offer.query.filter(Offer.offererAddressId.in_(duplicates_offerer_addresses))
        .with_entities(Offer.id)
        .yield_per(1000)
    )
    db.session.bulk_update_mappings(
        Offer, [{"id": offer.id, "offererAddressId": main_offerer_address_id} for offer in offers_query]
    )
    print(f"Swith offers related to {offerer_addresses} to main offererAddressId {main_offerer_address_id}")
    db.session.flush()


def switch_venues_to_main_offerer_address(
    main_offerer_address_id: int, offerer_addresses: dict, duplicated_ids: list[int]
) -> None:
    offerer_id = offerer_addresses["offerer_id"]
    duplicates_offerer_addresses = OffererAddress.query.filter(
        OffererAddress.offererId == offerer_id, OffererAddress.addressId.in_(duplicated_ids)
    ).with_entities(OffererAddress.id)
    Venue.query.filter(Venue.offererAddressId.in_(duplicates_offerer_addresses)).update(
        {"offererAddressId": main_offerer_address_id}, synchronize_session=False
    )
    print(f"Swith venues related to {offerer_addresses} to main offererAddressId {main_offerer_address_id}")
    db.session.flush()


def prune_duplicates_offerer_addresses(offerer_id: int, duplicated_ids: list[int]) -> None:
    OffererAddress.query.filter(
        OffererAddress.offererId == offerer_id, OffererAddress.addressId.in_(duplicated_ids)
    ).delete()
    db.session.flush()


def get_offerers_addresses(address_ids: list[int]) -> list[dict]:
    return [
        offerers_addresses
        for offerers_addresses, in db.session.execute(
            """
            SELECT
                jsonb_build_object(
                    'offerer_id',
                    offerer_address."offererId",
                    'address_ids',
                    array_agg(offerer_address."addressId")
                )
            FROM
                offerer_address
            WHERE
                offerer_address."addressId" IN :address_ids
            GROUP BY offerer_address."offererId"
        """,
            {"address_ids": tuple(address_ids)},
        ).all()
    ]


def get_duplicates_addresses() -> list[dict]:
    """
    Will return something like this
    All ids sharing same duplicated data
    We’ll arbitrary consider the first id as the main address, others as duplicates and therefor removed
    [
      ({"ids": [1, 2]}),
      ({"ids": [3, 4]}),
      ({"ids": [5, 6]}),
      ({"ids": [7, 8, 9]}),
      ...
    ]
    """
    return [
        address
        for address, in db.session.execute(
            """
        SELECT
            jsonb_build_object(
                'ids',
                array_agg(DISTINCT address."id")
            )
        FROM
            address
        JOIN
            address a2 on address."street" = a2."street"
            AND address."postalCode" = a2."postalCode"
            AND address."inseeCode" = a2."inseeCode"
            AND address."city" = a2."city"
            AND address."latitude" = a2."latitude"
            AND address."longitude" = a2."longitude"
            AND address."isManualEdition" = a2."isManualEdition"
            AND address."departmentCode" = a2."departmentCode"
            AND address."timezone" = a2."timezone"
            AND address."isManualEdition" is True
            AND address."id" != a2."id"
        GROUP BY
            address."street",
            address."city",
            address."postalCode",
            address."inseeCode",
            address."latitude",
            address."longitude",
            address."departmentCode",
            address."timezone"
        """
        ).all()
    ]


def switch_offerers_addresses_to_main_address_id(duplicates: list[dict]) -> None:
    """
    Find all offerer(s) addresses for a set of duplicates address and try to be smart:
        - If we already have one offerer address existing for the arbitrary main address:
            - Keep it and do nothing
        - Else:
            - Take an (arbitrary) duplicates offerer address
            - Make it main offerer address
        - Switch offers that might be on duplicates offererAddress to the main one
        - Prune every other existing (duplicates) offerer addresses
    """
    for address in duplicates:
        main_id, duplicated_ids = address["ids"][0], address["ids"][1:]
        offerers_addresses = get_offerers_addresses(address["ids"])
        for offerer_addresses in offerers_addresses:
            main_offerer_address_id = get_or_create_main_offerer_address(main_id, offerer_addresses, duplicated_ids)
            switch_venues_to_main_offerer_address(main_offerer_address_id, offerer_addresses, duplicated_ids)
            switch_offers_to_main_offerer_address(main_offerer_address_id, offerer_addresses, duplicated_ids)
            prune_duplicates_offerer_addresses(offerer_addresses["offerer_id"], duplicated_ids)
        print(f"{len(offerers_addresses)} offerer addresses switch to main address {main_id}")


def empty_ban_id_on_addresses() -> None:
    Address.query.filter(Address.isManualEdition.is_(True), Address.banId.is_not(None)).update(
        {"banId": None}, synchronize_session=False
    )
    db.session.flush()
    print("banId empty from all manual edited addresses")


def remove_duplicates_addresses(duplicates: list[dict]) -> None:
    duplicates_addresses = []
    for address in duplicates:
        duplicates_addresses.extend(address["ids"][1:])
    Address.query.filter(Address.id.in_(duplicates_addresses)).delete()
    db.session.flush()
    print(f"{len(duplicates_addresses)} duplicates removed")


def process_duplicates_addresses(dry_run: bool) -> None:
    db.session.execute("SET SESSION statement_timeout = '300s'")
    duplicates = get_duplicates_addresses()
    print(f"Found {len(duplicates)} addresses that appears more than once")

    try:
        empty_ban_id_on_addresses()
        switch_offerers_addresses_to_main_address_id(duplicates)
        remove_duplicates_addresses(duplicates)
    except Exception:
        db.session.rollback()
        raise

    if not dry_run:
        db.session.commit()
    else:
        db.session.rollback()
    db.session.execute(f"SET SESSION statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove duplicates addresses among manual edition")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    process_duplicates_addresses(args.dry_run)
