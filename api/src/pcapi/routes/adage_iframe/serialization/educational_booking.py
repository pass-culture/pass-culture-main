from pydantic import BaseModel


class BookEducationalOfferRequest(BaseModel):
    stockId: int


class BookEducationalOfferResponse(BaseModel):
    bookingId: int
