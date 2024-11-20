from datetime import datetime
from datetime import timedelta
import logging

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import CollectiveBookingStatus
import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer


logger = logging.getLogger(__name__)


def create_industrial_bookings_for_statistics() -> None:
    logger.info("create_industrial_bookings_for_statistics")
    _create_booking_for_statistics_offerer_multiple_venues()
    _create_booking_for_statistics_offerer_one_venues()
    _create_booking_for_statistics_individual_only()
    _create_booking_for_statistics_collective_only()
    _create_booking_for_statistics_no_offer_no_revenue()
    _create_booking_for_statistics_with_offer_no_revenue()
    logger.info("created bookings for statistics")


def _create_booking_for_statistics_offerer_multiple_venues() -> None:
    offerer_multi_venues = offerers_factories.OffererFactory(name="Stats - plusieurs lieux - CA et CA prévisionnel")
    offerers_factories.UserOffererFactory(offerer=offerer_multi_venues, user__email="retention_structures@example.com")
    offers = []
    for index in range(1, 4):

        offerer_multi_venues_venue = offerers_factories.VenueFactory(
            name=f"Lieu CA et CA prévisionnel {index}",
            pricing_point="self",
            managingOfferer=offerer_multi_venues,
            venueTypeCode=offerers_models.VenueTypeCode.DISTRIBUTION_STORE,
        )

        individual_offer = offers_factories.OfferFactory(venue=offerer_multi_venues_venue, isActive=True)
        offers_factories.StockFactory(offer=individual_offer)
        offers.append(individual_offer)

        collective_offer = educational_factories.CollectiveOfferFactory(venue=offerer_multi_venues_venue)
        educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        offers.append(collective_offer)

    _create_bookings(offers)
    logger.info("created bookings for statistics for offerer with multiple venues")


def _create_booking_for_statistics_offerer_one_venues() -> None:
    offerer_one_venue = offerers_factories.OffererFactory(name="Stats - un seul lieu - CA et CA prévisionnel")
    offerers_factories.UserOffererFactory(offerer=offerer_one_venue, user__email="retention_structures@example.com")
    venue = offerers_factories.VenueFactory(
        name="Lieu CA et CA prévisionnel",
        pricing_point="self",
        managingOfferer=offerer_one_venue,
        venueTypeCode=offerers_models.VenueTypeCode.DISTRIBUTION_STORE,
    )

    individual_offer = offers_factories.OfferFactory(venue=venue, isActive=True)
    offers_factories.StockFactory(offer=individual_offer)

    collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
    educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)

    _create_bookings([individual_offer, collective_offer])

    logger.info("created bookings for statistics for offerer with one venue")


def _create_booking_for_statistics_individual_only() -> None:
    offerer_individual_only = offerers_factories.OffererFactory(
        name="Stats - un seul lieu - individuel seulement - CA et CA prévisionnel"
    )
    offerers_factories.UserOffererFactory(
        offerer=offerer_individual_only, user__email="retention_structures@example.com"
    )
    venue = offerers_factories.VenueFactory(
        name="Lieu CA et CA prévisionnel individuel",
        pricing_point="self",
        managingOfferer=offerer_individual_only,
        venueTypeCode=offerers_models.VenueTypeCode.DISTRIBUTION_STORE,
    )

    individual_offer = offers_factories.OfferFactory(venue=venue, isActive=True)
    offers_factories.StockFactory(offer=individual_offer)

    _create_bookings([individual_offer])

    logger.info("created bookings for statistics for offerer individual only")


def _create_booking_for_statistics_collective_only() -> None:
    offerer_collective_only = offerers_factories.OffererFactory(
        name="Stats - un seul lieu - collectif seulement - CA et CA prévisionnel"
    )
    offerers_factories.UserOffererFactory(
        offerer=offerer_collective_only, user__email="retention_structures@example.com"
    )
    venue = offerers_factories.VenueFactory(
        name="Lieu CA et CA prévisionnel collectif",
        pricing_point="self",
        managingOfferer=offerer_collective_only,
        venueTypeCode=offerers_models.VenueTypeCode.DISTRIBUTION_STORE,
    )

    collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
    educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)

    _create_bookings([collective_offer])

    logger.info("created bookings for statistics for offerer collective only")


