import typing
from dataclasses import dataclass

import pydantic as pydantic_v2

from . import FULL_MAPPING


@dataclass
class FlattenedDetails:
    category: str
    module_str: str
    subcategory_id: str
    model: pydantic_v2.BaseModel


def stream_flattened_subcategories_models() -> typing.Generator[FlattenedDetails, None, None]:
    for category, modules in FULL_MAPPING.items():
        for module_name, models in modules.items():
            for subcategory_id, model in models.items():
                yield FlattenedDetails(category, module_name, subcategory_id, model)
