import datetime
from typing import Dict, Optional

from sqlalchemy import select

import models
from models.db import db, Model
from utils.date import read_json_date
from utils.human_ids import humanize
from utils.logger import logger


def insert_chunk(chunk_to_insert: Dict):
    db.session.bulk_save_objects(chunk_to_insert.values(), return_defaults=False)
    db.session.commit()


def update_chunk(chunk_to_update: Dict):
    for chunk_key, chunk_object in chunk_to_update.items():
        statement = _build_statement_for_update(chunk_key,
                                                chunk_object)
        try:
            connection = db.engine.connect()
            connection.execute(statement)
        except ValueError as e:
            logger.error('ERROR during object update: ' + e.__class__.__name__ + ' ' + str(e))


def get_existing_object(model_type: Model, id_at_providers: str) -> Optional[Dict]:
    conn = db.engine.connect()
    query = select([model_type]). \
        where(model_type.idAtProviders == id_at_providers)
    db_object_dict = conn.execute(query).fetchone()

    return _dict_to_object(db_object_dict, model_type) if db_object_dict else None


def get_last_update_for_provider(provider_id: int, pc_obj: Model) -> datetime:
    if pc_obj.lastProviderId == provider_id:
        return pc_obj.dateModifiedAtLastProvider
    for change in pc_obj.activity():
        if change.changed_data['lastProviderId'] == provider_id:
            return read_json_date(change.changed_data['dateModifiedAtLastProvider'])


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


def _build_statement_for_update(chunk_key: str, chunk_object: Model):
    model_name = chunk_key.split('|')[1]
    model_object = getattr(models, model_name)
    dict_to_update = _build_dict_to_update(chunk_object)
    statement = model_object.__table__.update(). \
        where(model_object.id == dict_to_update['id']). \
        values(dict_to_update)
    return statement


def _build_dict_to_update(object_to_update: Model) -> Dict:
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
