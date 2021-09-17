from pydantic import BaseModel


class VenueResponse(BaseModel):
    id: int
    publicName: str
    name: str

    class Config:
        orm_mode = True
