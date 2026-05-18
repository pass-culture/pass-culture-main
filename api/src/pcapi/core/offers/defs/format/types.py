import enum
import typing
from dataclasses import dataclass
from dataclasses import field

from pcapi.core.categories.subcategories import Subcategory
from pcapi.core.offers.defs import models
from pcapi.core.offers.defs.parse.types import Field


class FieldOrigin(enum.Enum):
    BASE = "base"
    OWN = "own"

    def __lt__(self, other: typing.Self) -> bool:
        return self == FieldOrigin.BASE


@dataclass(frozen=True)
class FieldWithOrigin(Field):
    origin: FieldOrigin = FieldOrigin.OWN

    @classmethod
    def from_field(cls, field: Field, origin: FieldOrigin) -> typing.Self:
        return cls.build(
            name=field.name,
            optional=field.optional,
            components=field.components,
            origin=origin,
            union_values=field.union_values,
        )


@dataclass(frozen=True)
class Properties:
    typology: models.Typology
    required: typing.Collection[FieldWithOrigin]
    optional: typing.Collection[FieldWithOrigin] = field(default_factory=list)


@dataclass(frozen=True)
class ModelSchema:
    subcategory: Subcategory
    properties: Properties
