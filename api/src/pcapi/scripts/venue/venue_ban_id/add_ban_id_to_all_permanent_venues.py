import csv
from io import StringIO
import logging
import pathlib

import requests
import sqlalchemy as sa

from pcapi.connectors import api_adresse
from pcapi.core.offerers.models import Venue
from pcapi.models import db


logger = logging.getLogger()
PATH = pathlib.Path().parent.resolve()
CHUNK_SIZE = 10
TIMEOUT = 1200


def request_adresse_api(
    filename: pathlib.Path, permanent_venues: list[Venue], already_requested_venues_ids: set[int]
) -> None:
    # Call to API
    base_url = "https://api-adresse.data.gouv.fr/search/csv/"
    header = "Venue ID,adresse,postcode,city\n"
    batches = [permanent_venues[i : i + CHUNK_SIZE] for i in range(0, len(permanent_venues), CHUNK_SIZE)]
    for i, batch in enumerate(batches, start=1):
        payload = f"{header}"
        for venue in batch:
            if venue.id not in already_requested_venues_ids:
                payload += f"{venue.id},{venue.address},{venue.postalCode},{venue.city}\n"

        if payload == header:
            print(f"WARNING: No venues to request from Adresse API, please check or delete {filename}")
            return

        files = [
            ("data", payload),
            ("result_columns", (None, "result_id")),
        ]

        response = requests.post(base_url, files=files, timeout=TIMEOUT)  # type: ignore [arg-type]
        if response.status_code == 200:
            # Save response to csv file
            result_data = csv.DictReader(StringIO(response.text))
            fieldnames = result_data.fieldnames if result_data.fieldnames else []
            output_exists = pathlib.Path(filename).is_file()
            # If existing, append to file
            with open(filename, mode="a", newline="", encoding="utf-8") as csv_output:
                writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
                if not output_exists:
                    writer.writeheader()
                writer.writerows(result_data)
        else:
            print(f"WARNING: Request wasn't successful. {response.status_code, response.content}")


# Does not work in Testing / Dev env: use
# @override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
def request_missing_ban_ids(permanent_venues_without_ban_id: list[Venue]) -> pathlib.Path:
    header = ["Venue ID", "adresse", "postcode", "city", "result_id"]
    output = PATH / "ban_ids_from_adresse_api_retry.csv"
    result_list = []
    for venue in permanent_venues_without_ban_id:
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
            pass

    with open(output, mode="w", newline="", encoding="utf-8") as csv_output:
        writer = csv.DictWriter(csv_output, fieldnames=header)
        writer.writeheader()
        for row in result_list:
            print(row)
            writer.writerow(row)
    return output


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


def merge_results(*files: str) -> str:
    merged_filename = PATH / "ban_ids_from_adresse_api_merged.csv"
    empty_data_ids = []
    venue_ids = set()
    unique_data = []
    for file in files:
        with open(file, "r", encoding="utf-8") as file:  # type: ignore [assignment]
            csv_reader = csv.DictReader(file)
            for data in csv_reader:
                venue_id = data["Venue ID"]
                ban_id = data.get("result_id", None)
                if venue_id not in venue_ids and ban_id:
                    venue_ids.add(venue_id)
                    unique_data.append(data)
                if venue_id not in venue_ids and not ban_id:
                    empty_data_ids.append(data["Venue ID"])

    with open(merged_filename, "w", encoding="utf-8") as f:
        fieldnames = ["Venue ID", "adresse", "postcode", "city", "result_id"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_data)
    return f"Venues ID with no BanID: {empty_data_ids}"


def execute(dry_run: bool = True) -> None:
    print("Adding ban id to all permanent venues")

    # CSV file where we save the ban ids fetched from Adresse API
    filename = PATH / "ban_ids_from_adresse_api.csv"
    # If existing, read this file to avoid requesting twice the data in case of network failure
    already_requested_venues_ids = set()
    if pathlib.Path(filename).is_file():
        with open(filename, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            already_requested_venues_ids = {int(line["Venue ID"]) for line in csv_reader}

    # Query all permanent Venues from DB (That are not virtual)
    permanent_venues = Venue.query.filter(Venue.isPermanent == True, Venue.isVirtual == False).all()
    print(f"{len(permanent_venues)} permanent venues to update in DB")

    # In case of dry run, we request the API and save data to the CSV file
    if dry_run:
        request_adresse_api(filename, permanent_venues, already_requested_venues_ids)

        # If we want to call for adresse api to complete missing data: uncomment following
        # permanent_venues_without_ban_id = {v for v in permanent_venues if v.id not in already_requested_venues_ids}
        # retry_output_filename = request_missing_ban_ids(permanent_venues_without_ban_id)
        # merge_results(filename, retry_output_filename)

    # Once we have saved all data to csv, we write them to DB
    if not dry_run:
        if not pathlib.Path(filename).is_file():
            print("WARNING: Run this script in dry run first")
            return
        update_venues_from_csv(filename, permanent_venues)

        batches = [permanent_venues[i : i + 1000] for i in range(0, len(permanent_venues), 1000)]
        for i, batch in enumerate(batches, start=1):
            for venue in batch:
                try:
                    db.session.add(venue)
                except sa.exc.DataError as e:
                    print(f"Error: can't update venue {venue.id}: {e}")
            db.session.commit()
