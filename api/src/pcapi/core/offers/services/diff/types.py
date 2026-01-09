import typing
from dataclasses import dataclass

from pcapi.core.offers.services.parse.types import Field


@dataclass(frozen=True)
class Diff:
    """Difference between an expected status and the real one

    All differences should be implemented by simply subclassing this
    class: this is a thin wrapper whose goal is merely to be match
    against or be printed.
    """

    field: str

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.field})"


class Same(Diff):
    pass


class ShouldBeOptional(Diff):
    pass


class ShouldBeMandatory(Diff):
    pass


class ShouldBePresent(Diff):
    pass


class ShouldBeMissing(Diff):
    pass


DiffKind = typing.Literal["no_diff", "minor", "major"]


@dataclass(frozen=True)
class SubcategoryDiffStatus:
    """Bring together all of the known fields and diff info"""

    subcategory_id: str
    subcategory_fields: set[Field]
    new_model_fields: set[Field]
    diff: typing.Collection[Diff]
    kind: DiffKind

    @classmethod
    def build(
        cls,
        subcategory_id: str,
        subcategory_fields: set[Field],
        new_model_fields: set[Field],
        diff: typing.Collection[Diff],
    ) -> typing.Self:
        return cls(
            subcategory_id=subcategory_id,
            subcategory_fields=subcategory_fields,
            new_model_fields=new_model_fields,
            diff=diff,
            kind=compute_diff_kind(diff),
        )


def compute_diff_kind(diff) -> DiffKind:
    """Compute difference kind

    There can be no difference at all, minor ones at most (meaning
    the exact same fields but some are optional/mandatory only
    on one side), or major ones (missing or extra fields).
    """
    kind = "no_diff"

    for diff_item in diff:
        if type(diff_item) in (ShouldBeOptional, ShouldBeMandatory):
            kind = "minor"
        elif type(diff_item) in (ShouldBePresent, ShouldBeMandatory):
            return "major"

    return kind
