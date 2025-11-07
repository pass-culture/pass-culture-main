import logging
import uuid

from psycopg2.extras import DateRange

from pcapi.core import object_storage

from . import models


logger = logging.getLogger(__name__)


def create_highlight(
    name: str,
    description: str,
    availability_datespan: DateRange,
    highlight_datespan: DateRange,
    image_as_bytes: bytes,
    image_mimetype: str,
) -> models.Highlight:
    image_id = str(uuid.uuid4())
    highlight = models.Highlight(
        name=name,
        description=description,
        availability_datespan=availability_datespan,
        highlight_datespan=highlight_datespan,
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
    availability_datespan: DateRange,
    highlight_datespan: DateRange,
    image_as_bytes: bytes | None,
    image_mimetype: str | None,
) -> models.Highlight:
    highlight.name = name
    highlight.description = description
    highlight.availability_datespan = availability_datespan
    highlight.highlight_datespan = highlight_datespan
    if image_as_bytes and image_mimetype:
        object_storage.delete_public_object(folder="highlights", object_id=highlight.mediation_uuid)
        image_id = str(uuid.uuid4())
        highlight.mediation_uuid = image_id
        object_storage.store_public_object(
            folder="highlights", object_id=image_id, blob=image_as_bytes, content_type=image_mimetype
        )
    return highlight
