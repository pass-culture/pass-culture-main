from datetime import datetime
from typing import List

from models import PcObject
from models.email import Email, EmailStatus
from models.pc_object import serialize


def save(content: dict, status: str):
    email = Email()
    email.content = content
    email.status = status
    email.datetime = serialize(datetime.utcnow())
    PcObject.check_and_save(email)


def find_all_in_error() -> List[Email]:
    return Email.query.filter_by(status=EmailStatus.ERROR).all()
