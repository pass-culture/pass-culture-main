import datetime
from typing import Dict, Optional, List

from sqlalchemy import select

import models
from models.db import db, Model
from utils.human_ids import humanize


def insert_chunk(chunk_to_insert: Dict):
    db.session.bulk_save_objects(chunk_to_insert.values(), return_defaults=False)
    db.session.commit()


def update_chunk(chunk_to_update: Dict):
    models_in_chunk = set(_extract_model_name_from_chunk_key(key) for key in chunk_to_update.keys())

    for model_in_chunk in models_in_chunk:
        matching_tuples_in_chunk = _filter_matching_pc_object_in_chunk(model_in_chunk, chunk_to_update)
        values_to_update_in_chunk = _extract_dict_values_from_chunk(matching_tuples_in_chunk)
        model_to_update = getattr(models, model_in_chunk)

        db.session.bulk_update_mappings(model_to_update, values_to_update_in_chunk)
    db.session.commit()


def _filter_matching_pc_object_in_chunk(model_in_chunk: Model, chunk_to_update: Dict) -> List[Model]:
    return list(
        filter(lambda item: _extract_model_name_from_chunk_key(item[0]) == model_in_chunk,
               chunk_to_update.items())
    )


def _extract_dict_values_from_chunk(matching_tuples_in_chunk: List[Model]) -> List[Dict]:
    return list(
        dictify_pc_object(pc_object_item) for pc_object_key, pc_object_item in matching_tuples_in_chunk
    )


def get_existing_object(model_type: Model, id_at_providers: str) -> Optional[Dict]:
    conn = db.engine.connect()
    query = select([model_type]). \
        where(model_type.idAtProviders == id_at_providers)
    db_object_dict = conn.execute(query).fetchone()

    return _dict_to_object(db_object_dict, model_type) if db_object_dict else None


def get_last_update_for_provider(provider_id: int, pc_obj: Model) -> datetime:
    if pc_obj.lastProviderId == provider_id:
        return pc_obj.dateModifiedAtLastProvider if pc_obj.dateModifiedAtLastProvider else None
    return None


def _dict_to_object(object_dict: Dict, model_object: Model) -> Model:
    pc_object = {}
    for key, value in object_dict.items():
        if key.endswith('Id'):
            pc_object[key] = humanize(value)
        else:
            pc_object[key] = value
    pc_obj = model_object(from_dict=pc_object)
    pc_obj.id = pc_object['id']
    return pc_obj


def dictify_pc_object(object_to_update: Model) -> Dict:
    dict_to_update = object_to_update.__dict__
    if '_sa_instance_state' in dict_to_update:
        del dict_to_update['_sa_instance_state']
    if 'datePublished' in dict_to_update:
        del dict_to_update['datePublished']
    if 'venue' in dict_to_update:
        del dict_to_update['venue']
    if 'offer' in dict_to_update:
        del dict_to_update['offer']
    if 'stocks' in dict_to_update:
        del dict_to_update['stocks']
    if 'baseScore' in dict_to_update:
        del dict_to_update['baseScore']
    if 'remainingQuantity' in dict_to_update:
        del dict_to_update['remainingQuantity']
    return dict_to_update


def _extract_model_name_from_chunk_key(chunk_key: str) -> str:
    return chunk_key.split('|')[1]
