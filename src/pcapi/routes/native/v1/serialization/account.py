from pydantic import BaseModel


class PasswordResetRequestModel(BaseModel):
    email: str
