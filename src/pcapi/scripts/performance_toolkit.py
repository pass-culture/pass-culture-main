from typing import List
from typing import Optional

from sqlalchemy import select

from pcapi.models.db import Model
from pcapi.models.db import db
from pcapi.repository.providable_queries import _dict_to_object
from pcapi.repository.providable_queries import dictify_pc_object


CHUNK_SIZE = 1000


def get_pc_object_by_id_in_database(pc_object_id: int, pc_model: Model) -> Optional[Model]:
    connection = db.engine.connect()
    query = select([pc_model]).where(pc_model.id == pc_object_id)
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
