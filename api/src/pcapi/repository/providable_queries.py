import datetime

import pcapi.core.offers.models as offers_models
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db


def insert_chunk(chunk_to_insert: dict[str, Model]) -> None:
    db.session.add_all(chunk_to_insert.values())
    db.session.commit()


def update_chunk(chunk_to_update: dict[str, Model]) -> None:
    # Access `Model.registry` here, not at module-scope,
    # because it may not be populated yet if this module is imported too early.
    MODELS = {mapper.class_.__name__: mapper.class_ for mapper in Base.registry.mappers}

    models_in_chunk: set[str] = set(_extract_model_name_from_chunk_key(key) for key in chunk_to_update.keys())

    for model_in_chunk in models_in_chunk:
        matching_tuples_in_chunk = _filter_matching_pc_object_in_chunk(model_in_chunk, chunk_to_update)
        values_to_update_in_chunk = _extract_dict_values_from_chunk(matching_tuples_in_chunk)
        model_to_update = MODELS[model_in_chunk]

        db.session.bulk_update_mappings(model_to_update, values_to_update_in_chunk)
    db.session.commit()


def _filter_matching_pc_object_in_chunk(
    model_in_chunk: str, chunk_to_update: dict[str, Model]
) -> list[tuple[str, Model]]:
    return list(
        filter(lambda item: _extract_model_name_from_chunk_key(item[0]) == model_in_chunk, chunk_to_update.items())
    )


def _extract_dict_values_from_chunk(matching_tuples_in_chunk: list[tuple[str, Model]]) -> list[dict]:
    return list(dictify_pc_object(pc_object_item) for pc_object_key, pc_object_item in matching_tuples_in_chunk)


def get_last_update_for_provider(
    provider_id: int,
    pc_obj: offers_models.Product | offers_models.Offer | offers_models.Stock | None,
) -> datetime.datetime | None:
    if pc_obj and pc_obj.lastProviderId == provider_id:
        return pc_obj.dateModifiedAtLastProvider
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
