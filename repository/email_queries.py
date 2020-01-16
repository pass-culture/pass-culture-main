from datetime import datetime
from typing import List

from models.email import Email, EmailStatus
from repository.repository import Repository
from utils.date import format_into_ISO_8601


def save(content: dict, status: EmailStatus):
    email = Email()
    email.content = content
    email.status = status
    email.datetime = format_into_ISO_8601(datetime.utcnow())
    Repository.save(email)


def find_all_in_error() -> List[Email]:
    return Email.query.filter_by(status=EmailStatus.ERROR).all()
