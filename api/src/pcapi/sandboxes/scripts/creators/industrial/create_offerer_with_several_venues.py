import logging

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories


logger = logging.getLogger(__name__)


def create_offerer_with_several_venues() -> None:
    user_offerer = offerers_factories.UserOffererFactory(offerer__name="Structure avec plusieurs lieux")
    venue1 = offerers_factories.VenueFactory(
        name="Lieu 1 de la structure avec plusieurs lieux",
        managingOfferer=user_offerer.offerer,
        pricing_point="self",
        reimbursement_point="self",
    )
    venue2 = offerers_factories.VenueFactory(
        name="Lieu 2 de la structure avec plusieurs lieux",
        managingOfferer=user_offerer.offerer,
        pricing_point="self",
        reimbursement_point="self",
    )
    offerers_factories.VenueFactory(
        name="Lieu 3 de la structure avec plusieurs lieux",
        managingOfferer=user_offerer.offerer,
        pricing_point="self",
        reimbursement_point=venue1,
    )
    offerers_factories.VenueWithoutSiretFactory(
        name="Lieu 4 sans SIRET de la structure avec plusieurs lieux",
        managingOfferer=user_offerer.offerer,
        pricing_point=venue1,
        reimbursement_point=venue1,
    )
    # offerers have always a virtual venue so we have to create one to match reality
    offerers_factories.VirtualVenueFactory(
        name="Lieu virtuel de la structure avec plusieurs lieux ", managingOfferer=user_offerer.offerer
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
