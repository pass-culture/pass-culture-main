import re
from typing import Annotated

import pydantic as pydantic_v2
from pydantic import AfterValidator
from pydantic import EmailStr

from .shared import Venue


def does_not_contain_ean(name: str) -> str:
    if re.search(r"\d{13}", name):
        raise ValueError(name)
    return name


class Mandatory(pydantic_v2.BaseModel):
    """Define all shared mandatory fields

    > Internal use, prefer `Base` as a mother-class for real models.

    Any validation rule set here should be valid for each model. If
    some specific rule is needed, override the field definition and
    add it.

    Please note that this model can be used to perform some partial
    validation: all fields might not be set but at least the core ones
    should be (and be valid). The configuration allows extra keys (this
    is useful for some partial validation), which should
    not be allowed otherwise.
    """

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

    Base sets the expected model_config right: no extra field is
    allowed. Model config should be shared by all models, as much as
    possible.

    > Every concrete model should inherit from `Base`.
    """

    description: str | None = None
    booking_email: EmailStr | None = None

    model_config = pydantic_v2.ConfigDict(extra="forbid")
