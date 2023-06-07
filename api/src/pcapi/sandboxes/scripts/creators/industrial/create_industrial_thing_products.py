import logging
import random

from pcapi.core.categories import subcategories_v2
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.domain.music_types import music_types
from pcapi.repository import repository
from pcapi.sandboxes.scripts.mocks.thing_mocks import MOCK_AUTHOR_NAMES
from pcapi.sandboxes.scripts.mocks.thing_mocks import MOCK_DESCRIPTIONS
from pcapi.sandboxes.scripts.mocks.thing_mocks import MOCK_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_FIRST_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_LAST_NAMES


logger = logging.getLogger(__name__)


THINGS_PER_SUBCATEGORY = 7


def create_industrial_thing_products() -> dict[str, offers_models.Product]:
    logger.info("create_industrial_thing_products")

    thing_products_by_name = {}

    thing_subcategories = [s for s in subcategories_v2.ALL_SUBCATEGORIES if not s.is_event]

    id_at_providers = 1234

    for product_creation_counter in range(0, THINGS_PER_SUBCATEGORY):
        for thing_subcategories_list_index, thing_subcategory in enumerate(thing_subcategories):
            mock_index = (product_creation_counter + thing_subcategories_list_index) % len(MOCK_NAMES)

            name = "{} / {}".format(thing_subcategory.id, MOCK_NAMES[mock_index])
            is_online_only = thing_subcategory.is_online_only
            url = "https://ilestencoretemps.fr/" if is_online_only else None

            thing_product = offers_factories.ProductFactory(
                extraData={"author": MOCK_AUTHOR_NAMES[mock_index]},
                description=MOCK_DESCRIPTIONS[mock_index],
                idAtProviders=str(id_at_providers),
                isNational=is_online_only,
                name=MOCK_NAMES[mock_index],
                subcategoryId=thing_subcategory.id,
                url=url,
            )

            extraData = {}
            extra_data_index = 0
            for conditionalField_name in thing_product.subcategory.conditional_fields:
                conditional_index = product_creation_counter + thing_subcategories_list_index + extra_data_index
                if conditionalField_name in [
                    subcategories_v2.ExtraDataFieldEnum.AUTHOR.value,
                    subcategories_v2.ExtraDataFieldEnum.PERFORMER.value,
                    subcategories_v2.ExtraDataFieldEnum.SPEAKER.value,
                    subcategories_v2.ExtraDataFieldEnum.STAGE_DIRECTOR.value,
                ]:
                    mock_first_name_index = (
                        product_creation_counter + thing_subcategories_list_index + extra_data_index
                    ) % len(MOCK_FIRST_NAMES)
                    mock_first_name = MOCK_FIRST_NAMES[mock_first_name_index]
                    mock_last_name_index = (
                        product_creation_counter + thing_subcategories_list_index + extra_data_index
                    ) % len(MOCK_LAST_NAMES)
                    mock_last_name = MOCK_LAST_NAMES[mock_last_name_index]
                    mock_name = "{} {}".format(mock_first_name, mock_last_name)
                    extraData[conditionalField_name] = mock_name
                elif conditionalField_name == "musicType":
                    music_type_index: int = conditional_index % len(music_types)
                    music_type = music_types[music_type_index]
                    extraData[conditionalField_name] = str(music_type.code)
                    music_sub_type_index: int = conditional_index % len(music_type.children)
                    music_sub_type = music_type.children[music_sub_type_index]
                    extraData["musicSubType"] = str(music_sub_type.code)
                elif conditionalField_name == "ean":
                    extraData["ean"] = "".join(random.choices("123456789-", k=13))
                extra_data_index += 1
            thing_product.extraData = extraData
            thing_products_by_name[name] = thing_product
            id_at_providers += 1

        product_creation_counter += len(thing_subcategories)

    repository.save(*thing_products_by_name.values())

    logger.info("created %d thing products", len(thing_products_by_name))

    return thing_products_by_name
