import datetime
import logging

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def create_tiny_venue() -> None:
    logger.info("start create tiny venue")
    email = "tom.pouce@example.com"
    user_offerer = UserOffererFactory.create(
        user__email=email, offerer__name="Ma petite entreprise", user__firstName="Tom", user__lastName="Pouce"
    )
    logger.info(f"You can connect to pro with : {email}")
    venue = VenueFactory.create(
        name="Petit lieu",
        managingOfferer=user_offerer.offerer,
        adageId="123546",
    )
    offer_event = EventOfferFactory.create(
        name="Conférence gesticulée",
        venue=venue,
        subcategoryId=subcategories.CONFERENCE.id,
    )
    stock = EventStockFactory.create(
        offer=offer_event,
        quantity=10,
        beginningDatetime=date_utils.get_naive_utc_now().replace(second=0, microsecond=0) + datetime.timedelta(days=20),
    )
    BookingFactory.create(quantity=1, stock=stock)
    logger.info("end create tiny venue with 1 booked offers")
