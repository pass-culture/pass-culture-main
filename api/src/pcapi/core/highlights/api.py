import logging
import uuid

from psycopg2.extras import DateTimeRange

from pcapi.core import object_storage

from . import models


logger = logging.getLogger(__name__)


def create_highlight(
    name: str,
    description: str,
    availability_timespan: DateTimeRange,
    highlight_timespan: DateTimeRange,
    image_as_bytes: bytes,
    image_mimetype: str,
) -> models.Highlight:
    image_id = str(uuid.uuid4())
    highlight = models.Highlight(
        name=name,
        description=description,
        availability_timespan=availability_timespan,
        highlight_timespan=highlight_timespan,
        mediation_uuid=image_id,
    )
    object_storage.store_public_object(
        folder="highlights", object_id=image_id, blob=image_as_bytes, content_type=image_mimetype
    )

    return highlight


def update_highlight(
    highlight: models.Highlight,
    name: str,
    description: str,
    availability_timespan: DateTimeRange,
    highlight_timespan: DateTimeRange,
    image_as_bytes: bytes | None,
    image_mimetype: str | None,
) -> models.Highlight:
    highlight.name = name
    highlight.description = description
    highlight.availability_timespan = availability_timespan
    highlight.highlight_timespan = highlight_timespan
    if image_as_bytes and image_mimetype:
        object_storage.delete_public_object(folder="highlights", object_id=highlight.mediation_uuid)
        image_id = str(uuid.uuid4())
        highlight.mediation_uuid = image_id
        object_storage.store_public_object(
            folder="highlights", object_id=image_id, blob=image_as_bytes, content_type=image_mimetype
        )
    return highlight
