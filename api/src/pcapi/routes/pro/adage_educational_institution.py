from pcapi.core.educational import repository
import pcapi.core.educational.api.institution as api
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.pro import adage_blueprint
from pcapi.routes.pro.adage_security import adage_jwt_required
from pcapi.routes.serialization import educational_institutions
from pcapi.routes.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@adage_blueprint.adage_iframe.route("/collective/institution", methods=["GET"])
@spectree_serialize(
    response_model=educational_institutions.EducationalInstitutionWithBudgetResponseModel,
    api=adage_blueprint.api,
)
@adage_jwt_required
def get_educational_institution_with_budget(
    authenticated_information: AuthenticatedInformation,
) -> educational_institutions.EducationalInstitutionWithBudgetResponseModel:
    if not authenticated_information.uai:
        raise ApiErrors({"code": "NOT ALLOWED"}, status_code=403)

    institution = repository.find_educational_institution_by_uai_code(authenticated_information.uai)
    if not institution:
        raise ApiErrors({"code": "INSTITUTION NOT FOUND"}, status_code=404)

    remaining_budget = api.get_current_year_remaining_credit(institution)

    return educational_institutions.EducationalInstitutionWithBudgetResponseModel(
        id=institution.id,
        name=institution.name,
        institutionType=institution.institutionType,
        postalCode=institution.postalCode,
        city=institution.city,
        phoneNumber=institution.phoneNumber,
        budget=int(remaining_budget),
    )
