import enum
import typing
from dataclasses import dataclass
from dataclasses import field

from pcapi.core.categories.subcategories import Subcategory
from pcapi.core.offers.services.parse.types import Field


class FieldOrigin(enum.Enum):
    MANDATORY = "mandatory"
    BASE = "base"
    INHERITED = "inherited"
    OWN = "own"

    def __lt__(self, other: typing.Self) -> bool:
        cls = type(self)

        match self:
            case cls.MANDATORY:
                return True
            case cls.BASE:
                return other in (cls.INHERITED, cls.OWN)
            case cls.INHERITED:
                return other is cls.OWN
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
    required: typing.Collection[FieldWithOrigin]
    optional: typing.Collection[FieldWithOrigin] = field(default_factory=list)


@dataclass(frozen=True)
class ModelSchema:
    subcategory: Subcategory
    properties: Properties


HierarchyCache = dict[str, set[Field]]


@dataclass(frozen=True)
class Hierarchy:
    mandatory: set[Field]
    base: set[Field]
    other: set[Field]
