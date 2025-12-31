import typing
from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True)
class ExtraDataField:
    """Store an extra data field's whole context

    `name` is the original form of the field's name. It is then
    normalized (removing any snake/camel/etc. case) to build the `id`
    that provides a key to be used to compare objects between them.

    The `optional` parameter indicates whether this fields has been
    identified as optional are not and is also used when comparing
    two objects.
    """
    id: str
    name: str = field(hash=False, compare=False)
    optional: bool
    default: typing.Any = field(hash=False, compare=False)

    @property
    def shortened(self) -> str:
        if self.optional:
            return f"{self.name}[opt]"
        return f"{self.name}"

    @classmethod
    def build(cls, name, optional=False, default="<missing>") -> typing.Self:
        return cls(
            id=name.lower().replace('_', ''),
            name=name,
            optional=optional,
            default=default
        )


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


class DiffSummary:
    """Wrap a collection of `Diff` with a subcategory id

    This container class sets together a subcategory id and all of its
    fields computed differences.
    """
    kind = "diff"

    def __init__(self, subcategory_id: str, raw: typing.Collection[Diff]):
        self.subcategory_id = subcategory_id
        self.raw = raw

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.subcategory_id}, {self.raw})"


class NoDiff(DiffSummary):
    kind = "no_diff"


class OptionalDiff(DiffSummary):
    kind = "optional_diff"


@dataclass(frozen=True)
class SubcategoryDiffStatus:
    """Bring together all of the known fields and diff info"""
    subcategory_id: str
    subcategory_fields: set[ExtraDataField]
    new_model_fields: set[ExtraDataField]
    diff: DiffSummary
