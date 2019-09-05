import datetime
from typing import Optional, Dict

from sqlalchemy import select

from local_providers.providable_info import ProvidableInfo
from models import PcObject
from models.db import db
from utils.date import read_json_date
from utils.human_ids import humanize


def get_existing_pc_obj(providable_info: ProvidableInfo,
                        chunk_to_insert: Dict,
                        chunk_to_update: Dict):
    object_in_current_chunk = get_object_from_current_chunks(providable_info,
                                                             chunk_to_insert,
                                                             chunk_to_update)
    if object_in_current_chunk is None:
        return get_existing_object_or_none(providable_info)
    else:
        return object_in_current_chunk


def get_object_from_current_chunks(providable_info: ProvidableInfo,
                                   chunk_to_insert: Dict,
                                   chunk_to_update: Dict) -> Optional[PcObject]:
    chunk_key = providable_info.idAtProviders + '|' + str(providable_info.type.__name__)
    if chunk_key in chunk_to_insert:
        pc_object = chunk_to_insert[chunk_key]
        if type(pc_object) == providable_info.type:
            return pc_object
    if chunk_key in chunk_to_update:
        pc_object = chunk_to_update[chunk_key]
        if type(pc_object) == providable_info.type:
            return pc_object
    return None


def get_existing_object_or_none(providable_info: ProvidableInfo):
    conn = db.engine.connect()
    model_to_query = providable_info.type
    query = select([model_to_query]). \
        where(model_to_query.idAtProviders == providable_info.idAtProviders)
    db_object_dict = conn.execute(query).fetchone()

    if db_object_dict is not None:
        return dict_to_object(db_object_dict, model_to_query)
    return None


def get_last_modification_date_for_provider(provider_id: int, obj) -> datetime:
    if obj.lastProviderId == provider_id:
        return obj.dateModifiedAtLastProvider
    for change in obj.activity():
        if change.changed_data['lastProviderId'] == provider_id:
            return read_json_date(change.changed_data['dateModifiedAtLastProvider'])


def dict_to_object(object_dict: Dict, model_object: PcObject) -> PcObject:
    pc_object = {}
    for key, value in object_dict.items():
        if key.endswith('Id'):
            pc_object[key] = humanize(value)
        else:
            pc_object[key] = value
    pc_obj = model_object(from_dict=pc_object)
    pc_obj.id = pc_object['id']
    return pc_obj
