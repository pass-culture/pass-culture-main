from typing import Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module


class UserProfileResponse(BaseModel):
    first_name: Optional[str]
    email: str
