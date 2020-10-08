from datetime import datetime

from pcapi.models.email import Email, EmailStatus
from pcapi.repository import repository
from pcapi.utils.date import format_into_utc_date


def save(content: dict, status: EmailStatus):
    email = Email()
    email.content = content
    email.status = status
    email.datetime = format_into_utc_date(datetime.utcnow())
    repository.save(email)
