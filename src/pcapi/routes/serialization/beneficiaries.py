from pydantic import BaseModel  # pylint: disable=no-name-in-module


class ApplicationUpdateRequest(BaseModel):
    id: str


class ApplicationUpdateResponse(BaseModel):
    pass
