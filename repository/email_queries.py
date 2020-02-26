from datetime import datetime

from models.email import Email, EmailStatus
from repository import repository
from utils.date import format_into_ISO_8601


def save(content: dict, status: EmailStatus):
    email = Email()
    email.content = content
    email.status = status
    email.datetime = format_into_ISO_8601(datetime.utcnow())
    repository.save(email)
