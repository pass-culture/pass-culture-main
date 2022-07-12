from pcapi.routes.serialization import BaseModel


class VenueResponse(BaseModel):
    id: int
    publicName: str | None
    name: str

    class Config:
        orm_mode = True
