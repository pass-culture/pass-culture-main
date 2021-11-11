from typing import Optional

from pydantic import BaseModel


class VenueResponse(BaseModel):
    id: int
    publicName: Optional[str]
    name: str

    class Config:
        orm_mode = True
