from pcapi.routes.pro import adage_blueprint
from pcapi.routes.pro.adage_security import adage_jwt_required
from pcapi.routes.serialization import academies
from pcapi.routes.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@adage_blueprint.adage_iframe.route("/collective/academies", methods=["GET"])
@spectree_serialize(
    response_model=academies.AcademiesResponseModel,
    api=adage_blueprint.api,
)
@adage_jwt_required
def get_academies(
    authenticated_information: AuthenticatedInformation,
) -> academies.AcademiesResponseModel:
    return academies.AcademiesResponseModel.build()
