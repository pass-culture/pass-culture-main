import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.schemas as offerers_schemas
import pcapi.core.offerers.structure_signup_api as structure_signup_api
from pcapi.routes.serialization import HttpBodyModel


# class SignupSimulationMessages:
#     importance_level: structure_signup_api.ImportanceLevelMessageSignupSimulation
#     content: structure_signup_api.ContentMessageSignupSimulation
class SignupSimulationMessages:
    importance_level: str
    content: str


class SignupSimulationResponseModel(HttpBodyModel):
    eligibility_documents: list[structure_signup_api.EligibilityDocuments]
    messages: list
    # messages: list[SignupSimulationMessages | None]


class SignupSimulationPayload(HttpBodyModel):
    siret: str
    isOpenToPublic: bool
    targets: list[str]
    activity: offerers_models.Activity


class LocationModelV2(HttpBodyModel, offerers_schemas.CoreLocationModelV2):
    pass


class StructureDataBodyModel(HttpBodyModel):
    siret: str
    siren: str | None
    name: str | None
    apeCode: str | None
    location: LocationModelV2 | None
    isDiffusible: bool
