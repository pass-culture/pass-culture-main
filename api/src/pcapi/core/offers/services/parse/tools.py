import typing

from . import types


def parse_properties(defs: dict, properties: dict) -> typing.Generator[types.Field, None, None]:
    """Top-level parse function

    Parse a pydantic's model json schema and yield `Field`s objects
    """
    for name, data in properties.items() if properties else []:
        match data:
            # current field contains an anyOf rule with two items:
            # a reference and the null type
            # -> its an optional field and the reference must be fetched
            # and parsed as its components
            case {"anyOf": [{"$ref": ref}, {"type": "null"}]}:
                yield types.Field.build(name=name, optional=True, components=_build_components(defs, ref))
            # current field contains an anyOf rule with some items and
            # previous rule did not match
            # -> there are many choices (`Field`s) that must be fetched
            # and parsed as its components
            case {"anyOf": choices}:
                optional = {"type": "null"} in choices
                yield types.Field.build(name=name, optional=optional, components=_parse_choices(defs, choices))
            # current field contains a reference that is not nested
            # inside an anyOf rule (previous rules did not match)
            # -> it is a mandatory field and the reference must be
            # fetched and parsed as its components
            case {"$ref": ref}:
                yield types.Field.build(name=name, components=_build_components(defs, ref))
            # none of the previous rule matched
            # -> current field is a simple basic one
            case _:
                yield types.Field.build(name=name)


def _parse_choices(defs: dict, refs: list[dict]) -> tuple[types.OrField, ...]:
    """Builds components as a collection of `OrField`s"""
    match refs:
        # there is only one reference that must be fetched and parsed
        case [{"$ref": ref}]:
            name, components = _parse_ref(defs, ref)
            return tuple([types.OrField.build(name=name, components=components)])
        # there are many references that must be fetched and parsed
        case [{"$ref": ref}, *rest]:
            name, components = _parse_ref(defs, ref)
            return tuple([types.OrField.build(name=name, components=components)]) + _parse_choices(defs, rest)
        case _:
            return tuple()


def _parse_ref(defs: dict, ref: str) -> tuple[str, tuple[types.Field, ...]]:
    definition = defs[ref.replace("#/$defs/", "")]
    props = definition.get("properties")
    name = definition.get("title")
    return name, tuple(parse_properties(defs, props))


def _build_components(defs: dict, ref: str) -> tuple[types.Field, ...]:
    props = defs[ref.replace("#/$defs/", "")].get("properties")
    return tuple(parse_properties(defs, props))
