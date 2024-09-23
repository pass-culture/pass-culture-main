import logging

from pcapi.core.categories import subcategories_v2
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.repository import repository
from pcapi.sandboxes.scripts.mocks.event_mocks import MOCK_NAMES


logger = logging.getLogger(__name__)

EVENTS_PER_OFFERER_WITH_PHYSICAL_VENUE = 5


def create_e2e_event_offers(
    offerers_by_name: dict[str, offerers_models.Offerer],
) -> dict[str, offers_models.Offer]:
    logger.info("create_e2e_event_offers")

    event_offers_by_name = {}

    event_index = 0
    offer_index = 0

    event_subcategories = [s for s in subcategories_v2.ALL_SUBCATEGORIES if s.is_event and s.is_offline_only]

    for offerer in offerers_by_name.values():
        event_venues = [venue for venue in offerer.managedVenues if not venue.isVirtual]

        if not event_venues:
            continue

        event_venue = event_venues[0]

        for venue_event_index in range(0, EVENTS_PER_OFFERER_WITH_PHYSICAL_VENUE):
            event_subcategory_index = (venue_event_index + event_index) % len(event_subcategories)
            event_subcategory = event_subcategories[event_subcategory_index]
            mock_index = (venue_event_index + event_index) % len(MOCK_NAMES)
            event_name = MOCK_NAMES[mock_index]

            name = "{} / {}".format(event_name, event_venue.name)
            is_active = True
            is_duo = True
            event_offers_by_name[name] = offers_factories.OfferFactory(
                venue=event_venue,
                subcategoryId=event_subcategory.id,
                extraData=offers_factories.build_extra_data_from_subcategory(
                    event_subcategory.id, set_all_fields=False
                ),
                isActive=is_active,
                isDuo=is_duo,
            )
            offer_index += 1

        event_index += EVENTS_PER_OFFERER_WITH_PHYSICAL_VENUE

    repository.save(*event_offers_by_name.values())

    logger.info("created %d event_offers", len(event_offers_by_name))

    return event_offers_by_name
