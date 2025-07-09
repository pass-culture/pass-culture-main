import argparse
import csv
import logging
import os

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils import human_ids


logger = logging.getLogger(__name__)


def extract_venues_changed_bank_account(year: int, month: int, half: int) -> list[dict]:
    assert half in (1, 2)  # should be either 1st or 2nd half of the month

    upper_field = sa.func.upper(offerers_models.VenueBankAccountLink.timespan)
    upper_day_field = sa.func.extract("day", upper_field)

    deprecation_links = (
        db.session.query(offerers_models.VenueBankAccountLink)
        .filter(
            sa.func.extract("year", upper_field) == year,
            sa.func.extract("month", upper_field) == month,
            (upper_day_field < 16) if half == 1 else (upper_day_field > 15),
        )
        .order_by(
            upper_field,
        )
        .all()
    )

    venue_bank_accounts_dict = {}
    for deprecation_link in deprecation_links:
        if deprecation_link.venueId in venue_bank_accounts_dict:
            continue
        venue_bank_accounts_dict[deprecation_link.venueId] = {
            "old_bank_account_id": deprecation_link.bankAccountId,
            "new_bank_account_ids": [],
        }

    lower_field = sa.func.lower(offerers_models.VenueBankAccountLink.timespan)
    lower_day_field = sa.func.extract("day", lower_field)
    for venue_id in venue_bank_accounts_dict:
        venue_links = (
            db.session.query(offerers_models.VenueBankAccountLink)
            .filter(
                sa.func.extract("year", lower_field) == year,
                sa.func.extract("month", lower_field) == month,
                (lower_day_field < 16) if half == 1 else (lower_day_field > 15),
                offerers_models.VenueBankAccountLink.venueId == venue_id,
            )
            .order_by(lower_field)
            .all()
        )
        for venue_link in venue_links:
            venue_bank_accounts_dict[venue_id]["new_bank_account_ids"].append(venue_link.bankAccountId)

    bank_account_ids = [e["old_bank_account_id"] for e in venue_bank_accounts_dict.values()]
    bank_account_ids += sum([e["new_bank_account_ids"] for e in venue_bank_accounts_dict.values()], [])
    bank_accounts = (
        db.session.query(finance_models.BankAccount).filter(finance_models.BankAccount.id.in_(bank_account_ids)).all()
    )
    bank_accounts_dict = {b.id: b for b in bank_accounts}

    venues = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id.in_(list(venue_bank_accounts_dict)))
        .all()
    )
    venues_dict = {v.id: v for v in venues}

    res = []
    for venue_id, changed_bank_accounts_dict in venue_bank_accounts_dict.items():
        venue = venues_dict[venue_id]
        old_bank_account_id = changed_bank_accounts_dict["old_bank_account_id"]
        entry = {
            "venue_id": venue_id,
            "venue_name": venue.name,
            "old_bank_account_id": old_bank_account_id,
            "old_bank_account_humanized_id": human_ids.humanize(changed_bank_accounts_dict["old_bank_account_id"]),
            "old_bank_account_iban": bank_accounts_dict[old_bank_account_id].iban,
        }

        for i, bank_account_id in enumerate(changed_bank_accounts_dict["new_bank_account_ids"], 1):
            entry[f"new_bank_account{i}_id"] = bank_account_id
            entry[f"new_bank_account{i}_humanized_id"] = human_ids.humanize(bank_account_id)
            entry[f"new_bank_account{i}_iban"] = bank_accounts_dict[bank_account_id].iban

        res.append(entry)

    return res


def get_csv_headers(entries: list[dict]) -> list[str]:
    longest_entry_len = max(len(e) for e in entries)
    return [list(e) for e in entries if len(e) == longest_entry_len][0]


def extract(year: int) -> None:
    # os.environ["OUTPUT_DIRECTORY"] = "."
    for month in range(1, 13):
        for half in (1, 2):
            filename = (
                f"{os.environ['OUTPUT_DIRECTORY']}/export_venues_changed_bank_account_{year}_{month:02}_{half}.csv"
            )
            venues_list = extract_venues_changed_bank_account(year, month, half)
            if not venues_list:
                continue
            logger.info("Exporting data to %s", filename)
            headers = get_csv_headers(venues_list)
            with open(filename, "w", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                for row in venues_list:
                    writer.writerow(row)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    args = parser.parse_args()

    extract(args.year)
