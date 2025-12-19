import os
import typing
from importlib import import_module

import pydantic as pydantic_v2
from pydantic import ValidationError

from pcapi.core.categories import subcategories

from .shared import Mandatory


class InputValidationError(Exception):
    def __init__(self, pydantic_errors):
        self.pydantic_errors = pydantic_errors
        self.details = {".".join(e["loc"]): {"type": e["type"]} for e in self.pydantic_errors}

        fields = {".".join(e["loc"]) for e in self.pydantic_errors}
        super().__init__(f"errors: {fields}")


class OfferMappingError(Exception):
    pass


class CannotCreateOffer(OfferMappingError):
    pass


class UnknownSubcategory(OfferMappingError):
    pass


def partial_validation(model: pydantic_v2.BaseModel, **kwargs: typing.Any) -> None:
    mandatory_keys = Mandatory.model_fields.keys()
    extra_keys = {k: v for k, v in kwargs.items() if k not in mandatory_keys}

    # should pass shared mandatory data
    Mandatory(**kwargs)

    try:
        model(**kwargs)
    except ValidationError as err:
        locs = {e["loc"][0] for e in err.errors()}

        # if an error has been raised because of either:
        #  * a mandatory field
        #  * or one that comes from kwargs (meaning caller explicitely
        #    tried to set that field with an invalid value)
        # then raise the error with only thoses fields.
        # Please keep in mind that this is only a partial validator.
        updated_locs_in_error = locs & (mandatory_keys | extra_keys)
        if updated_locs_in_error:
            details = [e for e in err.errors() if e["loc"][0] in updated_locs_in_error]
            raise InputValidationError(details) from err


def map_subcategories_to_models() -> dict[str, typing.Any]:
    def import_pkg(rel_path: str) -> typing.Any:
        return import_module("." + rel_path.replace(".py", ""), "pcapi.core.offers.services")

    def extract_subcategory(model: typing.Any) -> str:
        return model.model_fields["subcategory_id"].annotation.__args__[0]

    # filter files inside current module that contains models definition
    categories = ("digital", "thing", "activity")
    base_dir = os.path.dirname(__file__)
    files = [path for path in os.listdir(base_dir) if any(x in path for x in categories)]

    # from those files, load python modules and only keep pydantic
    # models that matches a subcategory
    modules = [import_pkg(path) for path in files]
    objs = [getattr(module, item) for module in modules for item in dir(module)]
    models = [obj for obj in objs if hasattr(obj, "model_fields") and "subcategory_id" in obj.model_fields]

    return {extract_subcategory(model): model for model in models}


def get_validation_model(subcategory: subcategories.Subcategory) -> Mandatory:
    subcategory_id = subcategory.id

    cannot_be_created = {
        subcategories.ACTIVATION_EVENT.id,
        subcategories.CAPTATION_MUSIQUE.id,
        subcategories.OEUVRE_ART.id,
        subcategories.BON_ACHAT_INSTRUMENT.id,
        subcategories.ACTIVATION_THING.id,
        subcategories.ABO_LUDOTHEQUE.id,
        subcategories.JEU_SUPPORT_PHYSIQUE.id,
        subcategories.DECOUVERTE_METIERS.id,
    }

    if subcategory_id in cannot_be_created:
        raise CannotCreateOffer(subcategory_id)

    try:
        return map_subcategories_to_models()[subcategory_id]
    except KeyError:
        # should not be reachable!
        raise UnknownSubcategory(subcategory_id)
