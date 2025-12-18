import os
import typing
from importlib import import_module

import pydantic as pydantic_v2
from pydantic import ValidationError

from pcapi.core.offers.services.shared import Mandatory


def partial_validation(model: pydantic_v2.BaseModel, **kwargs: typing.Any) -> None:
    mandatory_keys = Mandatory.model_fields.keys()
    extra_keys = {k: v for k, v in kwargs.items() if k not in mandatory_keys}

    # should pass shared mandatory data
    Mandatory(**kwargs)

    try:
        obj = model(**kwargs)
    except ValidationError as err:
        locs = {loc for e in err.errors() for loc in e['loc']}

        # if an error has been raised because of either:
        #  * a mandatory field
        #  * or one that comes from kwargs (meaning caller explicitely
        #    tried to set that field with an invalid value)
        # then raise the error with only thoses fields.
        # Please keep in mind that this is only a partial validator.
        if locs <= (mandatory_keys | extra_keys):
            raise


def map_subcategories_to_models() -> dict[str, typing.Any]:
    def import_pkg(rel_path: str) -> typing.Any:
        return import_module("." + rel_path.replace('.py', ''), 'pcapi.core.offers.services')

    def extract_subcategory(model: typing.Any) -> str:
        return model.model_fields['subcategoryId'].annotation.__args__[0]

    # filter files inside current module that contains models definition
    categories = ('digital', 'thing', 'activity')
    base_dir = os.path.dirname(__file__)
    files = [path for path in os.listdir(base_dir) if any (x in path for x in categories)]

    # from those files, load python modules and only keep pydantic
    # models that matches a subcategory
    modules = [import_pkg(path) for path in files]
    objs = [getattr(module, item) for module in modules for item in dir(module)]
    models = [obj for obj in objs if hasattr(obj, 'model_fields') and 'subcategoryId' in obj.model_fields]

    return {extract_subcategory(model): model for model in models}
