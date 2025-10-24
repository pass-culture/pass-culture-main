import logging

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.factories as providers_factories
from pcapi.core.categories import subcategories
from pcapi.models import db
from pcapi.sandboxes.scripts.mocks.thing_mocks import MOCK_NAMES
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


DEACTIVATED_OFFERS_PICK_MODULO = 3
THINGS_PER_OFFERER = 5


@log_func_duration
def create_industrial_thing_offers(
    offerers_by_name: dict[str, offerers_models.Offerer],
    venues_by_name: dict[str, offerers_models.Venue],
) -> dict[str, offers_models.Offer]:
    logger.info("create_industrial_thing_offers")

    thing_offers_by_name: dict[str, offers_models.Offer] = {}

    thing_subcategories = [s for s in subcategories.ALL_SUBCATEGORIES if not s.is_event]

    thing_index = 0
    offer_index = 0
    for offerer in offerers_by_name.values():
        physical_venue = sorted(offerer.managedVenues, key=lambda venue: venue.id)[0]

        for venue_thing_index in range(0, THINGS_PER_OFFERER):
            subcategory_index = (venue_thing_index + thing_index) % len(thing_subcategories)
            subcategory = thing_subcategories[subcategory_index]
            thing_name_index = (venue_thing_index + thing_index) % len(MOCK_NAMES)
            thing_name = MOCK_NAMES[thing_name_index]

            name = "{} / {}".format(thing_name, physical_venue.name)
            if offer_index % DEACTIVATED_OFFERS_PICK_MODULO == 0:
                is_active = False
            else:
                is_active = True
            thing_offers_by_name[name] = offers_factories.OfferFactory.create(
                venue=physical_venue,
                subcategoryId=subcategory.id,
                isActive=is_active,
                url="http://example.com" if subcategory.is_online_only else None,
                lastProvider=providers_factories.ProviderFactory(),
                extraData=offers_factories.build_extra_data_from_subcategory(subcategory.id, set_all_fields=False),
            )
            offer_index += 1

        thing_index += THINGS_PER_OFFERER

    db.session.add_all(thing_offers_by_name.values())
    db.session.commit()

    logger.info("created %d thing_offers", len(thing_offers_by_name))

    return thing_offers_by_name
