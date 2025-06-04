import datetime

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import offer as collective_offer_api
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import api
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="venues_with_same_pricing_point")
def venues_with_same_pricing_point_fixture():
    venue = offerers_factories.VenueFactory()
    destination_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
    pricing_point_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer, name="current")

    offerers_factories.VenuePricingPointLinkFactory(
        venue=destination_venue,
        pricingPoint=pricing_point_venue,
        timespan=[datetime.datetime.utcnow() - datetime.timedelta(days=1), None],
    )
    offerers_factories.VenuePricingPointLinkFactory(
        venue=venue,
        pricingPoint=pricing_point_venue,
        timespan=[datetime.datetime.utcnow() - datetime.timedelta(days=1), None],
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
    if state == educational_models.CollectiveBookingStatus.REIMBURSED:
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_stock = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        educational_factories.ReimbursedCollectiveBookingFactory(collectiveStock=collective_stock)
    if state == educational_models.CollectiveBookingStatus.CANCELLED:
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_stock = educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer)
        educational_factories.CancelledCollectiveBookingFactory(collectiveStock=collective_stock)
    return collective_offer


@pytest.mark.features(VENUE_REGULARIZATION=True)
class MoveCollectiveOfferSuccessTest:
    def test_move_collective_offer_with_its_own_OA(self):
        """
        Ensure the collective offer with its own OA keeps it once moved.
        """
        collective_offer = educational_factories.CollectiveOfferOnOtherAddressLocationFactory()
        destination_venue = offerers_factories.VenueFactory(managingOfferer=collective_offer.venue.managingOfferer)
        source_venue = collective_offer.venue
        assert collective_offer.offererAddress != source_venue.offererAddress
        offer_OA_id = collective_offer.offererAddressId

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.offererAddressId == offer_OA_id

    def test_move_collective_offer_with_venue_OA_gets_a_new_OA(self):
        """
        Ensure the collective offer using the venue's OA get a new OA once moved if that OA did not exist before.
        """
        collective_offer = educational_factories.CollectiveOfferOnAddressVenueLocationFactory()
        destination_venue = offerers_factories.VenueFactory(managingOfferer=collective_offer.venue.managingOfferer)
        source_venue = collective_offer.venue
        assert collective_offer.offererAddress == source_venue.offererAddress

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        # Same address, different OA, label is venue's common name
        assert collective_offer.offererAddress != source_venue.offererAddress
        assert collective_offer.offererAddress.addressId == source_venue.offererAddress.addressId
        assert collective_offer.offererAddress.label == source_venue.common_name

    def test_move_collective_offer_with_venue_OA_can_resuse_non_venue_OA(self):
        """
        Ensure the collective offer using the venue's OA can fit in an existing OA once moved.
        """
        collective_offer = educational_factories.CollectiveOfferOnAddressVenueLocationFactory()
        destination_venue = offerers_factories.VenueFactory(managingOfferer=collective_offer.venue.managingOfferer)
        source_venue = collective_offer.venue
        destination_OA = offerers_factories.OffererAddressFactory(
            offerer=source_venue.managingOfferer,
            label=source_venue.common_name,
            address=source_venue.offererAddress.address,
        )
        assert collective_offer.offererAddress == source_venue.offererAddress
        assert destination_OA != collective_offer.offererAddress

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.offererAddress == destination_OA

    def test_move_collective_offer_without_pricing_points(self):
        """
        A collective offer on a venue without pricing point can only be moved to another venue without pricing point
        """
        collective_offer = educational_factories.CollectiveOfferFactory()
        destination_venue = offerers_factories.VenueFactory(managingOfferer=collective_offer.venue.managingOfferer)
        assert collective_offer.venue.current_pricing_point_link is None
        assert destination_venue.current_pricing_point_link is None

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.venue == destination_venue

    def test_move_collective_offer_with_inactive_pricing_points(self):
        """
        A collective offer on a venue without pricing point can only be moved to another venue without pricing point
        """
        collective_offer = educational_factories.CollectiveOfferFactory()
        destination_venue = offerers_factories.VenueFactory(managingOfferer=collective_offer.venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(
            venue=destination_venue,
            pricingPoint=destination_venue,
            timespan=[
                datetime.datetime.utcnow() - datetime.timedelta(days=3),
                datetime.datetime.utcnow() - datetime.timedelta(days=1),
            ],
        )
        assert collective_offer.venue.current_pricing_point_link is None
        assert destination_venue.current_pricing_point_link is None

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.venue == destination_venue

    def test_move_collective_offer_with_same_pricing_points_without_bookings(self, venues_with_same_pricing_point):
        """
        A collective offer on a venue with a pricing point can be moved to another venue with the same pricing point
        """
        venue, destination_venue = venues_with_same_pricing_point
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.venue == destination_venue

    def test_move_collective_offer_with_past_stocks(self, venues_with_same_pricing_point):
        venue, destination_venue = venues_with_same_pricing_point
        yesterday = datetime.date.today() - datetime.timedelta(days=1)

        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        educational_factories.CollectiveStockFactory(collectiveOffer=collective_offer, startDatetime=yesterday)

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.venue == destination_venue

    def test_move_collective_offer_with_unused_bookings_without_reimbursment(self, venues_with_same_pricing_point):
        venue, destination_venue = venues_with_same_pricing_point
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer=collective_offer, status=CollectiveBookingStatus.CONFIRMED
        )

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        db.session.refresh(collective_booking)
        assert collective_offer.venue == destination_venue
        assert collective_booking.venue == destination_venue

    def test_move_collective_offer_with_used_bookings(self, venues_with_same_pricing_point):
        """
        A finance event is created when a collectiveBooking is used.
        Reimbursement does not create new finance event, only create CashFlow and Invoices.
        Link to venues is through BankAccount.
        Because an offer can only be moved to a venue with the same bank account, it should not be a problem.
        FinanceEvent venue does not change to keep track of past actions (like pricing date).
        """
        venue, destination_venue = venues_with_same_pricing_point
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer=collective_offer
        )
        finance_event = finance_api.add_event(
            finance_models.FinanceEventMotive.BOOKING_USED, booking=collective_booking
        )
        assert finance_event.venue == venue

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        db.session.refresh(collective_booking)
        db.session.refresh(finance_event)
        assert collective_offer.venue == destination_venue
        assert collective_booking.venue == destination_venue
        assert finance_event.venue == venue

    def test_move_collective_offer_with_booking_with_pricing_with_different_pricing_point(
        self, venues_with_same_pricing_point
    ):
        """Moving an offer from a venue with a pricing point A
        and a booking with a pricing with a different pricing point B
        to another venue with the same pricing point A should work."""
        venue, destination_venue = venues_with_same_pricing_point
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer=collective_offer
        )
        finance_event = finance_api.add_event(
            finance_models.FinanceEventMotive.BOOKING_USED, booking=collective_booking
        )
        finance_factories.PricingFactory(
            pricingPoint=offerers_factories.VenueFactory(managingOfferer=destination_venue.managingOfferer),
            collectiveBooking=collective_booking,
            event=finance_event,
        )

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        db.session.refresh(collective_booking)
        assert collective_offer.venue == destination_venue
        assert collective_booking.venue == destination_venue

    def test_move_collective_offer_without_bank_account(self, venues_with_same_pricing_point):
        """
        A collective offer on a venue without bank account can be moved to another venue without bank account
        """
        venue, destination_venue = venues_with_same_pricing_point
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer=collective_offer
        )

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        assert collective_offer.venue == destination_venue
        assert collective_booking.venue == destination_venue

    def test_move_collective_offer_without_bank_account_to_venue_with_bank_account(
        self, venues_with_same_pricing_point
    ):
        """
        A collective offer on a venue without bank account can be moved to another venue with the bank account
        """
        now = datetime.datetime.utcnow()
        venue, destination_venue = venues_with_same_pricing_point
        bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=destination_venue,
            bankAccount=bank_account,
            timespan=[now - datetime.timedelta(days=30), now - datetime.timedelta(days=3)],
        )
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer=collective_offer
        )

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        assert collective_offer.venue == destination_venue
        assert collective_booking.venue == destination_venue

    def test_move_collective_offer_with_bank_account(self, venues_with_same_pricing_point):
        """
        A collective offer on a venue with a bank account can be moved to another venue with the same bank account
        """
        now = datetime.datetime.utcnow()
        venue, destination_venue = venues_with_same_pricing_point
        bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue,
            bankAccount=bank_account,
            timespan=[now - datetime.timedelta(days=30), now - datetime.timedelta(days=3)],
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=destination_venue,
            bankAccount=bank_account,
            timespan=[now - datetime.timedelta(days=30), now - datetime.timedelta(days=3)],
        )
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        collective_booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer=collective_offer
        )

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        assert collective_offer.venue == destination_venue
        assert collective_booking.venue == destination_venue

    @pytest.mark.parametrize(
        "state",
        set(educational_models.CollectiveOfferDisplayedStatus),
    )
    def test_move_collective_offer_with_different_statuses(self, state):
        venue = offerers_factories.VenueFactory()
        destination_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        collective_offer = educational_factories.create_collective_offer_by_status(state, venue=venue)

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.venue == destination_venue

    @pytest.mark.parametrize(
        "state",
        [
            educational_models.CollectiveBookingStatus.PENDING,
            educational_models.CollectiveBookingStatus.CONFIRMED,
            educational_models.CollectiveBookingStatus.USED,
            educational_models.CollectiveBookingStatus.REIMBURSED,
            educational_models.CollectiveBookingStatus.CANCELLED,
        ],
    )
    def test_move_collective_offer_with_different_booking_statuses(self, state):
        venue = offerers_factories.VenueFactory()
        destination_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        collective_offer = create_offer_by_booking_state(venue, state)

        collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.venue == destination_venue
        assert db.session.query(educational_models.CollectiveBooking).count() == 1
        assert db.session.query(educational_models.CollectiveBooking).all()[0].venue == destination_venue


