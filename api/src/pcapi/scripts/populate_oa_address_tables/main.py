"""
input_data.csv looks like this:
old_street,old_city,old_postal_code,venues_ids,latitude,longitude,result_id,result_name,result_postcode,result_city,result_citycode,result_status
1 COURS D HERBOUVILLE,LYON 4EME,69004,[id, id, id, ...],45.7741,4.838369,69384_3530_00001,1 Cours d'Herbouville,69004,Lyon,69384,ok
5 Rue Eugène Freyssinet,Paris,75013,[id, id, ...],48.832574,2.371624,75113_3414_00005,5 Rue Eugène Freyssinet,75013,Paris,75113,ok
12 ALL DES PETITS PAINS,CERGY,95800,[id],49.047668,2.034227,95127_1243_00012,12 Allée des Petits Pains,95800,Cergy,95127,ok
...

The SQL statement populate the first four columns. Calling the API Address populates the remaining.
"""

import argparse
import csv
import json
import math
import os
import time

from fetch_input_data import fetch_input_data  # pylint: disable=import-error

from pcapi.app import app
from pcapi.connectors.api_adresse import ResultColumn
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db


app.app_context().push()

SKIP = ("skipped", "error", "not-found")


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


def populate_tables(dry_run: bool) -> None:

    fieldnames = [
        "old_street",
        "old_city",
        "old_postal_code",
        "venues_ids",
        ResultColumn.LATITUDE.value,
        ResultColumn.LONGITUDE.value,
        ResultColumn.RESULT_ID.value,
        ResultColumn.RESULT_NAME.value,
        ResultColumn.RESULT_POSTCODE.value,
        ResultColumn.RESULT_CITY.value,
        ResultColumn.RESULT_CITYCODE.value,
        ResultColumn.RESULT_STATUS.value,
    ]

    with open(f"{os.path.dirname(os.path.abspath(__file__))}/input_data.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, fieldnames=fieldnames)

        # skip the header
        next(reader)
        rows = list(reader)
        how_much_addresses = len(rows)

        print(f"Processing {how_much_addresses} addresses")

        for i, row in enumerate(rows):
            if row["result_status"] in SKIP:
                continue

            venues_and_offerers_ids = (
                offerers_models.Venue.query.filter(offerers_models.Venue.id.in_(json.loads(row["venues_ids"])))
                .with_entities(offerers_models.Venue.id, offerers_models.Venue.managingOffererId)
                .all()
            )

            postal_code = row[ResultColumn.RESULT_POSTCODE.value]
            city = row[ResultColumn.RESULT_CITY.value]

            if not postal_code and city == "Saint-Martin":
                postal_code = "97150"
            if not postal_code and city == "Nouméa":
                postal_code = "98800"
            if not postal_code and city == "Saint-Barthélemy":
                postal_code = "97133"

            address = offerers_api.get_or_create_address(
                offerers_api.LocationData(
                    ban_id=row[ResultColumn.RESULT_ID.value],
                    street=row[ResultColumn.RESULT_NAME.value],
                    city=city,
                    postal_code=postal_code,
                    insee_code=row[ResultColumn.RESULT_CITYCODE.value],
                    latitude=float(row[ResultColumn.LATITUDE.value]),
                    longitude=float(row[ResultColumn.LONGITUDE.value]),
                )
            )

            for venue_id, offerer_id in venues_and_offerers_ids:
                offerer_address = get_or_create_offerer_address(offerer_id, address.id)

                offerers_models.Venue.query.filter_by(id=venue_id).update({"offererAddressId": offerer_address.id})
                db.session.flush()

                db.session.bulk_update_mappings(offers_models.Offer, {"offererAddressId": offerer_address.id})
                db.session.flush()

            if not dry_run:
                db.session.commit()

            print(f"Processed {math.ceil(i/how_much_addresses*100)} % of the file", end="\r")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch addressess from API Address given our own internal data")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--batch-size", type=int)
    args = parser.parse_args()

    try:
        start = time.time()
        fetch_input_data(args.batch_size)
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
