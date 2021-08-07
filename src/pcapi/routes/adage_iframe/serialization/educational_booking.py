from pydantic import BaseModel


class BookEducationalOfferRequest(BaseModel):
    redactorEmail: str
    UAICode: str
    stockId: int


class BookEducationalOfferResponse(BaseModel):
    bookingId: int
