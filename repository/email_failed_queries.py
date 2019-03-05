from datetime import datetime

from models import PcObject
from models.email_failed import EmailFailed


def save(email):
    email_failed = EmailFailed()
    email_failed.json = email
    email_failed.status = 'ERROR'
    email_failed.datetime = datetime.utcnow()
    PcObject.check_and_save(email_failed)
