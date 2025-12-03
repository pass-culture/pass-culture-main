import datetime
import logging
import uuid

from psycopg2.extras import DateRange

from pcapi.core import object_storage
from pcapi.core.highlights import repository as highlights_repository
from pcapi.core.mails import transactional as transactional_mails

from . import models


logger = logging.getLogger(__name__)


def create_highlight(
    name: str,
    description: str,
    availability_datespan: DateRange,
    highlight_datespan: DateRange,
    communication_date: datetime.date,
    image_as_bytes: bytes,
    image_mimetype: str,
) -> models.Highlight:
    image_id = str(uuid.uuid4())
    highlight = models.Highlight(
        name=name,
        description=description,
        availability_datespan=availability_datespan,
        highlight_datespan=highlight_datespan,
        communication_date=communication_date,
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
    communication_date: datetime.date,
    image_as_bytes: bytes | None,
    image_mimetype: str | None,
) -> models.Highlight:
    highlight.name = name
    highlight.description = description
    highlight.availability_datespan = availability_datespan
    highlight.communication_date = communication_date
    highlight.highlight_datespan = highlight_datespan
    if image_as_bytes and image_mimetype:
        object_storage.delete_public_object(folder="highlights", object_id=highlight.mediation_uuid)
        image_id = str(uuid.uuid4())
        highlight.mediation_uuid = image_id
        object_storage.store_public_object(
            folder="highlights", object_id=image_id, blob=image_as_bytes, content_type=image_mimetype
        )
    return highlight


def send_email_for_highlight_with_communication_date_set_to_today() -> None:
    requests_for_today_highlights = highlights_repository.get_today_highlight_requests()
    for highlight_request in requests_for_today_highlights:
        transactional_mails.send_highlight_communication_email_to_pro(highlight_request.offer)
