from pcapi.routes.apis import public_api
from pcapi.routes.serialization.mailing_contacts_serialize import MailingContactBodyModel
from pcapi.routes.serialization.mailing_contacts_serialize import MailingContactResponseModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import expect_json_data
from pcapi.workers.mailing_contacts_job import mailing_contacts_job


@public_api.route("/mailing-contacts", methods=["POST"])
@spectree_serialize(response_model=MailingContactResponseModel, on_error_statuses=[400], on_success_status=201)
@expect_json_data
def save_mailing_contact(body: MailingContactBodyModel) -> MailingContactResponseModel:
    mailing_contacts_job.delay(body.email, body.dateOfBirth, body.departmentCode)
    return MailingContactResponseModel()
