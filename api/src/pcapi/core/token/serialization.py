from pcapi.routes.serialization import BaseModel


class ConnectAsInternalModel(BaseModel):
    redirect_link: str
    user_id: int
    internal_admin_email: str
    internal_admin_id: int
