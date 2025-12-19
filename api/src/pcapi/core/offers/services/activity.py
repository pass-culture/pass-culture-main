
from pydantic import EmailStr

from . import shared


class ActivityBaseModel(shared.Base):
    # optional for most of subcategories, but not these
    booking_email: EmailStr
