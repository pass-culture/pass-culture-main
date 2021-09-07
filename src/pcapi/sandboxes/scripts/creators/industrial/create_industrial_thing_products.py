import logging

from pcapi.core.categories import subcategories
from pcapi.domain.music_types import music_types
from pcapi.model_creators.specific_creators import create_product_with_thing_subcategory
from pcapi.repository import repository
from pcapi.sandboxes.scripts.mocks.thing_mocks import MOCK_AUTHOR_NAMES
from pcapi.sandboxes.scripts.mocks.thing_mocks import MOCK_DESCRIPTIONS
from pcapi.sandboxes.scripts.mocks.thing_mocks import MOCK_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_FIRST_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_LAST_NAMES


logger = logging.getLogger(__name__)
from pcapi.utils.token import random_token


THINGS_PER_SUBCATEGORY = 7


def create_industrial_thing_products():
    logger.info("create_industrial_thing_products")

    thing_products_by_name = {}

    thing_subcategories = [s for s in subcategories.ALL_SUBCATEGORIES if not s.is_event]

    id_at_providers = 1234

    for product_creation_counter in range(0, THINGS_PER_SUBCATEGORY):

        for (thing_subcategories_list_index, thing_subcategory) in enumerate(thing_subcategories):

            mock_index = (product_creation_counter + thing_subcategories_list_index) % len(MOCK_NAMES)

            name = "{} / {}".format(thing_subcategory.id, MOCK_NAMES[mock_index])
            is_online_only = (
                thing_subcategory.online_offline_platform == subcategories.OnlineOfflinePlatformChoices.ONLINE.value
            )
            url = "https://ilestencoretemps.fr/" if is_online_only else None

            thing_product = create_product_with_thing_subcategory(
                author_name=MOCK_AUTHOR_NAMES[mock_index],
                description=MOCK_DESCRIPTIONS[mock_index],
                id_at_providers=str(id_at_providers),
                is_national=is_online_only,
                thing_name=MOCK_NAMES[mock_index],
                thing_subcategory_id=thing_subcategory.id,
                thumb_count=0,
                url=url,
            )

            extraData = {}
            extra_data_index = 0
            for conditionalField in thing_product.subcategory.conditional_fields:
                conditional_index = product_creation_counter + thing_subcategories_list_index + extra_data_index
                if conditionalField in ["author", "performer", "speaker", "stageDirector"]:
                    mock_first_name_index = (
                        product_creation_counter + thing_subcategories_list_index + extra_data_index
                    ) % len(MOCK_FIRST_NAMES)
                    mock_first_name = MOCK_FIRST_NAMES[mock_first_name_index]
                    mock_last_name_index = (
                        product_creation_counter + thing_subcategories_list_index + extra_data_index
                    ) % len(MOCK_LAST_NAMES)
                    mock_last_name = MOCK_LAST_NAMES[mock_last_name_index]
                    mock_name = "{} {}".format(mock_first_name, mock_last_name)
                    extraData[conditionalField] = mock_name
                elif conditionalField == "musicType":
                    music_type_index = conditional_index % len(music_types)
                    music_type = music_types[music_type_index]
                    extraData[conditionalField] = str(music_type["code"])
                    music_sub_type_index = conditional_index % len(music_type["children"])
                    music_sub_type = music_type["children"][music_sub_type_index]
                    extraData["musicSubType"] = str(music_sub_type["code"])
                elif conditionalField == "isbn":
                    extraData[conditionalField] = random_token(13)
                extra_data_index += 1
            thing_product.extraData = extraData
            thing_products_by_name[name] = thing_product
            id_at_providers += 1

        product_creation_counter += len(thing_subcategories)

    repository.save(*thing_products_by_name.values())

    logger.info("created %d thing products", len(thing_products_by_name))

    return thing_products_by_name
