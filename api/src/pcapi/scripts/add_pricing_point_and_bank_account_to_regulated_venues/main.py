"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-35951-add-pricing-point-and-bank-account-to-regulated-venues/api/src/pcapi/scripts/add_pricing_point_and_bank_account_to_regulated_venues/main.py

"""

import argparse
import csv
import logging
import os
import typing
from datetime import datetime

from sqlalchemy.orm import exc as orm_exc

import pcapi.core.finance.models as finance_models
from pcapi.app import app
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)

VENUE_ID_HEADER = "venue_id"
OFFERER_ID_HEADER = "offerer_id"
NB_ACTIV_BA_OFFERER_HEADER = "nb_activ_ba_offerer"
NB_SIRET_OFFERER_HEADER = "nb_siret_offerer"


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def mock_csv(venues: list[offerers_models.Venue]) -> typing.Iterator[dict[str, str]]:
    for venue in venues:
        nb_siret_offerer = (
            db.session.query(offerers_models.Venue)
            .filter(
                offerers_models.Venue.managingOfferer == venue.managingOfferer,
                offerers_models.Venue.siret.isnot(None),
            )
            .count()
        )

        nb_activ_ba_offerer = (
            db.session.query(offerers_models.VenueBankAccountLink)
            .join(offerers_models.Venue, offerers_models.VenueBankAccountLink.venue)
            .filter(
                offerers_models.Venue.managingOfferer == venue.managingOfferer,
                offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
            )
            .count()
        )

        yield {
            "venue_id": str(venue.id),
            "offerer_id": str(venue.managingOfferer.id),
            "nb_activ_ba_offerer": str(nb_activ_ba_offerer),
            "nb_siret_offerer": str(nb_siret_offerer),
        }


def _add_pricing_point(rows: typing.Iterator[dict[str, str]]) -> None:
    data: dict[int, int] = {}
    for row in rows:
        try:
            venue_id = int(row[VENUE_ID_HEADER])
            offerer_id = int(row[OFFERER_ID_HEADER])
            nb_siret_offerer = int(row[NB_SIRET_OFFERER_HEADER])

            # If offerer has more than 1 SIRET, we don't want to proceed
            if nb_siret_offerer != 1:
                continue

            # Get Offerer's active pricing point
            pricing_point = (
                db.session.query(offerers_models.Venue)
                .join(
                    offerers_models.VenuePricingPointLink,
                    offerers_models.Venue.id == offerers_models.VenuePricingPointLink.venueId,
                )
                .filter(
                    offerers_models.Venue.managingOffererId == offerer_id,
                    offerers_models.Venue.id != venue_id,
                    offerers_models.Venue.siret.is_not(None),
                    offerers_models.VenuePricingPointLink.timespan.contains(datetime.utcnow()),
                )
                .one()
            )

            data[venue_id] = pricing_point.id

        except orm_exc.NoResultFound:
            logger.error("No valid pricing point found for venue %d. ", venue_id)

    for venue_id, pricing_point_id in data.items():
        # create pricing point link on this venue
        new_link = offerers_models.VenuePricingPointLink(
            pricingPointId=pricing_point_id, venueId=int(venue_id), timespan=(datetime.utcnow(), None)
        )
        db.session.add(new_link)
        logger.info("Updating venue %d pricing point id to %d", venue_id, pricing_point_id)


def _add_bank_account(rows: typing.Iterator[dict[str, str]]) -> None:
    data: dict[int, int] = {}
    for row in rows:
        try:
            venue_id = int(row[VENUE_ID_HEADER])
            offerer_id = int(row[OFFERER_ID_HEADER])
            nb_activ_ba_offerer = int(row[NB_ACTIV_BA_OFFERER_HEADER])
            if nb_activ_ba_offerer != 1:
                continue

            # Get Offerer's active bank account
            bank_account = (
                db.session.query(finance_models.BankAccount)
                .join(
                    offerers_models.VenueBankAccountLink,
                    finance_models.BankAccount.id == offerers_models.VenueBankAccountLink.bankAccountId,
                )
                .join(
                    offerers_models.Venue,
                    offerers_models.VenueBankAccountLink.venueId == offerers_models.Venue.id,
                )
                .filter(
                    offerers_models.VenueBankAccountLink.timespan.contains(datetime.utcnow()),
                    offerers_models.Venue.managingOffererId == offerer_id,
                    offerers_models.Venue.id != venue_id,
                )
                .one()
            )

            # Get all venues with no active BA to link to offerer's active bank account
            venues_to_update = (
                db.session.query(offerers_models.Venue)
                .outerjoin(
                    offerers_models.VenueBankAccountLink,
                )
                .filter(
                    offerers_models.VenueBankAccountLink.id.is_(None),
                    offerers_models.Venue.managingOffererId == offerer_id,
                )
            ).all()

            for venue in venues_to_update:
                data[venue.id] = bank_account.id

        except orm_exc.NoResultFound:
            logger.error("No valid pricing point found for venue %d. ", venue_id)

    for venue_id, bank_account_id in data.items():
        # Create bank account link
        new_link = offerers_models.VenueBankAccountLink(
            bankAccountId=bank_account_id, venueId=venue_id, timespan=(datetime.utcnow(), None)
        )
        db.session.add(new_link)
        logger.info("Updating venue %d bank account id to %d", venue_id, bank_account_id)


def main(not_dry: bool) -> None:
    _add_pricing_point(_read_csv_file("pricing_point"))
    _add_bank_account(_read_csv_file("bank_account"))


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
