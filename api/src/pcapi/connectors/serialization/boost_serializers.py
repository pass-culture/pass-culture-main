from pcapi.routes.serialization import BaseModel


class LoginBoost(BaseModel):
    code: int
    message: str
    token: str | None
