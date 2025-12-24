
from pydantic import EmailStr

from .base import Base


class ActivityBaseModel(Base):
    # optional for most of subcategories, but not these
    booking_email: EmailStr
