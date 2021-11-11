import logging

from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.repository import repository


logger = logging.getLogger(__name__)


DEACTIVATED_OFFERS_PICK_MODULO = 3
EVENTS_PER_OFFERER_WITH_PHYSICAL_VENUE = 5


def create_industrial_event_offers(events_by_name, offerers_by_name):
    logger.info("create_industrial_event_offers")

    event_offers_by_name = {}

    event_index = 0
    offer_index = 0

    event_items = list(events_by_name.items())

    for offerer in offerers_by_name.values():

        event_venues = [venue for venue in offerer.managedVenues if not venue.isVirtual]

        if not event_venues:
            continue

        event_venue = event_venues[0]

        for venue_event_index in range(0, EVENTS_PER_OFFERER_WITH_PHYSICAL_VENUE):

            rest_event_index = (venue_event_index + event_index) % len(event_items)

            (event_name, event) = event_items[rest_event_index]

            name = "{} / {}".format(event_name, event_venue.name)
            if offer_index % DEACTIVATED_OFFERS_PICK_MODULO == 0:
                is_active = False
            else:
                is_active = True
            if offer_index % DEACTIVATED_OFFERS_PICK_MODULO == 0:
                is_duo = False
            else:
                is_duo = True
            event_offers_by_name[name] = create_offer_with_event_product(
                event_venue, product=event, event_subcategory_id=event.subcategoryId, is_active=is_active, is_duo=is_duo
            )
            offer_index += 1

        event_index += EVENTS_PER_OFFERER_WITH_PHYSICAL_VENUE

    repository.save(*event_offers_by_name.values())

    logger.info("created %d event_offers", len(event_offers_by_name))

    return event_offers_by_name
