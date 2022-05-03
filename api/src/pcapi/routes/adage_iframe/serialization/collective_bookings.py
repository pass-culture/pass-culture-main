from pcapi.routes.serialization import BaseModel


class BookCollectiveOfferRequest(BaseModel):
    stockId: int


class BookCollectiveOfferResponse(BaseModel):
    bookingId: int
