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


FILEPATH = "StockEtablissementHistorique_utf8.csv"


def read_siret_file() -> typing.Generator[dict[str, str], None, None]:
    with open(FILEPATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, quoting=csv.QUOTE_NONE)
        for row in reader:
            yield row


def find_siret_status(venue_sirets: list[str]) -> dict[str, bool]:
    # The StockEtablissementHistorique_utf8 file is *huge* but the nice part is
    # it's sorted by SIRET so we can do a single pass
    sirets = {}
    rows = iter(read_siret_file())
    row = next(rows)
    for siret in venue_sirets:
        # Scrolls untill we go past the siret
        # siret may appear several times in the file, we want to scan all the linked rows
        while row["siret"] < siret:
            if (
                row["siret"] == siret
                and not row["dateFin"]
                and datetime.fromisoformat(row["dateFin"]) <= datetime.today()  # Discard passed entries
            ):
                sirets[siret] = row["etatAdministratifEtablissement"] == "A"  # A for Actif
            try:
                row = next(rows)
            except StopIteration:
                logger.warning("End of file reached")
                return sirets
    return sirets


def fetch_venue_sirets() -> list[str]:
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


def assert_active_sirets(existing_sirets: list[str]) -> None:
    logger.info("Reading the SIRET file")
    sirets = find_siret_status(existing_sirets)
    logger.info("Extracting active offerer's siren")
    count_active_sirets_per_siren: dict[str, list[str]] = {}

    for siret in existing_sirets:
        if sirets.get(siret, False):  # Active
            count_active_sirets_per_siren.setdefault(siret[:9], []).append(siret)

    for siren, linked_sirets in count_active_sirets_per_siren.items():
        if len(linked_sirets) == 1:
            logger.info(f"SIREN {siren} has only one active SIRET {linked_sirets[0]}")
        else:
            logger.info(f"SIREN {siren} has {len(linked_sirets)} active SIRETs")


def main(not_dry: bool) -> None:
    logger.info("Starting")
    venue_sirets = fetch_venue_sirets()
    logger.info(f"Found {len(venue_sirets)} venue SIRETs: {venue_sirets}")
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
