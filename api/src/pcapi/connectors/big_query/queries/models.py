import pydantic


class ProEmailModel(pydantic.BaseModel):
    venue_booking_email: pydantic.EmailStr
