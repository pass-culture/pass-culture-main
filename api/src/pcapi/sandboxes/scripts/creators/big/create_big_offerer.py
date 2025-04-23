import datetime
import logging

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.factories import VirtualVenueFactory
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory


logger = logging.getLogger(__name__)


def create_big_offerer() -> None:
    logger.info("start create big offerer")
    user_offerer = UserOffererFactory.create(user__email="gros@example.com", offerer__name="Gros offerer")
    # offerers have always a virtual venue so we have to create one to match reality
    VirtualVenueFactory.create(name="Lieu virtuel du gros offerer", managingOfferer=user_offerer.offerer)
    logger.info(" you can connect to pro, before end of sandbox, with : gros@example.com")
    for i in range(0, 51):
        venue = VenueFactory.create(
            name=f"Lieu du gros offerer {i}",
            managingOfferer=user_offerer.offerer,
        )
        for j in range(0, 100):
            offer_event = EventOfferFactory.create(
                name=f"Conférence {j} lieu {i} ",
                venue=venue,
                subcategoryId=subcategories.CONFERENCE.id,
            )
            stock = EventStockFactory.create(
                offer=offer_event,
                quantity=10,
                beginningDatetime=datetime.datetime.utcnow().replace(second=0, microsecond=0)
                + datetime.timedelta(days=20),
            )
            BookingFactory.create(quantity=1, stock=stock)
        logger.info("create venue %d of big offerer", i)
    logger.info("end create big offerer with 5k+ booked offers")
