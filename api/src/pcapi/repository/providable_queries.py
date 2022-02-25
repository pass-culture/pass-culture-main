import datetime
from typing import Optional

from pcapi.core.offers.models import Offer
from pcapi.models import Model
from pcapi.models import db


def insert_chunk(chunk_to_insert: dict):
    db.session.bulk_save_objects(chunk_to_insert.values(), return_defaults=False)
    db.session.commit()


def update_chunk(chunk_to_update: dict):
    # Access `Model.registry` here, not at module-scope,
    # because it may not be populated yet if this module is imported
    # too early.
    MODELS = {mapper.class_.__name__: mapper.class_ for mapper in Model.registry.mappers}

    models_in_chunk = set(_extract_model_name_from_chunk_key(key) for key in chunk_to_update.keys())

    for model_in_chunk in models_in_chunk:
        matching_tuples_in_chunk = _filter_matching_pc_object_in_chunk(model_in_chunk, chunk_to_update)
        values_to_update_in_chunk = _extract_dict_values_from_chunk(matching_tuples_in_chunk)
        model_to_update = MODELS[model_in_chunk]

        db.session.bulk_update_mappings(model_to_update, values_to_update_in_chunk)
    db.session.commit()


def _filter_matching_pc_object_in_chunk(model_in_chunk: Model, chunk_to_update: dict) -> list[Model]:
    return list(
        filter(lambda item: _extract_model_name_from_chunk_key(item[0]) == model_in_chunk, chunk_to_update.items())
    )


def _extract_dict_values_from_chunk(matching_tuples_in_chunk: list[Model]) -> list[dict]:
    return list(dictify_pc_object(pc_object_item) for pc_object_key, pc_object_item in matching_tuples_in_chunk)


def get_existing_object(model_type: Model, id_at_providers: str) -> Optional[dict]:
    # exception to the ProvidableMixin because Offer no longer extends this class
    # idAtProviders has been replaced by idAtProvider property
    if model_type == Offer:
        return model_type.query.filter_by(idAtProvider=id_at_providers).one_or_none()

    return model_type.query.filter_by(idAtProviders=id_at_providers).one_or_none()


def get_last_update_for_provider(provider_id: int, pc_obj: Model) -> datetime:
    if pc_obj.lastProviderId == provider_id:
        return pc_obj.dateModifiedAtLastProvider if pc_obj.dateModifiedAtLastProvider else None
    return None


def dictify_pc_object(object_to_update: Model) -> dict:
    dict_to_update = object_to_update.__dict__.copy()
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
