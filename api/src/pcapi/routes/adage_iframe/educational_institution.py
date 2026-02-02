from pcapi.core.educational import repository
from pcapi.core.educational.api import institution as api
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import educational_institution
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic


@blueprint.adage_iframe.route("/collective/institution", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=educational_institution.EducationalInstitutionBudgetResponseModel,
    api=blueprint.api,
)
@adage_jwt_required
def get_educational_institution_with_budget(
    authenticated_information: AuthenticatedInformation,
) -> educational_institution.EducationalInstitutionBudgetResponseModel:
    if not authenticated_information.uai:
        raise ApiErrors({"code": "NOT ALLOWED"}, status_code=403)

    institution = repository.find_educational_institution_by_uai_code(authenticated_information.uai)
    if not institution:
        raise ApiErrors({"code": "INSTITUTION NOT FOUND"}, status_code=404)

    remaining_budget = api.get_current_year_remaining_credit(institution)

    return educational_institution.EducationalInstitutionBudgetResponseModel(budget=int(remaining_budget))
