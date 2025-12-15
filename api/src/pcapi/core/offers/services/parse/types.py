import enum
import typing
from dataclasses import dataclass
from dataclasses import field


class FieldCompareKind(enum.Enum):
    EQUAL = "equal"
    SHOULD_BE_OPTIONAL = "should_be_optional"
    SHOULD_BE_MANDATORY = "should_be_mandatory"
    SHOULD_BE_MISSING = "should_be_missing"
    SHOULD_BE_PRESENT = "should_be_present"


@dataclass(frozen=True, order=True)
class Field:
    id: str
    name: str = field(compare=False)
    optional: bool = False
    components: typing.Collection[typing.Self] = field(default_factory=tuple, compare=False)

    @classmethod
    def build(cls, **kwargs: typing.Any) -> typing.Self:
        return cls(id=kwargs["name"].lower().replace("_", ""), **kwargs)

    def compare(self, other: typing.Self | None = None) -> FieldCompareKind:
        if not other:
            return FieldCompareKind.SHOULD_BE_PRESENT
        if self == other:
            return FieldCompareKind.EQUAL
        elif (self.id == other.id) and self.optional:
            return FieldCompareKind.SHOULD_BE_OPTIONAL
        else:
            return FieldCompareKind.SHOULD_BE_MANDATORY


@dataclass(frozen=True, order=True)
class OrField(Field):
    pass
