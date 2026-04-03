import enum
import typing
from dataclasses import dataclass
from dataclasses import field

from pcapi.core.categories.subcategories import Subcategory
from pcapi.core.offers.defs.parse.types import Field


class FieldOrigin(enum.Enum):
    BASE = "base"
    OWN = "own"

    def __lt__(self, other: typing.Self) -> bool:
        cls = type(self)

        match self:
            case cls.BASE:
                return other in (cls.BASE, cls.OWN)
            case _:
                return other == cls.OWN


@dataclass(frozen=True)
class FieldWithOrigin(Field):
    origin: FieldOrigin = FieldOrigin.OWN

    @classmethod
    def from_field(cls, field: Field, origin: FieldOrigin) -> typing.Self:
        return cls.build(name=field.name, optional=field.optional, components=field.components, origin=origin)


@dataclass(frozen=True)
class Properties:
    is_digital: bool
    can_be_an_event: bool
    required: typing.Collection[FieldWithOrigin]
    optional: typing.Collection[FieldWithOrigin] = field(default_factory=list)


@dataclass(frozen=True)
class ModelSchema:
    subcategory: Subcategory
    properties: Properties


HierarchyCache = dict[str, set[Field]]

Hierarchy = set[Field]
