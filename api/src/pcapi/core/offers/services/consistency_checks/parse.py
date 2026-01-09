# import typing

# from pcapi.core.categories import subcategories
# from pcapi.core.offers.services import models

# from . import types


# def parse_properties(defs: dict, properties: dict) -> typing.Generator[types.Field, None, None]:
    # for name, data in properties.items() if properties else []:
        # match data:
            # case {"anyOf": [{"$ref": ref}, {"type": "null"}]}:
                # components = build_components(defs, ref)
                # yield types.Field.build(name=name, optional=True, components=components)
            # case {"anyOf": choices}:
                # components = parse_choices(defs, choices)
                # optional = {"type": "null"} in choices
                # yield types.Field.build(name=name, optional=optional, components=components)
            # case {"$ref": ref}:
                # components = build_components(defs, ref)
                # yield types.Field.build(name=name, components=components)
            # case _:
                # if name == 'extra_data' and data is None:
                    # raise ValueError(name)
                # yield types.Field.build(name=name)


# def parse_choices(defs: dict, refs: list[dict]) -> tuple[types.OrField]:
    # match refs:
        # case [{"$ref": ref}]:
            # name, components = parse_ref(defs, ref)
            # return tuple([types.OrField.build(name=name, components=components)])
        # case [{"$ref": ref}, *rest]:
            # name, components = parse_ref(defs, ref)
            # return tuple([types.OrField.build(name=name, components=components)]) + parse_choices(defs, rest)
        # case _:
            # return tuple()


# def parse_ref(defs: dict, ref: dict) -> tuple[str, tuple[types.Field]]:
    # definition = defs[ref.replace("#/$defs/", "")]
    # props = definition.get("properties")
    # name = definition.get("title")
    # return name, tuple(parse_properties(defs, props))


# def build_components(defs: dict, ref: str) -> tuple[types.Field]:
    # props = defs[ref.replace("#/$defs/", "")].get("properties")
    # return tuple(parse_properties(defs, props))


# def build_model_fields(model: models.base.Base) -> typing.Collection[types.Field]:
    # schema = model.model_json_schema()
    # defs = schema["$defs"]
    # properties = schema["properties"]
    # if not properties:
        # return set()

    # return set(parse_properties(defs, properties))


# def build_new_model_extra_data_fields(model: models.base.Base) -> set[types.Field]:
    # schema = model.model_json_schema()
    # defs = schema["$defs"]
    # extra_data_properties = schema["properties"].get("extra_data")
    # if not extra_data_properties:
        # return set()

    # extra_data_field = parse_properties(defs, {"extra_data": extra_data_properties})
    # return set(component for field in extra_data_field for component in field.components)


# def subcategory_fields(subcategory: subcategories.Subcategory) -> set[types.ExtraDataField]:
    # """Extract a Subcategory's fields' information

    # Notes:
        # a field is considered optional is `is_required_in_internal_form`
        # is false. The `is_required_in_external_form` is ignored but this
        # is a quite arbitrary choice.
    # """

    # def _parse(name, condition):
        # return types.Field.build(name=name, optional=not condition.is_required_in_internal_form)

    # return {_parse(name, condition) for name, condition in subcategory.conditional_fields.items()}
