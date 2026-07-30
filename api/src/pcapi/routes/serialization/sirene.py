import pydantic as pydantic_v2

from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offerers import structure_signup_api
from pcapi.routes.serialization import HttpBodyModel
from pcapi.serialization.utils import SiretField


class SignupSimulationMessageModel(HttpBodyModel):
    level: structure_signup_api.SignupSimulationMessageLevel
    type: structure_signup_api.SignupSimulationMessageType


class SignupSimulationResponseModel(HttpBodyModel):
    eligibility_documents: list[structure_signup_api.EligibilityDocument]
    messages: list[SignupSimulationMessageModel]


class SignupSimulationPayload(HttpBodyModel):
    siret: SiretField
    is_open_to_public: bool
    targets: list[offerers_models.OffererTarget] = pydantic_v2.Field(min_length=1, max_length=2)
    activity: offerers_models.ActivityOpenToPublic | offerers_models.ActivityNotOpenToPublic


class LocationModelV2(HttpBodyModel, offerers_schemas.CoreLocationModelV2):
    pass


class StructureDataBodyModel(HttpBodyModel):
    siret: SiretField
    siren: str | None
    name: str | None
    apeCode: str | None
    location: LocationModelV2 | None
    isDiffusible: bool
