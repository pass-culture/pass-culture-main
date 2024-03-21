from collections import namedtuple
import json
import logging

import pydantic

from pcapi.connectors.api_adresse import RELIABLE_SCORE_THRESHOLD
from pcapi.connectors.api_adresse import ResultColumn
from pcapi.connectors.api_adresse import format_payload
from pcapi.connectors.api_adresse import format_q
from pcapi.connectors.api_adresse import search_csv
from pcapi.core.offerers.models import Venue
from pcapi.models import db


logger = logging.getLogger(__name__)

ObjVenue = namedtuple("ObjVenue", ["id", "banId", "address", "city"])


class SearchedVenue(pydantic.BaseModel):
    venue_id: int
    venue_ban_id: str
    q: str
    latitude: float
    longitude: float
    result_id: str
    result_label: str
    result_score: float

    @pydantic.field_validator("result_score", "latitude", "longitude", mode="before")
    def to_float(cls, s: str) -> float:
        return float(s or 0)


def _get_permanent_venues(json_venues_path: str | None = None) -> list[ObjVenue] | list[Venue]:
    if json_venues_path:
        with open(json_venues_path, mode="r", encoding="utf-8") as f:
            venues = json.load(f)
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
    logger.info("Permanent venues: %d", len(permanent_venues))
    return permanent_venues


def _search_csv_venues(venues: list[ObjVenue] | list[Venue]) -> list[SearchedVenue]:
    headers = ["venue_id", "venue_ban_id", "q"]
    lines = []
    for venue in venues:
        id_ = venue.id
        ban_id = venue.banId or ""
        address = venue.address or ""
        city = venue.city or ""
        q = format_q(address, city)
        lines.append(
            {
                "venue_id": id_,
                "venue_ban_id": ban_id,
                "q": q,
            }
        )
    payload = format_payload(headers, lines)
    results = search_csv(
        payload,
        columns=["q"],
        result_columns=[
            ResultColumn.LATITUDE,
            ResultColumn.LONGITUDE,
            ResultColumn.RESULT_ID,
            ResultColumn.RESULT_LABEL,
            ResultColumn.RESULT_SCORE,
        ],
    )
    searched_venues = [SearchedVenue(**result) for result in results]
    logger.info("Searched venues: %d", len(searched_venues))
    return searched_venues


def _get_mismatched_venues(searched_venues: list[SearchedVenue]) -> list[SearchedVenue]:
    mismatched_venues = [
        searched_venue for searched_venue in searched_venues if searched_venue.venue_ban_id != searched_venue.result_id
    ]
    logger.info("Mismatched venues: %d", len(mismatched_venues))
    return mismatched_venues


def _split_venues_on_fixable(
    mismatched_venues: list[SearchedVenue],
) -> tuple[list[SearchedVenue], list[SearchedVenue]]:
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
    logger.info("Fixable venues: %d", len(fixable_venues))
    logger.info("Non-fixable venues: %d", len(non_fixable_venues))
    return fixable_venues, non_fixable_venues


def _fix_venues(permanent_venues: list[Venue], fixable_venues: list[SearchedVenue]) -> None:
    d_fixable_venues = {fixable_venue.venue_id: fixable_venue for fixable_venue in fixable_venues}
    venues_to_update = []
    for permanent_venue in permanent_venues:
        fixable_venue = d_fixable_venues.get(permanent_venue.id)
        if not fixable_venue:
            continue
        permanent_venue.banId = fixable_venue.result_id
        permanent_venue.latitude = fixable_venue.latitude
        permanent_venue.longitude = fixable_venue.longitude
        venues_to_update.append(permanent_venue)

    batch_size = 1000
    batches = [venues_to_update[i : i + batch_size] for i in range(0, len(venues_to_update), batch_size)]
    for batch in batches:
        for venue in batch:
            db.session.add(venue)
        db.session.commit()


def main(
    json_venues_path: str | None = None,
    dry_run: bool = True,
) -> tuple[list[SearchedVenue], list[SearchedVenue]]:
    # 1) Get permanent venues:
    permanent_venues = _get_permanent_venues(json_venues_path=json_venues_path)

    # 2) Search permanent venues in Base Adresse Nationale (BAN):
    searched_venues = _search_csv_venues(permanent_venues)

    # 3) Identify permanent venues with mismatched ban_id:
    mismatched_venues = _get_mismatched_venues(searched_venues)

    # 4) Split between fixable and non-fixable mismatched venues:
    fixable_venues, non_fixable_venues = _split_venues_on_fixable(mismatched_venues)

    # 5) Fix venues which are fixable:
    if not json_venues_path and not dry_run:
        _fix_venues(permanent_venues, fixable_venues)  # type: ignore

    return fixable_venues, non_fixable_venues
