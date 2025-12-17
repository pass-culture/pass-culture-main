import typing

import pydantic as pydantic_v2
from pydantic import ValidationError

from .shared import Mandatory


def validate_only_update(model: pydantic_v2.BaseModel, **kwargs: typing.Any) -> pydantic_v2.BaseModel:
    mandatory_keys = Mandatory.model_fields.keys()
    extra_keys = {k: v for k, v in kwargs.items() if k not in mandatory_keys}

    # should pass shared mandatory data
    Mandatory(**kwargs)

    try:
        model(**kwargs)
    except ValidationError as err:
        locs = {loc for e in err.errors() for loc in e['loc']}
        breakpoint()
        raise


def lookup_concrete_models():
    from importlib import import_module
    from pathlib import Path
    import os

    # [import_module(str((base / x)).replace('/', '.').replace('.py', '')) for x in os.listdir(base) if any(y in x for y in ('digital', 'thing', 'activity'))]
    # objs = [getattr(modules[1], x) for x in dir(modules[1])]
    # objs = [obj for obj in objs if hasattr(obj, 'model_fields') and 'subcategoryId' in obj.model_fields]
    # objs[0].model_fields['subcategoryId'].asdict()['annotation'].__dict__['__args__']
