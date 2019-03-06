from datetime import datetime

from models import PcObject
from models.email import Email


def save(content):
    email = Email()
    email.content = content
    email.status = 'ERROR'
    email.datetime = datetime.utcnow()
    PcObject.check_and_save(email)


def find_all_in_error():
    return Email.query.filter_by(status='ERROR').all()
