import datetime

from rq.decorators import job

from pcapi import settings
from pcapi.core import mails
from pcapi.workers import worker
from pcapi.workers.decorators import job_context
from pcapi.workers.decorators import log_job


@job(worker.default_queue, connection=worker.conn)
@job_context
@log_job
def mailing_contacts_job(contact_email: str, contact_date_of_birth: str, contact_department_code: str) -> None:
    _create_mailing_contact(contact_email, contact_date_of_birth, contact_department_code)
    _add_contact_to_eligible_soon_list(contact_email)


def _create_mailing_contact(email: str, birth_date: str, department: str) -> None:
    response = mails.create_contact(email)
    # FIXME (dbaty, 2020-02-03): I doubt that a 400 status code means
    # a success. Ditto below with the call to `update_contact()` and
    # in `_add_contact_to_eligible_soon_list()`. Also, we should probably
    # accept all 2xx status codes.
    if response.status_code not in (201, 400):
        raise ValueError(
            "Got error %d from Mailjet while creating contact: %s" % (response.status_code, response.content)
        )

    birth_date = datetime.date.fromisoformat(birth_date)
    response = mails.update_contact(email, birth_date=birth_date, department=department)
    if response.status_code not in (200, 400):
        raise ValueError(
            "Got error %d from Mailjet while updating contact: %s" % (response.status_code, response.content)
        )


def _add_contact_to_eligible_soon_list(email) -> None:
    response = mails.add_contact_to_list(email, settings.MAILJET_NOT_YET_ELIGIBLE_LIST_ID)
    if response.status_code not in (201, 400):
        raise ValueError(
            "Got error %d from Mailjet while adding contact to list: %s" % (response.status_code, response.content)
        )
