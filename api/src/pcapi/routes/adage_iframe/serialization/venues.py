from typing import Optional

from pcapi.routes.serialization import BaseModel


class VenueResponse(BaseModel):
    id: int
    publicName: Optional[str]
    name: str

    class Config:
        orm_mode = True
