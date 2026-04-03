import os
import typing
from contextlib import suppress
from importlib import import_module
from pathlib import Path

from pcapi.core.categories import subcategories

from . import models


def extract_subcategory(model: models.Base) -> subcategories.Subcategory:
    subcategory_id = typing.get_args(model.model_fields["subcategory_id"].annotation)[0]
    return subcategories.ALL_SUBCATEGORIES_DICT[subcategory_id]


def _fetch_models() -> dict[str, models.Base]:
    def import_pkg(module_name: str) -> typing.Any:
        return import_module("." + module_name, "pcapi.core.offers.defs.models")

    models_dir = Path(os.path.dirname(__file__)) / Path("models")
    modules = [import_pkg(path.replace(".py", "")) for path in os.listdir(models_dir)]

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

            # Errors will be raised for some intermediate models that
            # are not linked to a subcategory: we do not care about
            # them. This is fine since there not so many of them inside
            # the models module: it is easier to suppress these errors
            # than to avoid them with some filters, checks, etc.
            # This is acceptable as long as a basic unit tests checks
            # that every known subcategory is mapped.
            with suppress(AttributeError, KeyError, IndexError):
                res[extract_subcategory(obj).id] = obj
    return res


MODELS = _fetch_models()
