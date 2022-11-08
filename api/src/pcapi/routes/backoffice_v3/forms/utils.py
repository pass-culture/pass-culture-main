import enum
import typing


def choices_from_enum(enum_cls: typing.Type[enum.Enum]) -> list[tuple]:
    return [(opt.name, opt.value) for opt in enum_cls]


def values_from_enum(enum_cls: typing.Type[enum.Enum]) -> list[tuple]:
    return [(opt.value, opt.value) for opt in enum_cls]
