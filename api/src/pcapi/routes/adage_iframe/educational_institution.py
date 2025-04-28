from pcapi.core.educational import repository
import pcapi.core.educational.api.institution as api
from pcapi.models.api_errors import ApiErrors
from pcapi.repository.session_management import atomic
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import educational_institution
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/collective/institution", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=educational_institution.EducationalInstitutionWithBudgetResponseModel,
    api=blueprint.api,
)
@adage_jwt_required
def get_educational_institution_with_budget(
    authenticated_information: AuthenticatedInformation,
) -> educational_institution.EducationalInstitutionWithBudgetResponseModel:
    if not authenticated_information.uai:
        raise ApiErrors({"code": "NOT ALLOWED"}, status_code=403)

    institution = repository.find_educational_institution_by_uai_code(authenticated_information.uai)
    if not institution:
        raise ApiErrors({"code": "INSTITUTION NOT FOUND"}, status_code=404)

    remaining_budget = api.get_current_year_remaining_credit(institution)

    return educational_institution.EducationalInstitutionWithBudgetResponseModel(
        id=institution.id,
        name=institution.name,
        institutionType=institution.institutionType,
        postalCode=institution.postalCode,
        city=institution.city,
        phoneNumber=institution.phoneNumber,
        budget=int(remaining_budget),
    )
