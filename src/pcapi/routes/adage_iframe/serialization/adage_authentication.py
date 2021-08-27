from typing import Optional

from pydantic import BaseModel


class AuthenticatedInformation(BaseModel):
    civility: str
    lastname: str
    firstname: str
    email: str
    uai: Optional[str]
