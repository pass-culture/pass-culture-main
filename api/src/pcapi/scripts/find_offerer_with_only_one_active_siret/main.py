"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37647-api-sortir-la-liste-des-offerers-avec-plusieurs-sire-ts-mais-dont-1-seul-est-actif/api/src/pcapi/scripts/find_offerer_with_only_one_active_siret/main.py

"""

import argparse
import csv
import logging
import typing
from datetime import datetime

import pcapi.core.offerers.models as offerers_models
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


ETABLISSEMENTS_FILEPATH = "/Users/xordoquy/Downloads/StockEtablissementHistorique_utf8.csv"
SIRET_FILEPATH = "/Users/xordoquy/Downloads/siret_with_multiple_venues.csv"


def read_siret_file() -> typing.Generator[dict[str, str], None, None]:
    with open(ETABLISSEMENTS_FILEPATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, quoting=csv.QUOTE_NONE)
        for row in reader:
            yield row


def find_siret_status(venue_sirets: list[str]) -> dict[str, bool]:
    # The StockEtablissementHistorique_utf8 file is *huge* but the nice part is
    # it's sorted by SIRET so we can do a single pass
    sirets = {}
    rows = iter(read_siret_file())
    row = next(rows)
    ct = 1
    for siret in venue_sirets:
        # Scrolls untill we go past the siret
        # siret may appear several times in the file, we want to scan all the linked rows
        while row["siret"] <= siret:
            if (
                row["siret"] == siret
                and datetime.fromisoformat(row["dateDebut"]) <= datetime.today()
                and (
                    not row["dateFin"] or datetime.fromisoformat(row["dateFin"]) > datetime.today()
                )  # Discard passed entries
            ):
                sirets[siret] = row["etatAdministratifEtablissement"] == "A"  # A for Actif
            try:
                ct += 1
                if ct % 1_000_000 == 0:
                    logger.info(f"Processed {ct} rows, currently at siret {row['siret']}, checking for siret {siret}")
                row = next(rows)
            except StopIteration:
                logger.warning("End of file reached")
                return sirets

    return sirets


def fetch_venue_sirets_from_db() -> list[str]:
    offerer_ids = (
        db.session.query(offerers_models.Venue.managingOffererId)
        .filter(offerers_models.Venue.siret.isnot(None))
        .group_by(offerers_models.Venue.managingOffererId)
        .having(db.func.count(offerers_models.Venue.siret) > 1)
    )
    venue_sirets = (
        db.session.query(offerers_models.Venue.siret)
        .filter(
            offerers_models.Venue.siret.isnot(None),
            offerers_models.Venue.managingOffererId.in_([id for (id,) in offerer_ids]),
        )
        .order_by(offerers_models.Venue.siret)
        .all()
    )
    return [siret for (siret,) in venue_sirets]


def fetch_venue_sirets_from_file() -> list[dict[str, str]]:
    venue_sirets = []
    with open(SIRET_FILEPATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, quoting=csv.QUOTE_NONE)
        for row in reader:
            venue_sirets.append({"siret": row["venue_siret"], "offerer_id": row["managingOffererId"]})
    return venue_sirets


# SELECT
# 	venue.siret AS venue_siret,
# 	venue."managingOffererId"
# FROM venue
# WHERE
# 	venue.siret IS NOT NULL
# AND venue."managingOffererId" IN (
# 		SELECT DISTINCT(venue."managingOffererId") AS "offererId"
# 		FROM venue
# 		WHERE venue.siret IS NOT NULL
# 		AND venue."isSoftDeleted" IS NOT true
# 		GROUP BY venue."managingOffererId"
# 		HAVING count(venue.siret) > 1
# 	)
# AND venue."isSoftDeleted" IS NOT true
# ORDER BY venue.siret


def assert_active_sirets(existing_sirets: list[dict[str, str]]) -> None:
    logger.info("Reading the etablissement file")
    sirets = find_siret_status([row["siret"] for row in existing_sirets])
    logger.info("Extracting active offerer's siren")
    count_active_sirets_per_offerer_id: dict[str, list[str]] = {}
    count_inactive_sirets_per_offerer_id: dict[str, list[str]] = {}

    for row in existing_sirets:
        if sirets.get(row["siret"], False):  # Active
            count_active_sirets_per_offerer_id.setdefault(row["offerer_id"], []).append(row["siret"])
        elif not sirets.get(row["siret"], False):  # Inactive
            count_inactive_sirets_per_offerer_id.setdefault(row["offerer_id"], []).append(row["siret"])

    with open("output.csv", "w", encoding="utf-8") as f:
        csv_writer = csv.writer(f, dialect=csv.excel)
        csv_writer.writerow(["offerer_id", "active_siret", "inactive_sirets"])
        for offerer_id, linked_sirets in count_active_sirets_per_offerer_id.items():
            if len(linked_sirets) == 1:
                csv_writer.writerow(
                    [offerer_id, linked_sirets[0], str(count_inactive_sirets_per_offerer_id.get(offerer_id, []))[1:-1]]
                )


def main(not_dry: bool) -> None:
    logger.info("Starting")
    venue_sirets = fetch_venue_sirets_from_file()
    logger.info(f"Found {len(venue_sirets)} venue SIRETs")
    assert_active_sirets(venue_sirets)
    logger.info("Done")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
