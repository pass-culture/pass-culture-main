import logging

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.core.categories import subcategories
from pcapi.repository import repository
from pcapi.sandboxes.scripts.mocks.thing_mocks import MOCK_NAMES


logger = logging.getLogger(__name__)


DEACTIVATED_OFFERS_PICK_MODULO = 3
THINGS_PER_OFFERER = 5


def create_industrial_thing_offers(
    offerers_by_name: dict[str, offerers_models.Offerer],
    venues_by_name: dict[str, offerers_models.Venue],
) -> dict[str, offers_models.Offer]:
    logger.info("create_industrial_thing_offers")

    thing_offers_by_name: dict[str, offers_models.Offer] = {}

    thing_subcategories = [s for s in subcategories.ALL_SUBCATEGORIES if not s.is_event]

    id_at_provider = 1234
    thing_index = 0
    offer_index = 0
    for offerer in offerers_by_name.values():
        virtual_venue = next(venue for venue in offerer.managedVenues if venue.isVirtual)

        physical_venue_name = virtual_venue.name.replace(" (Offre numérique)", "")
        physical_venue = venues_by_name.get(physical_venue_name)

        for venue_thing_index in range(0, THINGS_PER_OFFERER):
            thing_venue = None
            subcategory_index = (venue_thing_index + thing_index) % len(thing_subcategories)
            subcategory = thing_subcategories[subcategory_index]
            thing_name_index = (venue_thing_index + thing_index) % len(MOCK_NAMES)
            thing_name = MOCK_NAMES[thing_name_index]

            if subcategory.is_offline_only:
                thing_venue = physical_venue
            elif subcategory.is_online_only:
                thing_venue = virtual_venue
            else:
                thing_venue = physical_venue

            if thing_venue is None:
                continue

            name = "{} / {}".format(thing_name, thing_venue.name)
            if offer_index % DEACTIVATED_OFFERS_PICK_MODULO == 0:
                is_active = False
            else:
                is_active = True
            thing_offers_by_name[name] = offers_factories.OfferFactory.create(
                venue=thing_venue,
                subcategoryId=subcategory.id,
                isActive=is_active,
                url="http://example.com" if subcategory.is_online_only else None,
                idAtProvider=str(id_at_provider),
                extraData=offers_factories.build_extra_data_from_subcategory(subcategory.id, set_all_fields=False),
            )
            offer_index += 1
            id_at_provider += 1

        thing_index += THINGS_PER_OFFERER

    repository.save(*thing_offers_by_name.values())

    logger.info("created %d thing_offers", len(thing_offers_by_name))

    return thing_offers_by_name