def _create_booking_for_statistics_no_offer_no_revenue() -> None:
    offerer_no_offer_no_revenue = offerers_factories.OffererFactory(name="Stats - aucune offre, aucun CA")
    offerers_factories.UserOffererFactory(
        offerer=offerer_no_offer_no_revenue, user__email="retention_structures@example.com"
    )
    offerers_factories.VenueFactory(
        name="Lieu aucune offre - aucun CA",
        pricing_point="self",
        managingOfferer=offerer_no_offer_no_revenue,
        venueTypeCode=offerers_models.VenueTypeCode.DISTRIBUTION_STORE,
    )
    logger.info("created bookings for statistics for offerer no offer and no revenue")


def _create_booking_for_statistics_with_offer_no_revenue() -> None:
    offerer_offers_no_booking = offerers_factories.OffererFactory(name="Stats - offres, aucun CA")
    offerers_factories.UserOffererFactory(
        offerer=offerer_offers_no_booking, user__email="retention_structures@example.com"
    )
    venue = offerers_factories.VenueFactory(
        name="Lieu avec offre - aucun CA",
        pricing_point="self",
        managingOfferer=offerer_offers_no_booking,
        venueTypeCode=offerers_models.VenueTypeCode.DISTRIBUTION_STORE,
    )

    individual_offer = offers_factories.OfferFactory(venue=venue, isActive=True)
    offers_factories.StockFactory(offer=individual_offer)

    collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
    educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)

    logger.info("created bookings for statistics for offerer with offers but no revenue")


def _create_bookings(offers: list[Offer]) -> None:
    january_first = datetime.utcnow().replace(month=1, day=1)
    for offer in offers:
        dates_used = [january_first, january_first - timedelta(days=500), january_first - timedelta(days=800)]
        # Current year in the past, 2 years ago, 3 years ago
        if isinstance(offer, Offer):
            for date_used in dates_used:
                booking = _create_booking_for_individual_offer(offer, date_used, BookingStatus.USED)
                finance_factories.UsedBookingFinanceEventFactory(booking=booking)
        else:
            for date_used in dates_used:
                booking = _create_booking_for_collective_offer(offer, date_used, CollectiveBookingStatus.USED)
                finance_factories.UsedCollectiveBookingFinanceEventFactory(collectiveBooking=booking)

        # Current year in the future, next year
        dates_programmed = [
            datetime.utcnow().replace(month=12, day=31),
            datetime.utcnow().replace(month=12, day=31) + timedelta(days=20),
        ]
        if isinstance(offer, Offer):
            for date_programmed in dates_programmed:
                booking = _create_booking_for_individual_offer(offer, date_programmed, BookingStatus.CONFIRMED)
        else:
            for date_programmed in dates_programmed:
                booking = _create_booking_for_collective_offer(
                    offer, date_programmed, CollectiveBookingStatus.CONFIRMED
                )


def _create_booking_for_individual_offer(
    offer: offers_factories.OfferFactory, booking_date: datetime, status: BookingStatus
) -> offers_factories.OfferFactory:
    return BookingFactory(
        status=status,
        stock=offer.stocks[0],
        dateUsed=booking_date,
        amount=offer.stocks[0].price,
        offerer=offer.venue.managingOfferer,
    )


def _create_booking_for_collective_offer(
    offer: educational_factories.CollectiveOfferFactory, booking_date: datetime, status: CollectiveBookingStatus
) -> educational_factories.CollectiveBookingFactory:
    if status == CollectiveBookingStatus.USED:
        return educational_factories.UsedCollectiveBookingFactory(
            collectiveStock=offer.collectiveStock, dateUsed=booking_date
        )
    return educational_factories.CollectiveBookingFactory(collectiveStock=offer.collectiveStock, status=status)
