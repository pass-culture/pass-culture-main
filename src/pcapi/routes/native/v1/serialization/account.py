from datetime import date
from typing import Optional

from pydantic import BaseModel


class AccountRequest(BaseModel):
    email: str
    password: str
    birthdate: date
    hasAllowedRecommendations: bool
    token: str


class UserProfileResponse(BaseModel):
    first_name: Optional[str]
    email: str
    is_beneficiary: bool
