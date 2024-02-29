import csv
import logging
import pathlib

import sqlalchemy.exc as sa_exc

from pcapi.connectors import api_adresse
from pcapi.core.offerers.models import Venue
from pcapi.models import db


logger = logging.getLogger()
PATH = pathlib.Path(__file__).parent.resolve()
CHUNK_SIZE = 10
TIMEOUT = 1200


# Does not work in Testing / Dev env: use
# from pcapi.core.testing import override_settings
# @override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def request_adresse_api_adresse(filename: pathlib.Path, venues_to_update: list[Venue]) -> None:
    header = ["Venue ID", "adresse", "postcode", "city", "result_id"]
    result_list = []
    for venue in venues_to_update:
        try:
            address_infos = api_adresse.get_address(address=venue.address, postcode=venue.postalCode, city=venue.city)  # type: ignore [arg-type]
            result_list.append(
                {
                    "Venue ID": venue.id,
                    "adresse": venue.address,
                    "postcode": venue.postalCode,
                    "city": venue.city,
                    "result_id": address_infos.id,
                }
            )
        except api_adresse.NoResultException:
            logger.exception(
                "Got an error while looking for address information on adresse API for Venue with ID: %s",
                venue.id,
            )
        except api_adresse.AdresseApiException:
            logger.exception(
                "There has been an error while connecting to adresse API for venue : %s",
                venue.id,
            )

    with open(filename, mode="w", newline="", encoding="utf-8") as csv_output:
        writer = csv.DictWriter(csv_output, fieldnames=header)
        writer.writeheader()
        for row in result_list:
            writer.writerow(row)


def update_venues_from_csv(filename: pathlib.Path, permanent_venues: list[Venue]) -> None:
    # Read result csv and update banId
    with open(filename, "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        permanent_venues_ids = {v.id: v for v in permanent_venues}
        for data in csv_reader:
            try:
                venue_id = int(data["Venue ID"])
                ban_id = data.get("result_id", None)
                venue = permanent_venues_ids.get(venue_id)
                if venue and ban_id:
                    venue.banId = ban_id
            except KeyError:
                print(f"ERROR: Venue ID is missing for this entry: {data}")
    # Log infos of which venues have been updated
    venues_with_ban_id = [v for v in permanent_venues if v.banId]
    venues_without_ban_id = [v for v in permanent_venues if not v.banId]
    print(
        f"{len(venues_with_ban_id)} Venues have been updated \n"
        f"{len(venues_without_ban_id)} Venues not updated. Check in DB with this command:\n"
        f'> SELECT id FROM venue WHERE "isPermanent" IS TRUE AND "isVirtual" IS FALSE AND "banId" IS NULL\n'
        f"\n Don't forget to remove file from system when you are done:\n"
        f"> rm {filename}"
    )


def get_incomplete_ban_ids(venue_list: list[Venue]) -> list[Venue]:
    venues_with_incomplete_ban_ids = []
    for venue in venue_list:
        if not venue.banId:
            venues_with_incomplete_ban_ids.append(venue)
        elif venue.banId and venue.address and (len(venue.banId) <= 10 and not venue.address.isalpha()):
            # For venues which have a short BAN id (meaning BAN id doesn't inform on street number)
            # We check if address has in fact no street number. If it has, it means the BAN id is incomplete
            venues_with_incomplete_ban_ids.append(venue)
    return venues_with_incomplete_ban_ids


def execute(dry_run: bool = True) -> None:
    print("Adding missing or incomplete BAN id to permanent venues")

    # CSV file where we save the ban ids fetched from Adresse API
    filename = PATH / "ban_ids_from_adresse_api.csv"

    # Query all permanent Venues from DB (That are not virtual)
    all_permanent_venues = (
        Venue.query.filter(Venue.isPermanent == True, Venue.isVirtual == False).order_by(Venue.id.asc()).all()
    )

    # In case of dry run, we request the API and save data to the CSV file
    if dry_run:
        print(f"Dry run: only fetching incomplete banIds from adresse API and save them in {filename}")

        permanent_venues_with_incomplete_ban_id = get_incomplete_ban_ids(all_permanent_venues)
        print(f"{len(permanent_venues_with_incomplete_ban_id)} venues to update")
        request_adresse_api_adresse(filename, permanent_venues_with_incomplete_ban_id)

    # Once we have saved all data to csv, we write them to DB
    if not dry_run:
        if not pathlib.Path(filename).is_file():
            print("WARNING: Run this script in dry run first")
            return
        update_venues_from_csv(filename, all_permanent_venues)

        batches = [all_permanent_venues[i : i + 1000] for i in range(0, len(all_permanent_venues), 1000)]
        for i, batch in enumerate(batches, start=1):
            for venue in batch:
                db.session.add(venue)
            try:
                db.session.commit()
            except sa_exc.SQLAlchemyError:
                logger.exception("Could not update batch %d", i)
                db.session.rollback()
