from pcapi.routes.serialization import BaseModel


class UpdateProAttributesRequest(BaseModel):
    email: str
    time_id: str  # see comment in update_pro_attributes_task
