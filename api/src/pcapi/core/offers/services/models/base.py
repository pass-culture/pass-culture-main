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
    return name


class Mandatory(pydantic_v2.BaseModel):
    """Define all shared mandatory fields

    Any specific mandatory field should be defined inside another
    (shared or not) subclass.

    Any validation rule set here should be valid for each model. If
    some specific rule is needed, override the field definition and
    add it.

    Please note that this model can be used to perform some partial
    validation: all fields might not be set bet at least the core ones
    should be (and be valid). This explains two specific definitions:

        1. the `subcategory_id` is a literal containing many values and
        should obviously be overriden inside concrete class with one
        specific value;
        2. the model_config allows extra fields whereas concrete classes
        should not
    """
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
    """Base class to inherit from that adds shared optional fields

    Every concrete model should inherit from `Base`.
    """
    description: str | None = None
    booking_email: EmailStr | None = None

    model_config = pydantic_v2.ConfigDict(extra="forbid")
