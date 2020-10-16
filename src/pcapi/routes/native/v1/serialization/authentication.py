from pydantic import BaseModel


class SigninRequestModel(BaseModel):
    identifier: str
    password: str


class SigninResponseModel(BaseModel):
    pass
