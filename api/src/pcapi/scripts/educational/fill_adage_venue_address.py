import typing

import sqlalchemy as sa

from pcapi.core.educational.models import AdageVenueAddress
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.utils.chunks import get_chunks


VenueGenerator = typing.Generator[Venue, None, None]


def fetch_venues() -> VenueGenerator:
    query = Venue.query.options(sa.orm.load_only(Venue.id, Venue.adageId, Venue.adageInscriptionDate)).yield_per(5_000)
    return (venue for venue in query)


def filter_known_venues(venues: typing.Collection[Venue]) -> VenueGenerator:
    ids = {venue.id for venue in venues}
    known_ids = {ava.venueId for ava in AdageVenueAddress.query.filter(AdageVenueAddress.venueId.in_(ids))}
    return (venue for venue in venues if venue.id not in known_ids)


def build_ava_data_from_venue(venue: Venue) -> dict:
    return {
        "id": venue.id,
        "venueId": venue.id,
        "adageId": venue.adageId,
        "adageInscriptionDate": venue.adageInscriptionDate
    }


def fill_adage_venue_addresses() -> None:
    count = 0

    connection = db.engine.connect()

    for idx, chunk in enumerate(get_chunks(fetch_venues(), chunk_size=5_000), start=1):
        print(f"Round {idx}...")

        addresses = [build_ava_data_from_venue(venue) for venue in filter_known_venues(chunk)]
        with db.engine.begin():
            db.engine.execute(AdageVenueAddress.__table__.insert(), addresses)

        print(f"{len(addresses)} new AdageVenueAddress created so far...")
