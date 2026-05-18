import typing
from dataclasses import dataclass

from pcapi.core.offers.defs.parse.types import Field


@dataclass(frozen=True)
class FieldDiff:
    """Wrap a field name with its computed difference kind

    All differences should be implemented by simply subclassing this
    class: this is a thin wrapper whose goal is merely to be match
    against or be printed.
    """

    field: str

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.field})"


class Same(FieldDiff):
    pass


class ShouldBeOptional(FieldDiff):
    pass


class ShouldBeMandatory(FieldDiff):
    pass


class ShouldBePresent(FieldDiff):
    pass


class ShouldBeMissing(FieldDiff):
    pass


DiffKind = typing.Literal["no_diff", "minor", "major"]


@dataclass(frozen=True)
class DiffStatus:
    """Bring together all of the known fields and diff info"""

    subcategory_id: str
    subcategory_fields: set[Field]
    new_model_fields: set[Field]
    diff: typing.Collection[FieldDiff]
    kind: DiffKind

    @classmethod
    def build(
        cls,
        subcategory_id: str,
        subcategory_fields: set[Field],
        new_model_fields: set[Field],
        diff: typing.Collection[FieldDiff],
    ) -> typing.Self:

        # There can be no difference at all, minor ones at most (meaning
        # the exact same fields except some are optional/mandatory only
        # on one side), or major ones (missing or extra fields).
        kind: DiffKind = "no_diff"
        for diff_item in diff:
            match diff_item:
                case ShouldBeOptional() | ShouldBeMandatory():
                    kind = "minor"
                case ShouldBePresent() | ShouldBeMandatory():
                    # higher kind reached, no need to continue
                    kind = "major"
                    break

        return cls(
            subcategory_id=subcategory_id,
            subcategory_fields=subcategory_fields,
            new_model_fields=new_model_fields,
            diff=diff,
            kind=kind,
        )


TypologyDiff = typing.Literal[
    "should_be_selectable",
    "should_not_be_selectable",
    "should_be_digital",
    "should_not_be_digital",
    "should_be_activity",
    "should_not_be_activity",
    "same",
]
