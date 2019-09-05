from io import BytesIO
from typing import Dict

import models
from connectors.thumb_storage import save_thumb
from local_providers.providable_info import ProvidableInfo
from models import ProvidableMixin, PcObject
from models.db import db
from utils.logger import logger


def save_chunks(chunk_to_insert: Dict[str, ProvidableMixin], chunk_to_update: Dict[str, ProvidableMixin],
                providable_info: ProvidableInfo):
    if len(chunk_to_insert) > 0:
        db.session.bulk_save_objects(chunk_to_insert.values())
        db.session.commit()

    if len(chunk_to_update) > 0:
        save_chunk_to_update(chunk_to_update, providable_info)


def save_chunk_to_update(chunk_to_update: Dict, providable_info: ProvidableInfo):
    conn = db.engine.connect()

    for chunk_key, chunk_object in chunk_to_update.items():
        try:
            model_name = chunk_key.split('|')[1]
            model_object = getattr(models, model_name)
        except AttributeError:
            model_object = providable_info.type

        dict_to_update = _build_dict_to_update(chunk_object)

        statement = model_object.__table__.update(). \
            where(model_object.id == dict_to_update['id']). \
            values(dict_to_update)
        try:
            conn.execute(statement)
        except ValueError as e:
            logger.error('ERROR during object update: '
                         + e.__class__.__name__ + ' ' + str(e))


def save_thumb_from_thumb_count_to_index(index: int, obj: PcObject, thumb: BytesIO):
    counter = obj.thumbCount
    while obj.thumbCount <= index:
        save_thumb(obj, thumb, counter, need_save=False)
        counter += 1


def _build_dict_to_update(object_to_update: PcObject) -> Dict:
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
    return dict_to_update
