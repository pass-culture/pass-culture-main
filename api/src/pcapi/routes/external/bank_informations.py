from pcapi.routes.apis import public_api
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes.dms import BankInformationDmsFormModel
from pcapi.validation.routes.dms import BankInformationDmsResponseModel
from pcapi.validation.routes.dms import require_dms_token
from pcapi.workers.bank_information_job import bank_information_job


@public_api.route("/bank_informations/venue/application_update", methods=["POST"])
@require_dms_token
@spectree_serialize(on_success_status=202, on_error_statuses=[400, 403])
def update_venue_demarches_simplifiees_application(
    form: BankInformationDmsFormModel,
) -> BankInformationDmsResponseModel:
    bank_information_job.delay(form.dossier_id, form.procedure_id)
    return BankInformationDmsResponseModel()
