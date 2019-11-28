from typing import List, Optional

from sqlalchemy import select

from models.db import db, Model
from repository.providable_queries import _dict_to_object, dictify_pc_object

CHUNK_SIZE = 1000


def get_pc_object_by_id_in_database(pc_object_id: int, pc_model: Model) -> Optional[Model]:
    connection = db.engine.connect()
    query = select([pc_model]). \
        where(pc_model.id == pc_object_id)
    db_object_dict = connection.execute(query).fetchone()
    if db_object_dict:
        return _dict_to_object(db_object_dict, pc_model)
    return None


def bulk_update_pc_objects(pc_objects_to_update: List[Model], pc_model: Model):
    values_to_update = list(dictify_pc_object(pc_object_item) for pc_object_item in pc_objects_to_update)
    db.session.bulk_update_mappings(pc_model, values_to_update)
    db.session.commit()


def bulk_insert_pc_objects(pc_objects_to_insert: List[Model], pc_model: Model):
    values_to_update = list(dictify_pc_object(pc_object_item) for pc_object_item in pc_objects_to_insert)
    db.session.bulk_insert_mappings(pc_model, values_to_update)
    db.session.commit()
