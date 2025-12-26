import os
import typing
from collections import defaultdict
from importlib import import_module
from pathlib import Path

import pydantic as pydantic_v2


def _map_subcategories_to_models() -> dict[str, dict[str, dict[str, pydantic_v2.BaseModel]]]:
    """Build a detailed mapping of subcategories to models

    This function builds a three-level mapping:
        1. main category (digital, thing, activity)
        2. (python) module (name only)
        3. subcategory

    And then each subcategory is mapped to its specific pydantic model.
    For example:
        {
            "thing": {
                "things_with_ean": {
                    "SUPPORT_PHYSIQUE_FILM": <model instance>
                    "LIVRE_PAPIER": <another model instance>
                },
                "things_random": {
                    "ABO_CONCERT": <and another model instance>
                }
            }
        }

    This function is meant to be called once in order to store its value
    inside a global variable. There is no need to scan and parse many
    python module many time.

    Its multi-level mapping becomes useful inside tests and a python
    shell to understand what is going on (check that a subcategory is
    handled at the right place and is used inside the appropriate python
    module, etc., print some static document that shows how things are
    structured, etc.)
    """

    def import_pkg(rel_path: str) -> typing.Any:
        return import_module("." + rel_path.replace(".py", ""), "pcapi.core.offers.services.models")

    def extract_subcategory(model: typing.Any) -> str:
        return model.model_fields["subcategory_id"].annotation.__args__[0]

    base_dir = Path() / os.path.dirname(__file__) / "models"

    base_mapping = defaultdict(list)
    for path in os.listdir(base_dir):
        if path.startswith("digital_"):
            base_mapping["digital"].append(import_pkg(path))
        elif path.startswith("things_"):
            base_mapping["things"].append(import_pkg(path))
        elif path.startswith("activity_"):
            base_mapping["activity"].append(import_pkg(path))
        elif path.startswith("unselectable_"):
            base_mapping["unselectable"].append(import_pkg(path))

    # map a global category (digital, thing, activity) to modules
    # and map those modules to subcategories
    # and map those subcategories to their pydantic model
    mapping = {}
    for category, modules in base_mapping.items():
        mapping[category] = {}

        for module in modules:
            module_name = module.__name__.split(".")[-1]
            mapping[category][module_name] = {}

            for item in dir(module):
                obj = getattr(module, item)
                if getattr(obj, "__module__", None) != module.__name__:
                    # either:
                    #   * obj is not a model or
                    #   * obj is a model but it is not defined inside
                    #     this module, but imported by it
                    continue

                # 1. `obj` must be a pydantic model
                # 2. this model must have a `subcategory_id` field defined
                # 3. this field must be defined with only one allowed value
                # (eg. a literal with one subcategory id, not an enum of
                # allowed subcategory ids)
                has_specific_subcategory_defined = (
                    hasattr(obj, "model_fields")
                    and "subcategory_id" in obj.model_fields
                    and len(obj.model_fields["subcategory_id"].annotation.__args__) == 1
                )
                if has_specific_subcategory_defined:
                    mapping[category][module_name][extract_subcategory(obj)] = obj

    return mapping


def _flattended_mapping(main_mapping: dict) -> dict:
    return {
        subcategory_id: model
        for category, modules in main_mapping.items()
        for module_name, models in modules.items()
        for subcategory_id, model in models.items()
    }


FULL_MAPPING = _map_subcategories_to_models()

SUBCATEGORY_TO_MODEL = _flattended_mapping(FULL_MAPPING)
