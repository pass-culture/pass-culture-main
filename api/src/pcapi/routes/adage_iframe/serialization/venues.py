from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel


class GetRelativeVenuesQueryModel(BaseModel):
    getRelative: bool = False


class VenueResponse(BaseModel):
    id: int
    publicName: str | None
    name: str
    relative: list[int]
    bannerUrl: str | None
    bannerMeta: dict | None

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue, relative: list[int] | None = None) -> "VenueResponse":
        venue.relative = relative or []
        return super().from_orm(venue)
