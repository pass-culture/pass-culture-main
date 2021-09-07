import logging

from pcapi.core.categories import subcategories
from pcapi.domain.music_types import music_types
from pcapi.domain.show_types import show_types
from pcapi.model_creators.specific_creators import create_product_with_event_subcategory
from pcapi.repository import repository
from pcapi.sandboxes.scripts.mocks.event_mocks import MOCK_ACTIVATION_DESCRIPTION
from pcapi.sandboxes.scripts.mocks.event_mocks import MOCK_ACTIVATION_NAME
from pcapi.sandboxes.scripts.mocks.event_mocks import MOCK_DESCRIPTIONS
from pcapi.sandboxes.scripts.mocks.event_mocks import MOCK_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_FIRST_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_LAST_NAMES


logger = logging.getLogger(__name__)


EVENT_COUNTS_PER_TYPE = 7


def create_industrial_event_products():
    logger.info("create_industrial_event_products")

    event_products_by_name = {}

    event_subcategories = [s for s in subcategories.ALL_SUBCATEGORIES if s.is_event]

    activation_index = 0

    for product_creation_counter in range(0, EVENT_COUNTS_PER_TYPE):

        for (event_subcategories_list_index, event_subcategory) in enumerate(event_subcategories):

            mock_index = (product_creation_counter + event_subcategories_list_index) % len(MOCK_NAMES)
            if event_subcategory == subcategories.ACTIVATION_EVENT:
                event_name = "{} {}".format(MOCK_ACTIVATION_NAME, activation_index)
                description = MOCK_ACTIVATION_DESCRIPTION
                activation_index += 1
            else:
                event_name = MOCK_NAMES[mock_index]
                description = MOCK_DESCRIPTIONS[mock_index]

            name = "{} / {}".format(event_subcategory.id, event_name)
            event_product = create_product_with_event_subcategory(
                description=description,
                duration_minutes=60,
                event_name=event_name,
                event_subcategory_id=event_subcategory.id,
                thumb_count=0,
            )

            extraData = {}
            extra_data_index = 0
            for conditionalField in event_product.subcategory.conditional_fields:
                conditional_index = product_creation_counter + event_subcategories_list_index + extra_data_index
                if conditionalField in ["author", "performer", "speaker", "stageDirector"]:
                    mock_first_name_index = conditional_index % len(MOCK_FIRST_NAMES)
                    mock_first_name = MOCK_FIRST_NAMES[mock_first_name_index]
                    mock_last_name_index = conditional_index % len(MOCK_LAST_NAMES)
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
                elif conditionalField == "showType":
                    show_type_index = conditional_index % len(show_types)
                    show_type = show_types[show_type_index]
                    extraData[conditionalField] = str(show_type["code"])
                    show_sub_type_index = conditional_index % len(show_type["children"])
                    show_sub_type = show_type["children"][show_sub_type_index]
                    extraData["showSubType"] = str(show_sub_type["code"])
                elif conditionalField == "visa":
                    pass
                extra_data_index += 1
            event_product.extraData = extraData
            event_products_by_name[name] = event_product

        product_creation_counter += len(event_subcategories)

    repository.save(*event_products_by_name.values())

    logger.info("created %d event products", len(event_products_by_name))

    return event_products_by_name
