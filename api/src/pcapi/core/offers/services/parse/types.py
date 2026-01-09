import typing
from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True, order=True)
class Field:
    id: str
    name: str = field(compare=False)
    optional: bool = False
    components: typing.Collection[typing.Self] = field(default_factory=tuple, compare=False)

    @classmethod
    def build(cls, **kwargs: typing.Any) -> typing.Self:
        return cls(id=kwargs["name"].lower().replace("_", ""), **kwargs)


@dataclass(frozen=True, order=True)
class OrField(Field):
    pass


# @dataclass(frozen=True)
# class ExtraDataField:
# """Store an extra data field's whole context

# `name` is the original form of the field's name. It is then
# normalized (removing any snake/camel/etc. case) to build the `id`
# that provides a key to be used to compare objects between them.

# The `optional` parameter indicates whether this fields has been
# identified as optional are not and is also used when comparing
# two objects.
# """

# id: str
# optional: bool
# name: str = field(compare=False)
# components: typing.Collection[typing.Self] = field(default_factory=tuple, compare=False)

# @classmethod
# def build(cls, name, optional=False, components=tuple()) -> typing.Self:
# return cls(id=name.lower().replace("_", ""), name=name, optional=optional, components=components)
