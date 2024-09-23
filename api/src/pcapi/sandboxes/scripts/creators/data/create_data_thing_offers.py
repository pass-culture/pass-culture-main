import logging

from pcapi.core.categories import subcategories_v2
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.repository import repository


logger = logging.getLogger(__name__)

THINGS_PER_OFFERER = 5


def create_data_thing_offers(
    offerers_by_name: dict[str, offerers_models.Offerer],
    venues_by_name: dict[str, offerers_models.Venue],
) -> dict[str, offers_models.Offer]:
    logger.info("create_data_thing_offers_data")
    thing_offers_by_name: dict[str, offers_models.Offer] = {}
    id_at_provider = 5678
    thing_index = 0
    venue_thing_index = 0
    offer_index = 0
    thing_subcategories = [s for s in subcategories_v2.ALL_SUBCATEGORIES if not s.is_event]
    for offerer in offerers_by_name.values():
        subcategory_index = (venue_thing_index + thing_index) % len(thing_subcategories)
        subcategory = thing_subcategories[subcategory_index]
        virtual_venue = list(offerer.managedVenues)[0]
        physical_venue_name = virtual_venue.name.replace(" (Offre numérique)", "")
        physical_venue = venues_by_name.get(physical_venue_name)
        current_offers_count = 0
        for venue_thing_index in range(0, THINGS_PER_OFFERER):
            logger.info("creating offers for venue idx %d...", venue_thing_index)
            thing_venue = physical_venue
            thing_name = ""

            if subcategory.is_online_only:
                continue

            if thing_venue:
                name = f"{thing_name} / {thing_venue.name} / DATA"
                is_active = True
                thing_offers_by_name[name] = offers_factories.OfferFactory(
                    venue=thing_venue,
                    subcategoryId=subcategory.id,
                    isActive=is_active,
                    idAtProvider=str(id_at_provider),
                    extraData=offers_factories.build_extra_data_from_subcategory(subcategory.id, set_all_fields=False),
                )
                offer_index += 1
                id_at_provider += 1
                current_offers_count += 1
        thing_index += current_offers_count
    repository.save(*thing_offers_by_name.values())

    logger.info("created %d thing_offers_data", len(thing_offers_by_name))

    return thing_offers_by_name
