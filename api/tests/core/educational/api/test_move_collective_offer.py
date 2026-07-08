import datetime

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="venues_with_same_pricing_point")
def venues_with_same_pricing_point_fixture():
    venue = offerers_factories.VenueFactory()
    destination_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
    pricing_point_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer, name="current")

    offerers_factories.VenuePricingPointLinkFactory(
        venue=destination_venue,
        pricingPoint=pricing_point_venue,
        timespan=[date_utils.get_naive_utc_now() - datetime.timedelta(days=1), None],
    )
    offerers_factories.VenuePricingPointLinkFactory(
        venue=venue,
        pricingPoint=pricing_point_venue,
        timespan=[date_utils.get_naive_utc_now() - datetime.timedelta(days=1), None],
    )
    return venue, destination_venue


def create_offer_by_booking_state(venue, state):
    collective_offer = None
    if state == educational_models.CollectiveBookingStatus.PENDING:
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_stock = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        educational_factories.CollectiveBookingFactory(collectiveStock=collective_stock)
    if state == educational_models.CollectiveBookingStatus.CONFIRMED:
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_stock = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        educational_factories.CollectiveBookingFactory(collectiveStock=collective_stock)
    if state == educational_models.CollectiveBookingStatus.USED:
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_stock = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        educational_factories.UsedCollectiveBookingFactory(collectiveStock=collective_stock)
    if state == educational_models.CollectiveBookingStatus.PENDING_REIMBURSEMENT:
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_stock = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        educational_factories.PendingReimbursementCollectiveBookingFactory(collectiveStock=collective_stock)
    if state == educational_models.CollectiveBookingStatus.REIMBURSED:
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_stock = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        educational_factories.ReimbursedCollectiveBookingFactory(collectiveStock=collective_stock)
    if state == educational_models.CollectiveBookingStatus.CANCELLED:
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_stock = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        educational_factories.CancelledCollectiveBookingFactory(collectiveStock=collective_stock)
    return collective_offer
