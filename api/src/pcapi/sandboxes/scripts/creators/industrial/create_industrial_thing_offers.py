import logging

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.repository import repository


logger = logging.getLogger(__name__)


DEACTIVATED_OFFERS_PICK_MODULO = 3
THINGS_PER_OFFERER = 5


def create_industrial_thing_offers(
    thing_products_by_name: dict[str, offers_models.Product],
    offerers_by_name: dict[str, offerers_models.Offerer],
    venues_by_name: dict[str, offerers_models.Venue],
) -> dict[str, offers_models.Offer]:
    logger.info("create_industrial_thing_offers")

    thing_offers_by_name: dict[str, offers_models.Offer] = {}

    id_at_provider = 1234
    thing_index = 0
    offer_index = 0
    thing_items = list(thing_products_by_name.items())
    for offerer in offerers_by_name.values():
        virtual_venue = [venue for venue in offerer.managedVenues if venue.isVirtual][0]

        physical_venue_name = virtual_venue.name.replace(" (Offre numérique)", "")
        physical_venue = venues_by_name.get(physical_venue_name)

        for venue_thing_index in range(0, THINGS_PER_OFFERER):
            thing_venue = None
            while thing_venue is None:
                rest_thing_index = (venue_thing_index + thing_index) % len(thing_items)
                (thing_name, thing_product) = thing_items[rest_thing_index]
                if thing_product.subcategory.is_offline_only:
                    thing_venue = physical_venue
                elif thing_product.subcategory.is_online_only:
                    thing_venue = virtual_venue
                else:
                    thing_venue = physical_venue

                thing_index += 1

            name = "{} / {}".format(thing_name, thing_venue.name)
            if offer_index % DEACTIVATED_OFFERS_PICK_MODULO == 0:
                is_active = False
            else:
                is_active = True
            thing_offers_by_name[name] = offers_factories.OfferFactory(
                venue=thing_venue,
                subcategoryId=thing_product.subcategoryId,
                isActive=is_active,
                url="http://example.com" if thing_product.isDigital else None,
                idAtProvider=str(id_at_provider),
                extraData=thing_product.extraData,
            )
            offer_index += 1
            id_at_provider += 1

        thing_index += THINGS_PER_OFFERER

    repository.save(*thing_offers_by_name.values())

    logger.info("created %d thing_offers", len(thing_offers_by_name))

    return thing_offers_by_name
