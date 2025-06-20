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
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
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


def _write_modifications(modifications: list[tuple[int, str]], filename: str) -> None:
    # csv output to check what has been done and what failed
    output_file = f"{os.environ['OUTPUT_DIRECTORY']}/{filename}"
    logger.info("Exporting data to %s", output_file)

    with open(output_file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow([VENUE_ID_HEADER, "Modification"])
        writer.writerows(modifications)


def _get_offerer_active_pricing_point(venue_id: int, offerer_id: int) -> offerers_models.Venue | None:
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
    )
    # We need to check whether offerer has only one active pricing point
    if len(pricing_point.all()) == 1:
        return pricing_point.one()
    return None


def _add_pricing_point(rows: typing.Iterator[dict[str, str]]) -> None:
    logger.info("Adding pricing point to venues from pricing_point.csv")
    fails: list[tuple[int, str]] = []
    modifications: list[tuple[int, str]] = []
    data: dict[int, int] = {}

    # For each venue ids, we try to fetch the valid pricing point to link it to
    for row in rows:
        venue_id = int(row[VENUE_ID_HEADER])
        offerer_id = int(row[OFFERER_ID_HEADER])
        nb_siret_offerer = int(row[NB_SIRET_OFFERER_HEADER])

        # First check : does this venue still exist ?
        if not db.session.query(offerers_models.Venue).filter_by(id=venue_id).one_or_none():
            logger.warning("Venue %s not found, skipping...", venue_id)
            fails.append((venue_id, "Venue not found"))
            continue

        # If offerer has more than 1 SIRET, we don't want to proceed
        if nb_siret_offerer != 1:
            fails.append((venue_id, "More than 1 SIRET found on this offerer"))
            continue

        # Get Offerer's active pricing point
        if pricing_point := _get_offerer_active_pricing_point(venue_id=venue_id, offerer_id=offerer_id):
            data[venue_id] = pricing_point.id
        else:
            fails.append((venue_id, "Too many or no valid pricing points on this Offerer"))

    logger.info("Data length for pricing point: %s ", len(data))

    for venue_id, pricing_point_id in data.items():
        # create pricing point link on this venue
        new_link = offerers_models.VenuePricingPointLink(
            pricingPointId=pricing_point_id, venueId=int(venue_id), timespan=(datetime.utcnow(), None)
        )
        db.session.add(new_link)
        db.session.flush()
        # log this into action history + csv output file
        history_api.add_action(
            venue=new_link.venue,
            author=None,
            action_type=history_models.ActionType.VENUE_REGULARIZATION,
            comment="Pricing point added from venue with SIRET, please check extra data in database for more informations",
            extra_data={
                "modified_info": {"pricingPoint": {"old_info": None, "new_info": pricing_point_id}},
            },
        )
        modifications.append((venue_id, f"Pricing point {pricing_point_id} added"))
        logger.info("Updating venue %s pricing point id to %s", venue_id, pricing_point_id)

    _write_modifications(modifications=modifications, filename="add_pricing_point.csv")
    _write_modifications(modifications=fails, filename="add_pricing_point_fails.csv")


def _add_bank_account(rows: typing.Iterator[dict[str, str]]) -> None:
    logger.info("Adding bank account to venues from bank_account.csv")
    modifications: list[tuple[int, str]] = []
    fails: list[tuple[int, str]] = []
    data: dict[int, int] = {}

    # For each venue, we try to fetch the valid bank account to link it to
    for row in rows:
        venue_id = int(row[VENUE_ID_HEADER])
        venue: offerers_models.Venue = db.session.query(offerers_models.Venue).filter_by(id=venue_id).one_or_none()
        if not venue:
            logger.warning("Venue %s not found, skipping...", venue_id)
            fails.append((venue_id, "Venue not found"))
            continue
        offerer_id = venue.managingOffererId
        nb_activ_ba_offerer = int(row[NB_ACTIV_BA_OFFERER_HEADER])
        if nb_activ_ba_offerer != 1:
            fails.append((venue_id, "Too many active bank accounts on Offerer"))
            continue

        try:
            # Get Offerer's active bank account
            bank_account: finance_models.BankAccount = (
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
            ).one()  # should just be one given the above condition

        except orm_exc.NoResultFound:
            logger.error("No valid bank account for venue %d. ", venue_id)
            fails.append((venue_id, "No valid bank account for this venue"))

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

    logger.info("Data length for bank account: %s ", len(data))

    for venue_id, bank_account_id in data.items():
        # Create bank account link
        new_link = offerers_models.VenueBankAccountLink(
            bankAccountId=bank_account_id, venueId=venue_id, timespan=(datetime.utcnow(), None)
        )
        # log this into action history + csv output file
        db.session.add(new_link)
        db.session.flush()
        history_api.add_action(
            venue=new_link.venue,
            author=None,
            action_type=history_models.ActionType.VENUE_REGULARIZATION,
            bank_account=new_link.bankAccount,
            comment="Bank account added from venue with SIRET",
        )
        modifications.append((venue_id, f"Bank account{bank_account_id} added"))
        logger.info("Updating venue %d bank account id to %d", venue_id, bank_account_id)

    _write_modifications(modifications=modifications, filename="add_bank_account.csv")
    _write_modifications(modifications=fails, filename="add_bank_account_fails.csv")


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
