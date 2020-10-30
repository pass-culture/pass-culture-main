from pydantic import BaseModel


class SigninRequest(BaseModel):
    identifier: str
    password: str


class SigninResponse(BaseModel):
    refresh_token: str
    access_token: str
