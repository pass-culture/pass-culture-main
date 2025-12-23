import os
import typing
from collections import defaultdict
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
        return import_module("." + rel_path.replace(".py", ""), "pcapi.core.offers.services")

    def extract_subcategory(model: typing.Any) -> str:
        return model.model_fields["subcategory_id"].annotation.__args__[0]

    base_dir = os.path.dirname(__file__)

    base_mapping = defaultdict(list)
    for path in os.listdir(base_dir):
        if "digital" in path:
            base_mapping["digital"].append(import_pkg(path))
        elif "thing" in path:
            base_mapping["thing"].append(import_pkg(path))
        elif "activity" in path:
            base_mapping["activity"].append(import_pkg(path))

    # map a global category (digital, thing, activity) to modules
    # and map those modules to subcategories
    # and map those subcategories to their pydantic model
    mapping = {}
    for category, modules in base_mapping.items():
        mapping[category] = {}

        for module in modules:
            module_name = module.__name__.split('.')[-1]
            mapping[category][module_name] = {}

            for item in dir(module):
                obj = getattr(module, item)
                if getattr(obj, '__module__', None) != module.__name__:
                    # either:
                    #   * obj is not a model or
                    #   * obj is a model but it is not defined inside
                    #     this module, but imported by it
                    continue

                if hasattr(obj, "model_fields") and "subcategory_id" in obj.model_fields:
                    mapping[category][module_name][extract_subcategory(obj)] = obj

    return mapping


SUBCATEGORY_TO_MODEL = map_subcategories_to_models()


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
        return SUBCATEGORY_TO_MODEL[subcategory_id]
    except KeyError:
        # should not be reachable!
        raise UnknownSubcategory(subcategory_id)
