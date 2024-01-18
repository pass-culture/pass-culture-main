import datetime
import logging

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories


logger = logging.getLogger(__name__)


def create_offerer_with_several_venues() -> offerers_models.Offerer:
    user_offerer = offerers_factories.UserOffererFactory(offerer__name="Structure avec plusieurs lieux")
    venue1 = offerers_factories.VenueFactory(
        name="Compagnie de théâtre",
        managingOfferer=user_offerer.offerer,
        pricing_point="self",
        reimbursement_point="self",
        venueTypeCode=offerers_models.VenueTypeCode.PERFORMING_ARTS,
    )
    venue2 = offerers_factories.VenueFactory(
        name="Musée",
        managingOfferer=user_offerer.offerer,
        pricing_point="self",
        reimbursement_point="self",
        venueTypeCode=offerers_models.VenueTypeCode.MUSEUM,
    )
    offerers_factories.VenueFactory(
        name="Festival de musique",
        managingOfferer=user_offerer.offerer,
        pricing_point="self",
        reimbursement_point=venue1,
        venueTypeCode=offerers_models.VenueTypeCode.FESTIVAL,
    )
    offerers_factories.VenueWithoutSiretFactory(
        name="Bibliothèque sans SIRET",
        managingOfferer=user_offerer.offerer,
        pricing_point=venue1,
        reimbursement_point=venue1,
        venueTypeCode=offerers_models.VenueTypeCode.LIBRARY,
    )
    # offerers have always a virtual venue so we have to create one to match reality
    virtual_venue = offerers_factories.VirtualVenueFactory(
        name="Lieu virtuel de la structure avec plusieurs lieux ", managingOfferer=user_offerer.offerer
    )
    in_two_month = datetime.datetime.utcnow() + datetime.timedelta(days=60)
    for i in range(1, 6):
        offer = offers_factories.DigitalOfferFactory(name=f"Offre avec code d'activation {i}", venue=virtual_venue)

        offers_factories.StockWithActivationCodesFactory(
            offer=offer,
            activationCodes__expirationDate=in_two_month,
        )

    for i, venue in enumerate([venue1, venue2], 1):
        offers_factories.EventStockFactory(
            offer__name=f"Évènement 1 du lieu {i} - sans réservation", offer__venue=venue
        )

        event2 = offers_factories.EventStockFactory(
            offer__name=f"Évènement 2 du lieu {i} - 3 réservations confirmées", offer__venue=venue
        )
        booking_factories.BookingFactory.create_batch(3, stock=event2)

        event3 = offers_factories.EventStockFactory(
            offer__name=f"Évènement 3 du lieu {i} - 2 réservations dont 1 annulée", offer__venue=venue
        )
        booking_factories.BookingFactory(stock=event3)
        booking_factories.CancelledBookingFactory(stock=event3)

        event4 = offers_factories.EventStockFactory(
            offer__name=f"Évènement 4 du lieu {i} - réservations validées", offer__venue=venue
        )
        booking_factories.UsedBookingFactory.create_batch(2, stock=event4)

        event5 = offers_factories.EventStockFactory(
            offer__name=f"Évènement 5 du lieu {i} - réservations remboursées", offer__venue=venue
        )
        booking_factories.ReimbursedBookingFactory.create_batch(2, stock=event5)

    logger.info("create_offerer_with_several_venues")

    return user_offerer.offerer
