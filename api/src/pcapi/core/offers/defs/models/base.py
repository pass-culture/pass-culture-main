import enum
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


class Typology(enum.Enum):
    """Typology base on offers' subcategories and shared fields

    Note: this is quite arbitrary. Feel free to improve it by
    adding or remving some of them.

    Please keep in mind that:
        1. it might not be useful to add a new typology that has
        absolutely no specific rule with it;
        2. prefixes should be used to build a group (eg. all activities
        begin with ACTIVITY_);
        3. shared offer-specific fields should be more important
        than a vague global property (eg. is_digital).
    """

    UNSPECIFIED = "UNSPECIFIED"
    CANNOT_BE_CREATED = "CANNOT_BE_CREATED"
    THINGS = "THINGS"
    DIGITAL = "DIGITAL"
    ACTIVITY_ONLINE_EVENT = "ACTIVITY_ONLINE_EVENT"
    ACTIVITY_EVENT = "ACTIVITY_EVENT"
    ACTIVITY_RANDOM = "ACTIVITY_RANDOM"

    @property
    def is_digital(self) -> bool:
        # NOTE(jbaudet - 02/2026): method implemented for legacy
        # reason, to keep a not-too-far-away interface from the
        # original one (subcategories).
        return self in (self.DIGITAL, self.ACTIVITY_ONLINE_EVENT)

    @property
    def can_be_an_event(self) -> bool:
        # NOTE(jbaudet - 02/2026): method implemented for legacy
        # reason, to keep a not-too-far-away interface from the
        # original one (subcategories/Offer model based on subcategories
        # models).
        return self in (
            self.ACTIVITY_EVENT,
            self.ACTIVITY_ONLINE_EVENT,
        )


class Mandatory(pydantic_v2.BaseModel):
    """Define all shared mandatory fields

    Any specific mandatory field should be defined inside another
    subclass.

    Any validation rule set here should be valid for each model. If
    some specific rule is needed, override the field definition and
    add it.

    Please note that this model can be used to perform some partial
    validation: all fields might not be set but at least the core ones
    should be (and be valid). And the configuration allows extra keys
    (again, this is useful for some partial validation), which should
    not be allowed otherwise.
    """

    name: Annotated[str, AfterValidator(does_not_contain_ean)]
    venue: Venue
    audio_disability_compliant: bool
    mental_disability_compliant: bool
    motor_disability_compliant: bool
    visual_disability_compliant: bool

    # `typology` is meant to define some specific rules for some sets
    # of offers (eg. digital offers do not have the same rules as
    # physical one, or some activities can become events and thus allow
    # some sort of stocks, etc).
    # -> its usage is internal, there is no need to export it.
    typology: Typology = pydantic_v2.Field(Typology.UNSPECIFIED, exclude=True)

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
