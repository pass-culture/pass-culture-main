import pydantic.v1 as pydantic_v1


class ProEmailModel(pydantic_v1.BaseModel):
    venue_booking_email: pydantic_v1.EmailStr
