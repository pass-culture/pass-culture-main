import re
from typing import Annotated
from typing import Literal

import pydantic as pydantic_v2
from pydantic import AfterValidator
from pydantic import EmailStr

from pcapi.core.categories import subcategories

from .shared import Venue


def does_not_contain_ean(name: str) -> str:
    if re.search(r"\d{13}", name):
        raise ValueError(name)


class Mandatory(pydantic_v2.BaseModel):
    subcategory_id: Literal[*[sub.value for sub in subcategories.SubcategoryIdEnum]]  # to override
    name: Annotated[str, AfterValidator(does_not_contain_ean)]
    venue: Venue
    audio_disability_compliant: bool
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    visual_disability_compliant: bool

    model_config = pydantic_v2.ConfigDict(
        str_strip_whitespace=True,
        extra="ignore",
    )

class Base(Mandatory):
    description: str | None = None
    booking_email: EmailStr | None = None

    model_config = pydantic_v2.ConfigDict(extra="forbid")
