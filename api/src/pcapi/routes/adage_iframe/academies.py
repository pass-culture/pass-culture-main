from pcapi.repository.session_management import atomic
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization import academies
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/collective/academies", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=academies.AcademiesResponseModel,
    api=blueprint.api,
)
@adage_jwt_required
def get_academies(authenticated_information: AuthenticatedInformation) -> academies.AcademiesResponseModel:
    return academies.AcademiesResponseModel.build()
