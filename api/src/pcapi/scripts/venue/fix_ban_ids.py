from collections import namedtuple
import json

import pydantic

from pcapi.connectors.api_adresse import RELIABLE_SCORE_THRESHOLD
from pcapi.connectors.api_adresse import format_q
from pcapi.connectors.api_adresse import search_csv
from pcapi.core.offerers.models import Venue
from pcapi.models import db


class ResultVenue(pydantic.BaseModel):
    venue_id: int
    venue_ban_id: str
    q: str
    result_id: str
    result_label: str
    result_score: float

    @pydantic.field_validator("result_score", mode="before")
    def get_result_score(cls, result_score: str) -> float:
        return float(result_score or 0)


def search_csv_venues(venues: list) -> list[ResultVenue]:
    lines = [",".join(["venue_id", "venue_ban_id", "q"])]
    for venue in venues:
        id_ = venue.id
        ban_id = venue.banId or ""
        address = venue.address or ""
        city = venue.city or ""
        q = format_q(address, city)
        lines.append(",".join([str(id_), ban_id, q]))
    payload = "\n".join(lines)
    results = search_csv(
        payload,
        columns=["q"],
        result_columns=["result_id", "result_label", "result_score"],
    )
    return [ResultVenue(**result) for result in results]


def split_on_fixable(mismatched_venues: list[ResultVenue]) -> tuple[list[ResultVenue], list[ResultVenue]]:
    fixable_venues = []
    non_fixable_venues = []
    for mismatched_venue in mismatched_venues:
        q = mismatched_venue.q
        result_id = mismatched_venue.result_id
        result_score = mismatched_venue.result_score
        is_housenumber = bool(result_id.count("_") in (2, 3))  # 3 is for bis / ter
        is_street = bool(q and not q[0].isdigit() and result_id.count("_") == 1)
        has_high_score = bool(result_score > RELIABLE_SCORE_THRESHOLD)
        if (is_housenumber or is_street) and has_high_score:
            fixable_venues.append(mismatched_venue)
        else:
            non_fixable_venues.append(mismatched_venue)
    print(f"{len(fixable_venues)=}")
    print(f"{len(non_fixable_venues)=}")
    return fixable_venues, non_fixable_venues


def fix_venues(permanent_venues: list, fixable_venues: list[ResultVenue]) -> None:
    d_fixable_venues = {fixable_venue.venue_id: fixable_venue for fixable_venue in fixable_venues}
    venues_to_update = []
    for permanent_venue in permanent_venues:
        id_ = permanent_venue.id
        if id_ in d_fixable_venues:
            permanent_venue.banId = d_fixable_venues[id_].result_id
            # TODO: fix permanent_venue.latitude and permanent_venue.longitude ?
            venues_to_update.append(permanent_venue)

    batch_size = 1000
    batches = [venues_to_update[i : i + batch_size] for i in range(0, len(venues_to_update), batch_size)]
    for batch in batches:
        for venue in batch:
            db.session.add(venue)
        db.session.commit()


def main(json_venues_path: str | None = None, dry_run: bool = True) -> tuple[list[ResultVenue], list[ResultVenue]]:
    # Load permanent venues:
    if json_venues_path:
        dry_run = True
        with open(json_venues_path, mode="r", encoding="utf-8") as f:
            venues = json.load(f)
        ObjVenue = namedtuple("ObjVenue", ["id", "banId", "address", "city"])
        permanent_venues = [
            ObjVenue(
                id=venue["Venue ID"],
                banId=venue["Ban ID"],
                address=venue["Venue Address"],
                city=venue["Venue City"],
            )
            for venue in venues
            if venue["Venue Is Permanent"] and not venue["Venue Is Virtual"]
        ]
    else:
        permanent_venues = Venue.query.filter(Venue.isPermanent == True, Venue.isVirtual == False).all()
    print(f"{len(permanent_venues)=}")

    # Search permanent venues in Base Adresse Nationale (BAN):
    results = search_csv_venues(permanent_venues)

    # Identify permanent venues with mismatched ban_id:
    mismatched_venues: list[ResultVenue] = []
    for result in results:
        if result.venue_ban_id != result.result_id:
            mismatched_venues.append(result)
    print(f"{len(mismatched_venues)=}")

    # Split between fixable and non-fixable mismatched venues:
    fixable_venues, non_fixable_venues = split_on_fixable(mismatched_venues)

    # Fix venues which are fixable:
    if not dry_run:
        fix_venues(permanent_venues, fixable_venues)

    return fixable_venues, non_fixable_venues
