from models.pc_object import PcObject
from sandboxes.scripts.utils.storage_utils import store_public_object_from_sandbox_assets
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_object(model, mock):
    logger.info("look " + model.__name__ + " " + mock.get('id'))

    obj = model.query.filter_by(id=dehumanize(mock['id'])).first()

    if obj is None:
        obj = model(from_dict=mock)
        if 'id' in mock:
            obj.id = dehumanize(mock['id'])
        PcObject.check_and_save(obj)
        if 'thumbName' in mock:
            store_public_object_from_sandbox_assets(
                "thumbs",
                obj,
                mock['thumbName']
            )
        logger.info("created " + " " + model.__name__ + " " + str(obj))
    else:
        logger.info("--already here-- " + model.__name__ + " " + str(obj))

    return mock

def create_or_find_objects(model, *mocks):
    count = str(len(mocks))
    logger.info(model.__name__ + " mocks " + count)

    objs = []
    for (index, mock) in enumerate(mocks):
        logger.info(str(index) + "/" + count)
        obj = create_or_find_object(model, mock)
        objs.append(obj)

    return objs
