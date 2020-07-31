from rq.decorators import job

from workers import worker
from workers.decorators import job_context, log_job
from infrastructure.container import add_contact_in_eligibility_list


@job(worker.redis_queue, connection=worker.conn)
@job_context
@log_job
def mailing_contacts_job(contact_email: str, contact_date_of_birth: str, contact_department_code: str) -> None:
    add_contact_in_eligibility_list.execute(contact_email, contact_date_of_birth, contact_department_code)
