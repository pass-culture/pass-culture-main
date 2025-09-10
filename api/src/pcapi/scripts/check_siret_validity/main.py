"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37784-api-regarder-sur-les-offerer-avec-plusieurs-siret-combien-dofferer-ont-vraiment-plusieurs-siret-actifs/api/src/pcapi/scripts/check_siret_validity/main.py

"""

import argparse
import csv
import dataclasses
import logging
import os
import time

import pcapi.connectors.entreprise.api as enterprise_api
import pcapi.core.offerers.models as offerer_models
from pcapi.app import app
from pcapi.models import db
from pcapi.utils import siren as siren_utils


logger = logging.getLogger(__name__)


OFFERER_IDS_TO_CHECK = (
    14080,
    8320,
    1026,
    40768,
    1859,
    4101,
    4036,
    47683,
    4107,
    32269,
    5133,
    24269,
    9934,
    207,
    3261,
    4025,
    9251,
    23592,
    13097,
    9320,
    26349,
    11118,
    4078,
    1908,
    28916,
    11001,
    16120,
    15929,
    317,
)


@dataclasses.dataclass
class Siret:
    siret: str
    is_active: bool


def main(dry_run: bool) -> None:
    valid_sirets_per_offerer: dict[int, list[Siret]] = {}
    for offerer_id, siret in (
        db.session.query(offerer_models.Venue)
        .filter(offerer_models.Venue.managingOffererId.in_(OFFERER_IDS_TO_CHECK))
        .order_by(offerer_models.Venue.managingOffererId)
        .with_entities(offerer_models.Venue.managingOffererId, offerer_models.Venue.siret)
        .all()
    ):
        if siret:
            if siren_utils.is_valid_siret(siret):
                valid_sirets_per_offerer.setdefault(offerer_id, []).append(Siret(siret=siret, is_active=False))
            else:
                logger.warning("Invalid siret %s for offerer %d", siret, offerer_id)

    for offerer_id, sirets in valid_sirets_per_offerer.items():
        for siret in sirets:
            if siret.siret[:9] == "853318459":
                print(f"siret {siret.siret} for offerer {offerer_id} skipped")
                continue
            siret_info = enterprise_api.get_siret(siret.siret)
            if siret_info.active:
                siret.is_active = True
            time.sleep(1)

    output_file = f"{os.environ['OUTPUT_DIRECTORY']}/siret_validity_results.csv"
    logger.info("Exporting data to %s", output_file)

    with open(output_file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["offerer_id", "siret", "is_active"])
        writer.writerows(
            row
            for offerer_id, sirets in valid_sirets_per_offerer.items()
            for row in ((offerer_id, siret.siret, siret.is_active) for siret in sirets)
        )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()
    dry_run = not args.not_dry

    main(dry_run=dry_run)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
