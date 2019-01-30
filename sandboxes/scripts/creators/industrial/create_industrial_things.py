from domain.types import get_formatted_event_or_thing_types
from models.pc_object import PcObject
from sandboxes.scripts.mocks.thing_mocks import MOCK_AUTHOR_NAMES, \
                                                MOCK_DESCRIPTIONS, \
                                                MOCK_NAMES
from utils.logger import logger
from utils.test_utils import create_thing

THINGS_PER_TYPE = 7

def create_industrial_things():
    logger.info('create_industrial_things')

    things_by_name = {}

    thing_type_dicts = [
        t for t in get_formatted_event_or_thing_types()
        if t['type'] == 'Thing'
    ]

    id_at_providers = 1234

    for type_index in range(0, THINGS_PER_TYPE):

        for (thing_type_dict_index, thing_type_dict) in enumerate(thing_type_dicts):

            mock_index = (type_index + thing_type_dict_index) % len(MOCK_NAMES)

            name = "{} / {}".format(thing_type_dict['value'], MOCK_NAMES[mock_index])
            is_national = True if thing_type_dict['onlineOnly'] else False
            url = 'https://ilestencoretemps.fr/' if thing_type_dict['onlineOnly'] else None
            things_by_name[name] = create_thing(
                author_name=MOCK_AUTHOR_NAMES[mock_index],
                description=MOCK_DESCRIPTIONS[mock_index],
                id_at_providers=str(id_at_providers),
                is_national=is_national,
                thing_name=MOCK_NAMES[mock_index],
                thing_type=thing_type_dict['value'],
                url=url
            )

            id_at_providers += 1

        type_index += len(thing_type_dicts)

    PcObject.check_and_save(*things_by_name.values())

    logger.info('created {} things'.format(len(things_by_name)))

    return things_by_name
