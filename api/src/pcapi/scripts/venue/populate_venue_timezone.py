import logging
import math
import typing

import sqlalchemy.orm as sqla_orm

import pcapi.core.offerers.models as offerers_models
from pcapi.models import db


CHUNK_SIZE = 500

logger = logging.getLogger(__name__)


def populate_venue_timezone(from_venue_id: typing.Optional[int] = None) -> None:
    venues = _get_venues(from_venue_id)

    for venue in venues:
        venue.store_timezone()
        db.session.add(venue)


def _get_venues(from_venue_id: typing.Optional[int]) -> typing.Generator[offerers_models.Venue, None, None]:
    venue_query = offerers_models.Venue.query.options(
        sqla_orm.joinedload(offerers_models.Venue.managingOfferer)
    ).order_by(offerers_models.Venue.id)
    if from_venue_id:
        venue_query = venue_query.filter(offerers_models.Venue.id >= from_venue_id)

    venue_count = venue_query.count()
    max_chunk_index = math.ceil(venue_count / CHUNK_SIZE)
    logger.info("Venue count : %s", venue_count)
    logger.info("Chunk count : %s", max_chunk_index)

    for chunk_index in range(max_chunk_index):
        venues = venue_query.offset(chunk_index * CHUNK_SIZE).limit(CHUNK_SIZE)
        last_venue_id = None
        for venue in venues:
            last_venue_id = venue.id
            yield venue
        logger.info("Chunk %s/%s", chunk_index + 1, max_chunk_index)
        logger.info("Current progress %s%%", (chunk_index + 1) / max_chunk_index * 100)
        logger.info("Last venue id %s", last_venue_id)
        db.session.commit()
