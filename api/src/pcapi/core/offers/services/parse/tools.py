import typing

from . import types


def parse_properties(defs: dict, properties: dict) -> typing.Generator[types.Field, None, None]:
    for name, data in properties.items() if properties else []:
        match data:
            case {"anyOf": [{"$ref": ref}, {"type": "null"}]}:
                components = build_components(defs, ref)
                yield types.Field.build(name=name, optional=True, components=components)
            case {"anyOf": choices}:
                components = parse_choices(defs, choices)
                optional = {"type": "null"} in choices
                yield types.Field.build(name=name, optional=optional, components=components)
            case {"$ref": ref}:
                components = build_components(defs, ref)
                yield types.Field.build(name=name, components=components)
            case _:
                if name == 'extra_data' and data is None:
                    raise ValueError(name)
                yield types.Field.build(name=name)


def parse_choices(defs: dict, refs: list[dict]) -> tuple[types.OrField]:
    match refs:
        case [{"$ref": ref}]:
            name, components = parse_ref(defs, ref)
            return tuple([types.OrField.build(name=name, components=components)])
        case [{"$ref": ref}, *rest]:
            name, components = parse_ref(defs, ref)
            return tuple([types.OrField.build(name=name, components=components)]) + parse_choices(defs, rest)
        case _:
            return tuple()


def parse_ref(defs: dict, ref: dict) -> tuple[str, tuple[types.Field]]:
    definition = defs[ref.replace("#/$defs/", "")]
    props = definition.get("properties")
    name = definition.get("title")
    return name, tuple(parse_properties(defs, props))


def build_components(defs: dict, ref: str) -> tuple[types.Field]:
    props = defs[ref.replace("#/$defs/", "")].get("properties")
    return tuple(parse_properties(defs, props))
