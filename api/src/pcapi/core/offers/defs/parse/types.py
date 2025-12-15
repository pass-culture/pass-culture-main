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
    """Base datatype used by other modules

    It helps to map model fields to a set of Fields.. which makes
    it easier to compare models between them: no need to check field by
    field, etc. Simply use set operations.

    This id field is the normalized name and is used for equality
    checks. Otherwise fields named "music_type" and "musicType" could
    not be considered equal... which is not what we are looking for.
    """

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
