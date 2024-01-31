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


def fill_adage_venue_addresses() -> None:
    count = 0

    for idx, chunk in enumerate(get_chunks(fetch_venues(), chunk_size=5_000), start=1):
        print(f"Round {idx}...")
        for venue in filter_known_venues(chunk):
            try:
                db.session.add(
                    AdageVenueAddress(
                        id=venue.id,
                        venueId=venue.id,
                        adageId=venue.adageId,
                        adageInscriptionDate=venue.adageInscriptionDate,
                    )
                )
            except Exception:
                db.session.rollback()
                print(f"Failed to add new AdageVenueAddress, round {idx}. Roll back...")
                raise

            count += 1

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            print(f"Failed to save changes to db, round {idx}. Roll back...")
            raise

        print(f"{count} new AdageVenueAddress created so far...")
