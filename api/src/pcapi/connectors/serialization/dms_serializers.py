import datetime

from pydantic import BaseModel
from pydantic import field_validator

from pcapi.connectors.dms import models as dms_models


class DMSWebhookRequest(BaseModel):
    procedure_id: int
    dossier_id: int
    state: dms_models.GraphQLApplicationStates
    updated_at: datetime.datetime

    @field_validator("updated_at", mode="before")
    def validate_udpated_at(cls, value: str) -> datetime.datetime:
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")
