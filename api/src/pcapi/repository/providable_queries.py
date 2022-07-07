import datetime

from pcapi.core.offers.models import Offer
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db


def insert_chunk(chunk_to_insert: dict):  # type: ignore [no-untyped-def]
    db.session.bulk_save_objects(chunk_to_insert.values(), return_defaults=False)
    db.session.commit()


def update_chunk(chunk_to_update: dict):  # type: ignore [no-untyped-def]
    # Access `Model.registry` here, not at module-scope,
    # because it may not be populated yet if this module is imported too early.
    MODELS = {mapper.class_.__name__: mapper.class_ for mapper in Base.registry.mappers}

    models_in_chunk = set(_extract_model_name_from_chunk_key(key) for key in chunk_to_update.keys())

    for model_in_chunk in models_in_chunk:
        matching_tuples_in_chunk = _filter_matching_pc_object_in_chunk(model_in_chunk, chunk_to_update)
        values_to_update_in_chunk = _extract_dict_values_from_chunk(matching_tuples_in_chunk)
        model_to_update = MODELS[model_in_chunk]

        db.session.bulk_update_mappings(model_to_update, values_to_update_in_chunk)
    db.session.commit()


def _filter_matching_pc_object_in_chunk(model_in_chunk: Model, chunk_to_update: dict) -> list[Model]:  # type: ignore [valid-type]
    return list(
        filter(lambda item: _extract_model_name_from_chunk_key(item[0]) == model_in_chunk, chunk_to_update.items())  # type: ignore [index]
    )


def _extract_dict_values_from_chunk(matching_tuples_in_chunk: list[Model]) -> list[dict]:  # type: ignore [valid-type]
    return list(dictify_pc_object(pc_object_item) for pc_object_key, pc_object_item in matching_tuples_in_chunk)  # type: ignore [misc, has-type]


def get_existing_object(model_type: Model, id_at_providers: str) -> dict | None:  # type: ignore [valid-type]
    # exception to the ProvidableMixin because Offer no longer extends this class
    # idAtProviders has been replaced by idAtProvider property
    if model_type == Offer:
        return model_type.query.filter_by(idAtProvider=id_at_providers).one_or_none()  # type: ignore [attr-defined]

    return model_type.query.filter_by(idAtProviders=id_at_providers).one_or_none()  # type: ignore [attr-defined]


def get_last_update_for_provider(provider_id: int, pc_obj: Model) -> datetime:  # type: ignore [valid-type]
    if pc_obj.lastProviderId == provider_id:  # type: ignore [attr-defined]
        return pc_obj.dateModifiedAtLastProvider if pc_obj.dateModifiedAtLastProvider else None  # type: ignore [attr-defined]
    return None


def dictify_pc_object(object_to_update: Model) -> dict:  # type: ignore [valid-type]
    dict_to_update = object_to_update.__dict__.copy()  # type: ignore [attr-defined]
    if "_sa_instance_state" in dict_to_update:
        del dict_to_update["_sa_instance_state"]
    if "datePublished" in dict_to_update:
        del dict_to_update["datePublished"]
    if "venue" in dict_to_update:
        del dict_to_update["venue"]
    if "offer" in dict_to_update:
        del dict_to_update["offer"]
    if "stocks" in dict_to_update:
        del dict_to_update["stocks"]
    if "remainingQuantity" in dict_to_update:
        del dict_to_update["remainingQuantity"]
    return dict_to_update


def _extract_model_name_from_chunk_key(chunk_key: str) -> str:
    return chunk_key.split("|")[1]
