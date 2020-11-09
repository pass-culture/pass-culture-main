from pydantic import BaseModel  # pylint: disable=no-name-in-module


class SigninRequest(BaseModel):
    identifier: str
    password: str


class SigninResponse(BaseModel):
    refresh_token: str
    access_token: str


class RefreshResponse(BaseModel):
    access_token: str


class PasswordResetRequestRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    reset_password_token: str
    new_password: str
