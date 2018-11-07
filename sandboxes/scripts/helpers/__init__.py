from sandboxes.scripts.helpers.bookings import *
from sandboxes.scripts.helpers.deposits import *
from sandboxes.scripts.helpers.event_occurrences import *
from sandboxes.scripts.helpers.events import *
from sandboxes.scripts.helpers.mediations import *
from sandboxes.scripts.helpers.offerers import *
from sandboxes.scripts.helpers.offers import *
from sandboxes.scripts.helpers.recommendations import *
from sandboxes.scripts.helpers.stocks import *
from sandboxes.scripts.helpers.things import *
from sandboxes.scripts.helpers.user_offerers import *
from sandboxes.scripts.helpers.users import *
from sandboxes.scripts.helpers.venues import *

def default_create_or_find_object(mock, model):
    logger.info("look " + model.__name__ + " " + mock.get('id'))

    obj = model.query.get(dehumanize(mock['id']))

    if obj is None:
        obj = model(from_dict=mock)
        if 'id' in mock:
            obj.id = dehumanize(mock['id'])
        PcObject.check_and_save(obj)
        logger.info("created " + " " + model.__name__ + " " + str(obj))
    else:
        logger.info("--already here-- " + model.__name__ + " " + str(obj))

    return deposit

def create_or_find_objects(*mocks, create_or_find_object=default_create_or_find_object):
    count = str(len(mocks))
    logger.info(create_or_find_object.__name__ + " mocks " + count)

    objs = []
    for (index, mock) in enumerate(mocks):
        logger.info(str(index) + "/" + count)
        obj = create_or_find_object(mock)
        objs.append(obj)

    return objs
