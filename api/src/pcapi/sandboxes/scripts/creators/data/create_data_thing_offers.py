import logging

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def create_data_thing_offers(
    thing_products_by_name: dict[str, offers_models.Product],
    offerers_by_name: dict[str, offerers_models.Offerer],
    venues_by_name: dict[str, offerers_models.Venue],
) -> dict[str, offers_models.Offer]:
    logger.info("create_data_thing_offers_data")
    things_per_offerer = (len(thing_products_by_name)) // (len(offerers_by_name))
    logger.info("things_per_offerer %d", things_per_offerer)
    thing_offers_by_name: dict[str, offers_models.Offer] = {}
    id_at_provider = 5678
    thing_index = 0
    offer_index = 0
    thing_items = list(thing_products_by_name.items())
    for offerer in offerers_by_name.values():
        virtual_venue = [venue for venue in offerer.managedVenues ][0]
        physical_venue_name = virtual_venue.name.replace(" (Offre numérique)", "")
        physical_venue = venues_by_name.get(physical_venue_name)
        # physical_venue = list(offerer.managedVenues)
        current_offers_count = 0
        for venue_thing_index in range(0, things_per_offerer):
            logger.info("creating offers for venue idx %d...", venue_thing_index)
            thing_venue = physical_venue
            thing_name = ""
            rest_thing_index = (venue_thing_index + thing_index) % len(thing_items)

            (thing_name, thing_product) = thing_items[rest_thing_index]
            if thing_product.subcategory.is_online_only:
                continue

            if thing_venue:
                name = f"{thing_name} / {thing_venue.name} / DATA"
                is_active = True
                thing_offers_by_name[name] = offers_factories.OfferFactory(
                    venue=thing_venue,
                    product=thing_product,
                    isActive=is_active,
                    idAtProvider=str(id_at_provider),
                )
                offer_index += 1
                id_at_provider += 1
                current_offers_count += 1
        thing_index += current_offers_count
    repository.save(*thing_offers_by_name.values())

    logger.info("created %d thing_offers_data", len(thing_offers_by_name))

    return thing_offers_by_name
