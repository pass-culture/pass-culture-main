from pcapi.core.offers.services import models

from . import tools
from . import types


def build_model_fields(model: models.base.Base) -> set[types.Field]:
    schema = model.model_json_schema()
    defs = schema["$defs"]
    properties = schema["properties"]
    if not properties:
        return set()

    return set(tools.parse_properties(defs, properties))


def build_model_extra_data_fields(model: models.base.Base) -> set[types.Field]:
    schema = model.model_json_schema()
    defs = schema["$defs"]
    extra_data_properties = schema["properties"].get("extra_data")
    if not extra_data_properties:
        return set()

    # `parse_properties` needs a dict as an input and will be return the
    # whole extra_data `Field`. The thing is... we only care about its
    # components
    extra_data_field = tools.parse_properties(defs, {"extra_data": extra_data_properties})
    return set(component for field in extra_data_field for component in field.components)
