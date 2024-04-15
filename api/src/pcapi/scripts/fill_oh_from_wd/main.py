import argparse
from collections import namedtuple
import csv
import json
import logging
import os
import re

import pcapi.core.bookings.api  # avoid circular import  # pylint: disable=unused-import
import pcapi.core.history.api as history_api
import pcapi.core.offerers.api as offerers_api
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import Weekday
from pcapi.flask_app import app
from pcapi.models import db
import pcapi.routes.serialization.base as serialize_base
from pcapi.scripts.fill_oh_from_wd.opening_hours import DAYS
from pcapi.scripts.fill_oh_from_wd.opening_hours import FR_TO_EN_DAYS
from pcapi.scripts.fill_oh_from_wd.opening_hours import get_opening_hours
from pcapi.utils.date import numranges_to_readble_str


logger = logging.getLogger(__name__)

ObjVenue = namedtuple("ObjVenue", ["id", "withdrawalDetails"])


def _get_permanent_venues(json_venues_path: str | None = None) -> list[ObjVenue] | list[Venue]:
    if json_venues_path:
        with open(json_venues_path, mode="r", encoding="utf-8") as f:
            venues = json.load(f)
        permanent_venues = [
            ObjVenue(
                id=venue["Venue ID"],
                withdrawalDetails=venue["Venue Withdrawal Details"],
            )
            for venue in venues
            if venue["Venue Is Permanent"] and not venue["Venue Is Virtual"]
        ]
    else:
        permanent_venues = Venue.query.filter(Venue.isPermanent == True, Venue.isVirtual == False).all()
    logger.info("Permanent venues: %d", len(permanent_venues))
    return permanent_venues


def _get_venues_oh_in_wd(venues: list[ObjVenue] | list[Venue]) -> list[dict]:
    venues_oh_in_wd = []
    days = DAYS + (" we ", "weekend", "week-end", "tlj", "tous les jours")
    for venue in venues:
        withdrawal_details = venue.withdrawalDetails or ""
        groups = re.findall(rf"{'|'.join(days)}", withdrawal_details.lower())
        if groups:
            opening_hours = get_opening_hours(withdrawal_details)
            venues_oh_in_wd.append(
                {
                    "Venue ID": int(venue.id),
                    "Venue Withdrawal Details": withdrawal_details,
                    "Venue Opening Hours From Withdrawal Details": opening_hours,
                }
            )
    logger.info("Venues opening hours in withdrawal details: %d", len(venues_oh_in_wd))
    return venues_oh_in_wd


def _update_oh(venue: Venue, oh: dict) -> None:
    author = None
    venue_snapshot = history_api.ObjectUpdateSnapshot(venue, author)  # type: ignore
    for _day in DAYS:
        day = FR_TO_EN_DAYS[_day]
        if day not in oh:
            continue
        hours = oh[day]
        if hours is None:
            timespan = None
        else:
            timespan = [[hour["open"], hour["close"]] for hour in hours]
        opening_hours_data = serialize_base.OpeningHoursModel(weekday=day, timespan=timespan)

        weekday = Weekday(opening_hours_data.weekday)
        target = offerers_api.get_venue_opening_hours_by_weekday(venue, weekday)
        target.timespan = numranges_to_readble_str(target.timespan)
        venue_snapshot.trace_update(
            {
                "weekday": opening_hours_data.weekday,
                "timespan": numranges_to_readble_str(opening_hours_data.timespan),
            },
            target=target,
            field_name_template=f"openingHours.{opening_hours_data.weekday}.{{}}",
        )
        offerers_api.upsert_venue_opening_hours(venue, opening_hours_data)
    venue_snapshot.trace_update(
        {"comment": "Récupération des horaires d'ouverture depuis les modalités de retrait"},
    )
    venue_snapshot.add_action()


def _update_venues(permanent_venues: list[Venue], venues_oh_in_wd: list[dict]) -> None:
    d_venues_oh_in_wd = {venue_oh_in_wd["Venue ID"]: venue_oh_in_wd for venue_oh_in_wd in venues_oh_in_wd}
    existing_oh = 0
    new_oh = 0
    for permanent_venue in permanent_venues:
        if permanent_venue.opening_days and any(permanent_venue.opening_days.values()):
            existing_oh += 1
            continue
        venue_oh_in_wd = d_venues_oh_in_wd.get(permanent_venue.id)
        if not venue_oh_in_wd:
            continue

        oh = venue_oh_in_wd["Venue Opening Hours From Withdrawal Details"]
        if oh is None:
            continue

        _update_oh(permanent_venue, oh)
        new_oh += 1

        if new_oh % 1000 == 0:
            db.session.commit()

    db.session.commit()  # last chunk
    logger.info("Venues with existing opening hours: %d", existing_oh)
    logger.info("Venues with new opening hours: %d", new_oh)


def _format_oh(oh: dict[str, list[dict[str, str]] | None] | None) -> str | None:
    lines = []
    if not oh:
        return None
    for _day in DAYS:
        day = FR_TO_EN_DAYS[_day]
        if day not in oh:
            continue
        hours = oh[day]
        if not hours:
            h = "Fermé"
        else:
            h = " | ".join([hour["open"] + "-" + hour["close"] for hour in hours])
        lines.append(f"{_day:8s} : {h}")
    return "\n".join(lines)


def _export_to_csv(venues_oh_in_wd: list[dict]) -> None:
    output_directory = os.environ.get("OUTPUT_DIRECTORY", os.getcwd())
    output_path = os.path.join(output_directory, "results.csv")
    with open(output_path, mode="w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(
            [
                "Venue ID",
                "Venue Withdrawal Details",
                "Venue Opening Hours From Withdrawal Details",
            ]
        )
        for venue_oh_in_wd in venues_oh_in_wd:
            oh = venue_oh_in_wd["Venue Opening Hours From Withdrawal Details"]
            writer.writerow(
                [
                    venue_oh_in_wd["Venue ID"],
                    venue_oh_in_wd["Venue Withdrawal Details"],
                    _format_oh(oh),
                ]
            )
    logger.info("Exported results to csv")


def fill_oh_from_wd(
    json_venues_path: str | None = None, dry_run: bool = True, to_csv: bool = False
) -> list[dict[str, str]]:
    # 1) Get permanent venues:
    permanent_venues = _get_permanent_venues(json_venues_path=json_venues_path)

    # 2) Get venues opening hours in withdrawal details:
    venues_oh_in_wd = _get_venues_oh_in_wd(permanent_venues)

    # 3) Update venues:
    if not json_venues_path and not dry_run:
        _update_venues(permanent_venues, venues_oh_in_wd)  # type: ignore

    # 4) Export to csv:
    if to_csv:
        _export_to_csv(venues_oh_in_wd)

    return venues_oh_in_wd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--to-csv", action=argparse.BooleanOptionalAction, default=False)
    args = parser.parse_args()
    with app.app_context():
        fill_oh_from_wd(dry_run=args.dry_run, to_csv=args.to_csv)


if __name__ == "__main__":
    main()
