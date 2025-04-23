import datetime
import logging

from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories


logger = logging.getLogger(__name__)


def _create_event_with_opening_hours(
    startDatetime: datetime.datetime,
    endDatetime: datetime.datetime | None,
    subcategoryId: str,
    venue: offerers_models.Venue,
    isActive: bool = True,
    isSoftDeleted: bool = False,
) -> None:
    subcategoryId = subcategoryId or subcategories.VISITE.id
    offer = offers_factories.OfferFactory.create(isActive=isActive, subcategoryId=subcategoryId, venue=venue)
    offers_factories.EventWithOpeningHoursStockFactory.create(
        offer=offer,
        isSoftDeleted=isSoftDeleted,
        eventOpeningHours__startDatetime=startDatetime,
        eventOpeningHours__endDatetime=endDatetime,
        eventOpeningHours__isSoftDeleted=isSoftDeleted,
    )


def create_offerer_with_event_with_opening_hours() -> None:
    # FESTIVAL
    offerer = offerers_factories.OffererFactory.create(name="Festival du Midi")
    user = users_factories.ProFactory.create(
        email="festival@midi.fr",
        firstName="Pro",
        lastName="Api",
        phoneNumber="+33100000000",
    )
    offerers_factories.UserOffererFactory.create(offerer=offerer, user=user)
    festival_venue = offerers_factories.VenueFactory.create(
        name="La guinguette du camping", managingOfferer=offerer, venueTypeCode=VenueTypeCode.FESTIVAL
    )

    # Create festival in the future
    _create_event_with_opening_hours(
        startDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=7),
        endDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=10),
        subcategoryId=subcategories.FESTIVAL_MUSIQUE.id,
        venue=festival_venue,
    )

    # MUSEUM
    offerer = offerers_factories.OffererFactory.create(name="Ville Chalon-sur-Saône")
    user = users_factories.ProFactory.create(
        email="contact@museeniepce.com",
        firstName="Pro",
        lastName="Api",
        phoneNumber="+33100000000",
    )
    offerers_factories.UserOffererFactory.create(offerer=offerer, user=user)
    museum_venue = offerers_factories.VenueFactory.create(
        name="Musée Nicéphore Niépce", managingOfferer=offerer, venueTypeCode=VenueTypeCode.MUSEUM
    )

    # Permanent event
    _create_event_with_opening_hours(
        startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        endDatetime=None,
        subcategoryId=subcategories.VISITE.id,
        venue=museum_venue,
    )

    logger.info("create_offerer_with_event_with_opening_hours")