@pytest.mark.features(VENUE_REGULARIZATION=True)
class MoveCollectiveOfferFailTest:
    def test_move_collective_offer_without_pricing_point_to_venue_with_pricing_point(self):
        """
        A collective offer on a venue without pricing point cannot be moved to another venue with pricing point
        """
        collective_offer = educational_factories.CollectiveOfferFactory()
        destination_venue = offerers_factories.VenueFactory(managingOfferer=collective_offer.venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(
            venue=destination_venue,
            pricingPoint=destination_venue,
            timespan=[datetime.datetime.utcnow() - datetime.timedelta(days=1), None],
        )
        assert collective_offer.venue.current_pricing_point_link is None
        assert destination_venue.current_pricing_point_link is not None

        with pytest.raises(api.exceptions.NoDestinationVenue):
            collective_offer_api.move_collective_offer_for_regularization(collective_offer, destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.venue != destination_venue

    def test_move_collective_offer_with_different_pricing_point(self):
        venue = offerers_factories.VenueFactory()
        invalid_destination_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        pricing_point_venue_1 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer, name="current")
        pricing_point_venue_2 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer, name="current")

        offerers_factories.VenuePricingPointLinkFactory(
            venue=invalid_destination_venue,
            pricingPoint=pricing_point_venue_1,
            timespan=[datetime.datetime.utcnow() - datetime.timedelta(days=1), None],
        )
        offerers_factories.VenuePricingPointLinkFactory(
            venue=venue,
            pricingPoint=pricing_point_venue_2,
            timespan=[datetime.datetime.utcnow() - datetime.timedelta(days=1), None],
        )
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        with pytest.raises(api.exceptions.NoDestinationVenue):
            collective_offer_api.move_collective_offer_for_regularization(collective_offer, invalid_destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.venue != invalid_destination_venue

    def test_move_collective_offer_with_pricing_point_to_venue_without_pricing_point(self):
        venue = offerers_factories.VenueFactory()
        invalid_destination_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        pricing_point_venue_1 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer, name="current")

        offerers_factories.VenuePricingPointLinkFactory(
            venue=venue,
            pricingPoint=pricing_point_venue_1,
            timespan=[datetime.datetime.utcnow() - datetime.timedelta(days=1), None],
        )
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        with pytest.raises(api.exceptions.NoDestinationVenue):
            collective_offer_api.move_collective_offer_for_regularization(collective_offer, invalid_destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.venue != invalid_destination_venue

    def test_move_collective_offer_with_different_banking_account(self, venues_with_same_pricing_point):
        now = datetime.datetime.utcnow()
        venue, invalid_destination_venue = venues_with_same_pricing_point
        bank_account_1 = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        bank_account_2 = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue,
            bankAccount=bank_account_1,
            timespan=[now - datetime.timedelta(days=30), now + datetime.timedelta(days=3)],
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=invalid_destination_venue,
            bankAccount=bank_account_2,
            timespan=[now - datetime.timedelta(days=30), now + datetime.timedelta(days=3)],
        )
        collective_offer = educational_factories.CollectiveOfferFactory(venue=venue)
        with pytest.raises(api.exceptions.NoDestinationVenue):
            collective_offer_api.move_collective_offer_for_regularization(collective_offer, invalid_destination_venue)

        db.session.refresh(collective_offer)
        assert collective_offer.venue != invalid_destination_venue
