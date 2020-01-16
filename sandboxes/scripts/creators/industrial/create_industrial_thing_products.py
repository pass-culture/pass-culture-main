from domain.music_types import music_types
from domain.types import get_formatted_active_product_types
from sandboxes.scripts.mocks.thing_mocks import MOCK_AUTHOR_NAMES, \
    MOCK_DESCRIPTIONS, \
    MOCK_NAMES
from sandboxes.scripts.mocks.user_mocks import MOCK_FIRST_NAMES, \
    MOCK_LAST_NAMES
from tests.model_creators.specific_creators import create_product_with_thing_type
from utils.logger import logger
from utils.token import random_token

THINGS_PER_TYPE = 7

def create_industrial_thing_products():
    logger.info('create_industrial_thing_products')

    thing_products_by_name = {}

    thing_type_dicts = [
        t for t in get_formatted_active_product_types()
        if t['type'] == 'Thing'
    ]

    id_at_providers = 1234

    for type_index in range(0, THINGS_PER_TYPE):

        for (thing_type_dict_index, thing_type_dict) in enumerate(thing_type_dicts):

            mock_index = (type_index + thing_type_dict_index) % len(MOCK_NAMES)

            name = "{} / {}".format(thing_type_dict['value'], MOCK_NAMES[mock_index])
            is_national = True if thing_type_dict['onlineOnly'] else False
            url = 'https://ilestencoretemps.fr/' if thing_type_dict['onlineOnly'] else None
            thing_product = create_product_with_thing_type(
                author_name=MOCK_AUTHOR_NAMES[mock_index],
                description=MOCK_DESCRIPTIONS[mock_index],
                id_at_providers=str(id_at_providers),
                is_national=is_national,
                thing_name=MOCK_NAMES[mock_index],
                thing_type=thing_type_dict['value'],
                thumb_count=0,
                url=url
            )

            extraData = {}
            extra_data_index = 0
            for conditionalField in thing_product.offerType['conditionalFields']:
                conditional_index = type_index + thing_type_dict_index + extra_data_index
                if conditionalField in ['author', 'performer', 'speaker', 'stageDirector']:
                    mock_first_name_index = (type_index + thing_type_dict_index + extra_data_index) % len(MOCK_FIRST_NAMES)
                    mock_first_name = MOCK_FIRST_NAMES[mock_first_name_index]
                    mock_last_name_index = (type_index + thing_type_dict_index + extra_data_index) % len(MOCK_LAST_NAMES)
                    mock_last_name = MOCK_LAST_NAMES[mock_last_name_index]
                    mock_name = '{} {}'.format(mock_first_name, mock_last_name)
                    extraData[conditionalField] = mock_name
                elif conditionalField == "musicType":
                    music_type_index = conditional_index % len(music_types)
                    music_type = music_types[music_type_index]
                    extraData[conditionalField] = str(music_type['code'])
                    music_sub_type_index = conditional_index % len(music_type['children'])
                    music_sub_type = music_type['children'][music_sub_type_index]
                    extraData["musicSubType"] = str(music_sub_type['code'])
                elif conditionalField == "isbn":
                    extraData[conditionalField] = random_token(13)
                extra_data_index += 1
            thing_product.extraData = extraData

            thing_products_by_name[name] = thing_product

            id_at_providers += 1

        type_index += len(thing_type_dicts)

    Repository.save(*thing_products_by_name.values())

    logger.info('created {} thing products'.format(len(thing_products_by_name)))

    return thing_products_by_name
