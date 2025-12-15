import typing
from contextlib import suppress
from importlib import import_module

import pydantic

from pcapi.core.categories import subcategories

from . import models


def extract_subcategory(model: models.Base) -> subcategories.Subcategory:
    subcategory_id = typing.get_args(model.model_fields["subcategory_id"].annotation)[0]
    return subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id]


def _fetch_models() -> dict[str, models.Base]:
    def import_pkg(module_name: str) -> typing.Any:
        return import_module("." + module_name, "pcapi.core.offers.services.models")

    modules = [
        import_pkg("things"),
        import_pkg("digital"),
        import_pkg("activity"),
        import_pkg("unselectable"),
    ]

    res = {}
    for module in modules:
        for item in dir(module):
            obj = getattr(module, item)
            if getattr(obj, "__module__", None) != module.__name__:
                # either:
                #   * obj is not a model or
                #   * obj is a model but it is not defined inside
                #     this module, but imported by it
                continue

            # a couple of calls might crash because of intermedirate
            # models that should be ignored
            with suppress(AttributeError, KeyError, IndexError):
                res[extract_subcategory(obj).id] = obj
    return res


MODELS = _fetch_models()
