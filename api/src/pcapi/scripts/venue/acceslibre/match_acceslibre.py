import csv
from datetime import datetime
import json
import logging
import pathlib

import sqlalchemy.exc as sa_exc

import pcapi.connectors.acceslibre as acceslibre_connector
from pcapi.core.offerers import models
from pcapi.models import db


PATH = pathlib.Path(__file__).parent.resolve()
CHUNK_SIZE = 100

logger = logging.getLogger(__name__)


def export_match_as_csv(match: list, filename: pathlib.Path) -> None:
    output_file = PATH / filename
    output_exists = pathlib.Path(output_file).is_file()
    print(f"Writing matching venues in {filename}")
    with open(output_file, "a", newline="", encoding="utf-8") as csv_file:
        headers = [
            "Venue ID",
            "uuid AccesLibre",
            "slug AccesLibre",
            "Nom PassCulture",
            "Nom Publique PassCulture",
            "Nom AccesLibre",
            "Ban ID PassCulture",
            "Adresse PassCulture",
            "Adresse AccesLibre",
            "Activite PassCulture",
            "Activite AccesLibre",
            "Siret PassCulture",
            "Siret AccesLibre",
            "Last Update AccesLibre",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        if not output_exists:
            writer.writeheader()
        writer.writerows(match)


def export_no_match(output_file: pathlib.Path, venues_list: list[dict]) -> None:
    print(f"Exporting venues with no match found in {output_file}")
    output = []
    for venue in venues_list:
        output.append(
            {
                "Venue ID": venue["Venue ID"],
                "Venue Name": venue["Venue Name"],
                "Venue Public Name": venue["Venue Public Name"],
                "Venue Address": f"{venue['Venue Address']} {venue['Venue City']} {venue['Venue Postal Code']}",
                "Venue Ban ID": venue["Ban ID"],
                "Venue Siret": venue["Venue Siret"],
                "Venue Activity": venue["Venue Type Code"],
            }
        )
    with open(output_file, "w", newline="", encoding="utf-8") as csv_file:
        headers = [
            "Venue ID",
            "Venue Name",
            "Venue Public Name",
            "Venue Address",
            "Venue Ban ID",
            "Venue Siret",
            "Venue Activity",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(output)


def update_venues_from_csv(filename: pathlib.Path, permanent_venues: list[models.Venue]) -> None:
    # Read result csv and update slug
    with open(filename, "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        permanent_venues_ids = {v.id: v for v in permanent_venues}
        for line in csv_reader:
            try:
                venue_id = int(line["Venue ID"])
                acceslibre_slug = line.get("slug AccesLibre", None)
                acceslibre_last_update = line.get("Last Update AccesLibre")
                venue = permanent_venues_ids.get(venue_id)
                if venue and acceslibre_slug:
                    if not venue.accessibilityProvider:
                        venue.accessibilityProvider = models.AccessibilityProvider(
                            externalAccessibilityId=acceslibre_slug
                        )
                    else:
                        venue.accessibilityProvider.externalAccessibilityId = acceslibre_slug
                if venue and acceslibre_last_update:
                    if venue.accessibilityProvider:
                        venue.accessibilityProvider.lastUpdateAtProvider = datetime.strptime(
                            acceslibre_last_update, "%Y-%m-%d %H:%M:%S.%f%z"
                        )
            except KeyError:
                print(f"ERROR: Venue ID is missing for this entry: {line}")
    # Log infos of which venues have been updated
    venues_with_acceslibre_slug = [v for v in permanent_venues if v.accessibilityProvider]
    venues_without_acceslibre_slug = [v for v in permanent_venues if not v.accessibilityProvider]
    print(
        f"{len(venues_with_acceslibre_slug)} Venues have been updated \n"
        f"{len(venues_without_acceslibre_slug)} Venues not updated. Check in DB with this command:\n"
        f'> SELECT venue.id FROM venue JOIN accessibility_provider ON accessibility_provider."venueId" = venue.id '
        f'WHERE venue."isPermanent" IS TRUE AND venue."isVirtual" IS FALSE AND accessibility_provider."externalAccessibilityId" IS NULL\n'
        f"\n Don't forget to remove file from system when you are done:\n"
        f"> rm {filename}\n"
    )


# If we want to use this script in dev context we need to uncomment following lines
# and add ACCESLIBRE_API_KEY={your api key} in .env.local.secret
# from pcapi.core.testing import override_settings
# @override_settings(ACCESLIBRE_BACKEND="pcapi.connectors.acceslibre.AcceslibreBackend")
def run_matching(export_not_matching_venues: bool = False) -> None:
    matching_acceslibre_file = PATH / "match_acceslibre.csv"
    print(f"Requesting acceslibre API and write matching venues in {matching_acceslibre_file} \n")
    # To run locally, we use a metabase json export of Permanent AND Non Virtual Venues
    permanent_venues_file = PATH / "data/pc_permanent_venues.json"
    with open(permanent_venues_file, "r", encoding="utf-8") as file:
        permanent_venues = json.load(file)
    already_requested_venues_ids = set()

    # We need to export missing match to validate matching algorithm
    export_not_matching_filename = PATH / "venues_not_matching.csv"

    # If file already exists, we skip already matching venues
    if pathlib.Path(matching_acceslibre_file).is_file():
        with open(matching_acceslibre_file, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            already_requested_venues_ids = {int(line["Venue ID"]) for line in csv_reader}
    venues_to_process = [v for v in permanent_venues if int(v["Venue ID"]) not in already_requested_venues_ids]
    print(f"{len(venues_to_process)} permanent venues to update in DB \n")
    batches = [venues_to_process[i : i + CHUNK_SIZE] for i in range(0, len(venues_to_process), CHUNK_SIZE)]
    matching_venue_ids = set()
    for i, batch in enumerate(batches, start=1):
        match_list = []
        for venue in batch:
            # Request acceslibre API to find matching Venue
            acceslibre_venue = acceslibre_connector.find_venue_at_accessibility_provider(
                name=venue["Venue Name"],
                public_name=venue["Venue Public Name"],
                siret=venue["Venue Siret"],
                ban_id=venue["Ban ID"],
                city=venue["Venue City"],
                postal_code=venue["Venue Postal Code"],
                address=venue["Venue Address"],
            )
            if acceslibre_venue:
                match_list.append(
                    {
                        "Venue ID": venue["Venue ID"],
                        "uuid AccesLibre": acceslibre_venue["uuid"],
                        "slug AccesLibre": acceslibre_venue["slug"],
                        "Nom PassCulture": venue["Venue Name"],
                        "Nom Publique PassCulture": venue["Venue Public Name"],
                        "Nom AccesLibre": acceslibre_venue["nom"],
                        "Ban ID PassCulture": venue["Ban ID"],
                        "Adresse PassCulture": f"{venue['Venue Address']} {venue['Venue Postal Code']} {venue['Venue City']}",
                        "Adresse AccesLibre": acceslibre_venue["adresse"],
                        "Activite PassCulture": venue["Venue Type Code"],
                        "Activite AccesLibre": acceslibre_venue["activite"]["nom"],
                        "Siret PassCulture": venue["Venue Siret"],
                        "Siret AccesLibre": acceslibre_venue["siret"],
                        "Last Update AccesLibre": datetime.strptime(
                            acceslibre_venue["updated_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
                        ),
                    }
                )
                matching_venue_ids.add(venue["Venue ID"])
        export_match_as_csv(match_list, matching_acceslibre_file)
    venues_not_matching = [v for v in venues_to_process if v["Venue ID"] not in matching_venue_ids]
    print(f"Number of permanent venues matching acceslibre found: {len(matching_venue_ids)}\n")
    print(f"Number of permanent venues not matching acceslibre: {len(venues_not_matching)}\n")

    if export_not_matching_venues:
        export_no_match(output_file=export_not_matching_filename, venues_list=venues_not_matching)


def run_update(dry_run: bool = True) -> None:
    matching_acceslibre_file = PATH / "match_acceslibre.csv"
    if not pathlib.Path(matching_acceslibre_file).is_file():
        print(f"Matching file {matching_acceslibre_file} is missing ...")
        return
    permanent_venues = (
        models.Venue.query.filter(models.Venue.isPermanent == True, models.Venue.isVirtual == False)
        .order_by(models.Venue.id.asc())
        .all()
    )
    update_venues_from_csv(matching_acceslibre_file, permanent_venues)
    batches = [permanent_venues[i : i + 1000] for i in range(0, len(permanent_venues), 1000)]
    for i, batch in enumerate(batches, start=1):
        for venue in batch:
            db.session.add(venue)
        if not dry_run:
            try:
                db.session.commit()
            except sa_exc.SQLAlchemyError:
                logger.exception("Could not update batch %d", i)
                db.session.rollback()


def run_export_non_match() -> None:
    matching_acceslibre_file = PATH / "match_acceslibre.csv"
    permanent_venues_file = PATH / "data/pc_permanent_venues.json"
    export_not_matching_filename = PATH / "venues_not_matching_export.csv"

    with open(permanent_venues_file, "r", encoding="utf-8") as file:
        permanent_venues = json.load(file)
    matching_venue_ids = set()

    # If file already exists, we skip already matching venues
    if pathlib.Path(matching_acceslibre_file).is_file():
        with open(matching_acceslibre_file, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            matching_venue_ids = {int(line["Venue ID"]) for line in csv_reader}
    venues_list = [v for v in permanent_venues if int(v["Venue ID"]) not in matching_venue_ids]
    export_no_match(output_file=export_not_matching_filename, venues_list=venues_list)
