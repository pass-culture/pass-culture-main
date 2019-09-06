from typing import Dict, Optional

from local_providers.providable_info import ProvidableInfo
from models import ProvidableMixin
from models.db import Model
from repository.providable_queries import get_existing_object_or_none, save_chunk_to_insert, save_chunk_to_update


def get_existing_pc_obj(providable_info: ProvidableInfo,
                        chunk_to_insert: Dict,
                        chunk_to_update: Dict):
    object_in_current_chunk = get_object_from_current_chunks(providable_info,
                                                             chunk_to_insert,
                                                             chunk_to_update)
    if object_in_current_chunk is None:
        return get_existing_object_or_none(providable_info.type, providable_info.id_at_providers)
    else:
        return object_in_current_chunk


def get_object_from_current_chunks(providable_info: ProvidableInfo,
                                   chunk_to_insert: Dict,
                                   chunk_to_update: Dict) -> Optional[Model]:
    chunk_key = providable_info.id_at_providers + '|' + str(providable_info.type.__name__)
    if chunk_key in chunk_to_insert:
        pc_object = chunk_to_insert[chunk_key]
        if type(pc_object) == providable_info.type:
            return pc_object
    if chunk_key in chunk_to_update:
        pc_object = chunk_to_update[chunk_key]
        if type(pc_object) == providable_info.type:
            return pc_object
    return None


def save_chunks(chunk_to_insert: Dict[str, ProvidableMixin], chunk_to_update: Dict[str, ProvidableMixin],
                providable_info: ProvidableInfo):
    if len(chunk_to_insert) > 0:
        save_chunk_to_insert(chunk_to_insert)

    if len(chunk_to_update) > 0:
        save_chunk_to_update(chunk_to_update, providable_info)
