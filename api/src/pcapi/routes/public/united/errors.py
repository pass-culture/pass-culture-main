from pcapi.routes.serialization import BaseModel


class AuthErrorResponseModel(BaseModel):
    # only used as documentation for openapi
    errors: dict[str, str]
