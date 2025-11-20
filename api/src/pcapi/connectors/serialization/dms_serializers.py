import datetime

import pydantic.v1 as pydantic_v1

from pcapi.connectors.dms import models as dms_models


class DMSWebhookRequest(pydantic_v1.BaseModel):
    procedure_id: int
    dossier_id: int
    state: dms_models.GraphQLApplicationStates
    updated_at: datetime.datetime

    @pydantic_v1.validator("updated_at", pre=True)
    def validate_udpated_at(cls, value: str) -> datetime.datetime:
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")
