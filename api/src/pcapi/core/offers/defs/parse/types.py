import typing
from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True, order=True)
class Field:
    """Normalized data model for a field

    A `Field` is defined by its `id`, its `optional`, its `components`
    and its `union_values`. These will be used for comparison and set
    operations: two `Fields` are equal if those are.

    A `Field` also contains one extra information: its original name,
    used mainly for display operations.

    > The id is the normalized name: a mandatory "musicType" and a
    mandatory "music_type" should be considered equal because we are not
    interested in camel/snake/etc/case details but in the overall
    information.

    > components are nested fields, nothing more
    > union_values are the (meaningful) available values for this
      `Field`, eg. str | None are ignored whereas a union of model
      names won't be.
    """

    id: str
    name: str = field(compare=False)
    optional: bool = False
    components: tuple[typing.Self, ...] = field(default_factory=tuple)
    union_values: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def build(cls, **kwargs: typing.Any) -> typing.Self:
        # the **kwargs is not the most typesafe way to build a `Field`
        # but it makes it way easier for subclasses with additional
        # fields to call it.
        return cls(id=kwargs["name"].lower().replace("_", ""), **kwargs)
