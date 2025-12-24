import typing

import pydantic as pydantic_v2
from pydantic import ValidationError

from pcapi.core.categories import subcategories

from . import SUBCATEGORY_TO_MODEL
from .models.base import Mandatory


class InputValidationError(Exception):
    def __init__(self, pydantic_errors):
        self.pydantic_errors = pydantic_errors
        self.details = {".".join(e["loc"]): {"type": e["type"]} for e in self.pydantic_errors}

        fields = {".".join(e["loc"]) for e in self.pydantic_errors}
        super().__init__(f"errors: {fields}")


class MandatoryInputValidationError(InputValidationError):
    pass


class OfferMappingError(Exception):
    pass


class CannotCreateOffer(OfferMappingError):
    pass


class UnknownSubcategory(OfferMappingError):
    pass


def partial_validation(model: pydantic_v2.BaseModel, **params: typing.Any) -> None:
    """Only validate minimal consistency

    Only validate that shared mandatory fields exists and are valid, and
    that any other also passed through `params` are.

    This function should be used to ensure that through each step of an
    object (eg. an offer) creation and update process, it contains only
    valid data and that its moves forward to its final state with all
    its mandatory and optional fields set.

    Notes:
        * a shared mandatory field is one that is needed by all models,
        like a name or a subcategory;
        * some model might have some specific mandatory fields, if any
        of these is missing from `params`, no error will be raised;
        * an optional field sent through `params` with an invalid value
        will raise an exception.

    """
    mandatory_keys = Mandatory.model_fields.keys()
    extra_keys = {k: v for k, v in params.items() if k not in mandatory_keys}

    try:
        Mandatory(**params)
    except ValueError as err:
        raise MandatoryInputValidationError(err.errors()) from err

    try:
        model(**params)
    except ValidationError as err:
        locs = {e["loc"][0] for e in err.errors()}

        # if an error has been raised because of either:
        #  * a mandatory field
        #  * or one that comes from params (meaning caller explicitely
        #    tried to set that field with an invalid value)
        # then raise the error with only thoses fields.
        updated_locs_in_error = locs & (mandatory_keys | extra_keys)
        if updated_locs_in_error:
            details = [e for e in err.errors() if e["loc"][0] in updated_locs_in_error]
            raise InputValidationError(details) from err


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
