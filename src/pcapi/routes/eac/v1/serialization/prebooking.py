from pydantic import BaseModel


class PreBookingResponse(BaseModel):
    id: int


class PreBookingsResponse(BaseModel):
    prebookings: list[PreBookingResponse]
