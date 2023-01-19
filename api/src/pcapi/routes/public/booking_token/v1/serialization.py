from pcapi.routes.serialization import BaseModel


class PatchBookingByTokenQueryModel(BaseModel):
    email: str | None
    offer_id: str | None


class LegacyBookingResponse(BaseModel):
    bookingId: str | None
    date: str | None
    email: str | None
    isUsed: bool | None
    offerName: str | None
    userName: str | None
    venueDepartementCode: str | None
