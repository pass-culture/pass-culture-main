import logging

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.domain.music_types import music_types
from pcapi.domain.show_types import show_types
from pcapi.repository import repository
from pcapi.sandboxes.scripts.mocks.event_mocks import MOCK_DESCRIPTIONS
from pcapi.sandboxes.scripts.mocks.event_mocks import MOCK_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_FIRST_NAMES
from pcapi.sandboxes.scripts.mocks.user_mocks import MOCK_LAST_NAMES


logger = logging.getLogger(__name__)

EVENT_COUNTS_PER_TYPE_DATA = 2


def create_data_event_products() -> dict[str, offers_models.Product]:
    logger.info("create_data_event_products_data")

    event_products_by_name = {}

    event_subcategories = [s for s in subcategories.ALL_SUBCATEGORIES if s.is_event and s.is_offline_only]

    for product_creation_counter in range(0, EVENT_COUNTS_PER_TYPE_DATA):
        for event_subcategories_list_index, event_subcategory in enumerate(event_subcategories):
            mock_index = (product_creation_counter + event_subcategories_list_index) % len(MOCK_NAMES)
            event_name = f"DATA {MOCK_NAMES[mock_index]}"
            description = MOCK_DESCRIPTIONS[mock_index]

            name = f"{event_subcategory.id} / {event_name} / DATA"
            event_product = offers_factories.ProductFactory(
                description=description,
                durationMinutes=60,
                name=event_name,
                subcategoryId=event_subcategory.id,
            )

            extra_data = {}
            extra_data_index = 0
            for conditional_field in event_product.subcategory.conditional_fields:
                conditional_index = product_creation_counter + event_subcategories_list_index + extra_data_index
                if conditional_field in ["author", "performer", "speaker", "stageDirector"]:
                    mock_first_name_index = conditional_index % len(MOCK_FIRST_NAMES)
                    mock_first_name = MOCK_FIRST_NAMES[mock_first_name_index]
                    mock_last_name_index = conditional_index % len(MOCK_LAST_NAMES)
                    mock_last_name = MOCK_LAST_NAMES[mock_last_name_index]
                    mock_name = f"{mock_first_name} {mock_last_name}"
                    extra_data[conditional_field] = mock_name
                elif conditional_field == "musicType":
                    music_type_index: int = conditional_index % len(music_types)
                    music_type = music_types[music_type_index]
                    extra_data[conditional_field] = str(music_type.code)
                    music_sub_type_index: int = conditional_index % len(music_type.children)
                    music_sub_type = music_type.children[music_sub_type_index]
                    extra_data["musicSubType"] = str(music_sub_type.code)
                elif conditional_field == "showType":
                    show_type_index: int = conditional_index % len(show_types)
                    show_type = show_types[show_type_index]
                    extra_data[conditional_field] = str(show_type.code)
                    show_sub_type_index: int = conditional_index % len(show_type.children)
                    show_sub_type = show_type.children[show_sub_type_index]
                    extra_data["showSubType"] = str(show_sub_type.code)
                elif conditional_field == "visa":
                    pass
                extra_data_index += 1
            event_product.extraData = extra_data
            event_products_by_name[name] = event_product

        product_creation_counter += len(event_subcategories)

    repository.save(*event_products_by_name.values())

    logger.info("created %d event products", len(event_products_by_name))

    return event_products_by_name
