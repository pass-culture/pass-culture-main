import datetime

import pytest
import time_machine

from pcapi.core.educational import exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import testing as educational_testing
from pcapi.core.educational.api import stock as educational_api_stock
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.serialization import collective_stock_serialize


STATUSES_ALLOWING_EDIT_DATES = (
    CollectiveOfferDisplayedStatus.DRAFT,
    CollectiveOfferDisplayedStatus.ACTIVE,
    CollectiveOfferDisplayedStatus.PREBOOKED,
    CollectiveOfferDisplayedStatus.EXPIRED,
)

STATUSES_NOT_ALLOWING_EDIT_DATES = tuple(
    set(CollectiveOfferDisplayedStatus) - {*STATUSES_ALLOWING_EDIT_DATES, CollectiveOfferDisplayedStatus.INACTIVE}
)

STATUSES_ALLOWING_EDIT_DISCOUNT = (
    CollectiveOfferDisplayedStatus.DRAFT,
    CollectiveOfferDisplayedStatus.ACTIVE,
    CollectiveOfferDisplayedStatus.PREBOOKED,
    CollectiveOfferDisplayedStatus.BOOKED,
)

STATUSES_NOT_ALLOWING_EDIT_DISCOUNT = tuple(
    set(CollectiveOfferDisplayedStatus) - {*STATUSES_ALLOWING_EDIT_DISCOUNT, CollectiveOfferDisplayedStatus.INACTIVE}
)


@pytest.mark.usefixtures("db_session")
class EditCollectiveOfferStocksTest:
    def test_should_update_all_fields_when_all_changed(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        educational_factories.EducationalYearFactory(
            beginningDate=initial_event_date - datetime.timedelta(days=100),
            expirationDate=initial_event_date + datetime.timedelta(days=100),
        )

        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=5),
            bookingLimitDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=5, hours=16),
            totalPrice=1500,
            numberOfTickets=35,
        )

        # When
        educational_api_stock.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.startDatetime == new_stock_data.startDatetime.replace(tzinfo=None)
        assert stock.bookingLimitDatetime == new_stock_data.bookingLimitDatetime.replace(tzinfo=None)
        assert stock.price == 1500
        assert stock.numberOfTickets == 35

    def test_should_update_some_fields_and_keep_non_edited_ones(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        educational_factories.EducationalYearFactory(
            beginningDate=initial_event_date - datetime.timedelta(days=100),
            expirationDate=initial_event_date + datetime.timedelta(days=100),
        )
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=5),
            numberOfTickets=35,
        )

        # When
        educational_api_stock.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.startDatetime == new_stock_data.startDatetime.replace(tzinfo=None)
        assert stock.bookingLimitDatetime == initial_booking_limit_date
        assert stock.price == 1200
        assert stock.numberOfTickets == 35

    def test_should_replace_bookingLimitDatetime_with_new_event_datetime_if_provided_but_none(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        educational_factories.EducationalYearFactory(
            beginningDate=initial_event_date - datetime.timedelta(days=100),
            expirationDate=initial_event_date + datetime.timedelta(days=100),
        )
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_event_datetime = datetime.datetime.now(  # pylint: disable=datetime-now
            datetime.timezone.utc
        ) + datetime.timedelta(days=7, hours=5)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=new_event_datetime,
            bookingLimitDatetime=None,
        )

        # When
        educational_api_stock.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == new_event_datetime.replace(tzinfo=None)

    def test_should_replace_bookingLimitDatetime_with_old_event_datetime_if_provided_but_none_and_event_date_unchanged(
        self,
    ) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        educational_factories.EducationalYearFactory(
            beginningDate=initial_event_date - datetime.timedelta(days=100),
            expirationDate=initial_event_date + datetime.timedelta(days=100),
        )
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            bookingLimitDatetime=None,
        )

        # When
        educational_api_stock.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == initial_event_date

    # FIXME (rpaoloni, 2022-03-09) -> None: Uncomment for when pc-13428 is merged
    # @mock.patch("pcapi.core.search.async_index_offer_ids")
    # def test_should_reindex_offer_on_algolia(self, mocked_async_index_offer_ids) -> None:
    #     # Given
    #     initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
    #     initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
    #     stock_to_be_updated = educational_factories.CollectiveStockFactory(
    #         beginningDatetime=initial_event_date,
    #         price=1200,
    #         numberOfTickets=30,
    #         bookingLimitDatetime=initial_booking_limit_date,
    #     )
    #     new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
    #         beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=7, hours=5),
    #         numberOfTickets=35,
    #     )

    #     # When
    #     edit_collective_stock(
    #         stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
    #     )

    #     # Then
    #     stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
    #     mocked_async_index_offer_ids.assert_called_once_with([stock.collectiveOfferId])

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def test_should_not_allow_stock_edition_when_booking_status_is_REIMBURSED_or_USED(self) -> None:
        # Given
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime.utcnow() - datetime.timedelta(days=100),
            expirationDate=datetime.datetime.utcnow() + datetime.timedelta(days=100),
        )
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            price=1500,
            startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=2),
        )
        educational_factories.CollectiveBookingFactory(
            confirmationLimitDate=datetime.datetime.utcnow() + datetime.timedelta(days=3),
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.REIMBURSED,
        )

        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            totalPrice=1200,
        )

        # When
        with pytest.raises(exceptions.CollectiveOfferStockBookedAndBookingNotPending):
            educational_api_stock.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).first()
        assert stock.price == 1500

    @time_machine.travel("2020-11-17 15:00:00")
    def should_update_bookings_cancellation_limit_date_if_event_postponed(self) -> None:
        # Given
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2021, 9, 1), expirationDate=datetime.datetime(2022, 8, 31)
        )
        initial_event_date = datetime.datetime(2021, 12, 7, 15)
        cancellation_limit_date = datetime.datetime(2021, 11, 22, 15)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(startDatetime=initial_event_date)
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.PENDING,
            cancellationLimitDate=cancellation_limit_date,
            confirmationLimitDate=datetime.datetime(2021, 12, 17, 15),
            educationalYear=educational_year,
        )

        data = {"startDatetime": datetime.datetime(2021, 12, 12, 20)}

        # When
        educational_api_stock.edit_collective_stock(stock=stock_to_be_updated, stock_data=data)

        # Then
        booking_updated = CollectiveBooking.query.filter_by(id=booking.id).one()
        assert booking_updated.cancellationLimitDate == datetime.datetime(2021, 11, 12, 20)

    @time_machine.travel("2020-11-17 15:00:00", tick=False)
    def should_update_bookings_cancellation_limit_date_if_startDatetime_earlier(self) -> None:
        # Given
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=20)
        cancellation_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(startDatetime=initial_event_date)
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.PENDING,
            cancellationLimitDate=cancellation_limit_date,
            confirmationLimitDate=datetime.datetime.utcnow() + datetime.timedelta(days=30),
            educationalYear=educational_year,
        )

        new_event_date = datetime.datetime.now(  # pylint: disable=datetime-now
            datetime.timezone.utc
        ) + datetime.timedelta(days=5, hours=5)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=new_event_date,
            bookingLimitDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=3, hours=5),
        )

        # When
        educational_api_stock.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        booking_updated = CollectiveBooking.query.filter_by(id=booking.id).one()
        assert booking_updated.cancellationLimitDate == datetime.datetime.utcnow()

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_allow_stock_edition_and_not_modify_cancellation_limit_date_when_booking_cancelled(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=20)
        educational_factories.EducationalYearFactory(
            beginningDate=initial_event_date - datetime.timedelta(days=100),
            expirationDate=initial_event_date + datetime.timedelta(days=100),
        )

        cancellation_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.CANCELLED,
            cancellationLimitDate=cancellation_limit_date,
            confirmationLimitDate=datetime.datetime.utcnow() + datetime.timedelta(days=30),
        )

        new_event_date = datetime.datetime.now(  # pylint: disable=datetime-now
            datetime.timezone.utc
        ) + datetime.timedelta(days=25, hours=5)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=new_event_date,
        )

        # When
        educational_api_stock.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        booking = CollectiveBooking.query.filter_by(id=booking.id).one()
        assert booking.cancellationLimitDate == cancellation_limit_date
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.startDatetime == new_event_date.replace(tzinfo=None)

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_should_update_expired_booking(self) -> None:
        now = datetime.datetime.utcnow()
        limit = now - datetime.timedelta(days=2)
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=now + datetime.timedelta(days=5), bookingLimitDatetime=limit
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock,
            status=CollectiveBookingStatus.CANCELLED,
            cancellationReason=CollectiveBookingCancellationReasons.EXPIRED,
            cancellationDate=now - datetime.timedelta(days=1),
            confirmationLimitDate=limit,
        )

        new_limit = now + datetime.timedelta(days=1)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(bookingLimitDatetime=new_limit)
        educational_api_stock.edit_collective_stock(stock=stock, stock_data=new_stock_data.dict(exclude_unset=True))

        assert stock.bookingLimitDatetime == new_limit
        assert booking.status == CollectiveBookingStatus.PENDING
        assert booking.cancellationReason == None
        assert booking.cancellationDate == None
        assert booking.confirmationLimitDate == new_limit

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def test_should_not_update_expired_booking(self) -> None:
        now = datetime.datetime.utcnow()
        limit = now - datetime.timedelta(days=2)
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=now + datetime.timedelta(days=5), bookingLimitDatetime=limit
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock,
            status=CollectiveBookingStatus.CANCELLED,
            cancellationReason=CollectiveBookingCancellationReasons.EXPIRED,
            cancellationDate=now - datetime.timedelta(days=1),
            confirmationLimitDate=limit,
        )

        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            bookingLimitDatetime=now + datetime.timedelta(days=1)
        )
        educational_api_stock.edit_collective_stock(stock=stock, stock_data=new_stock_data.dict(exclude_unset=True))

        assert stock.bookingLimitDatetime == now + datetime.timedelta(days=1)
        assert booking.status == CollectiveBookingStatus.CANCELLED
        assert booking.cancellationReason == CollectiveBookingCancellationReasons.EXPIRED
        assert booking.cancellationDate == now - datetime.timedelta(days=1)
        assert booking.confirmationLimitDate == limit

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", educational_testing.STATUSES_ALLOWING_EDIT_DETAILS)
    def test_can_increase_price(self, status):
        offer = educational_factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        price = offer.collectiveStock.price
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(totalPrice=price + 100)

        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        assert offer.collectiveStock.price == price + 100

    @time_machine.travel("2020-11-17 15:00:00", tick=False)
    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", STATUSES_ALLOWING_EDIT_DATES)
    def test_can_edit_dates(self, status):
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        offer = educational_factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        new_limit = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10)
        new_start = new_limit + datetime.timedelta(days=5)
        new_end = new_limit + datetime.timedelta(days=7)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            bookingLimitDatetime=new_limit, startDatetime=new_start, endDatetime=new_end
        )
        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        assert offer.collectiveStock.bookingLimitDatetime == new_limit.replace(tzinfo=None)
        assert offer.collectiveStock.startDatetime == new_start.replace(tzinfo=None)
        assert offer.collectiveStock.endDatetime == new_end.replace(tzinfo=None)

        booking = offer.collectiveStock.lastBooking
        if booking:
            assert booking.confirmationLimitDate == new_limit.replace(tzinfo=None)

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", STATUSES_ALLOWING_EDIT_DISCOUNT)
    def test_can_lower_price_and_edit_price_details(self, status):
        offer = educational_factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        new_price = offer.collectiveStock.price - 100
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            totalPrice=new_price, educationalPriceDetail="yes", numberOfTickets=1200
        )
        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        assert offer.collectiveStock.price == new_price
        assert offer.collectiveStock.priceDetail == "yes"
        assert offer.collectiveStock.numberOfTickets == 1200

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_can_lower_price_and_edit_price_details_ended(self):
        offer = educational_factories.EndedCollectiveOfferFactory(booking_is_confirmed=True)

        new_price = offer.collectiveStock.price - 100
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            totalPrice=new_price, educationalPriceDetail="yes", numberOfTickets=1200
        )
        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        assert offer.collectiveStock.price == new_price
        assert offer.collectiveStock.priceDetail == "yes"
        assert offer.collectiveStock.numberOfTickets == 1200


@pytest.mark.usefixtures("db_session")
class ReturnErrorTest:
    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def test_edit_stock_of_non_approved_offer_fails(self) -> None:
        # Given
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.PENDING)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
            price=1200,
            numberOfTickets=30,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            numberOfTickets=35,
        )

        # When
        with pytest.raises(offers_exceptions.RejectedOrPendingOfferNotEditable) as error:
            educational_api_stock.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.numberOfTickets == 30

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_allow_stock_edition_when_startDatetime_not_provided_and_bookingLimitDatetime_set_after_existing_event_datetime(
        self,
    ) -> None:
        # Given
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=datetime.datetime(2021, 12, 10), bookingLimitDatetime=datetime.datetime(2021, 12, 5)
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            bookingLimitDatetime=datetime.datetime(2021, 12, 20, tzinfo=datetime.timezone.utc)
        )

        # When
        with pytest.raises(offers_exceptions.BookingLimitDatetimeTooLate):
            educational_api_stock.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == datetime.datetime(2021, 12, 5)

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_allow_stock_edition_when_bookingLimitDatetime_not_provided_and_startDatetime_set_before_existing_event_datetime(
        self,
    ) -> None:
        # Given
        educational_factories.EducationalYearFactory(
            beginningDate="2021-09-01T22:00:00Z", expirationDate="2022-07-31T22:00:00Z"
        )

        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=datetime.datetime(2021, 12, 10), bookingLimitDatetime=datetime.datetime(2021, 12, 5)
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime(2021, 12, 4, tzinfo=datetime.timezone.utc)
        )

        # When
        with pytest.raises(offers_exceptions.BookingLimitDatetimeTooLate):
            educational_api_stock.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.startDatetime == datetime.datetime(2021, 12, 10)

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_allow_stock_edition_and_not_modify_cancellation_limit_date_when_booking_cancelled(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=20)

        educational_factories.EducationalYearFactory(
            beginningDate=initial_event_date - datetime.timedelta(days=100),
            expirationDate=initial_event_date + datetime.timedelta(days=100),
        )

        cancellation_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.CANCELLED,
            cancellationLimitDate=cancellation_limit_date,
            confirmationLimitDate=datetime.datetime.utcnow() + datetime.timedelta(days=30),
        )

        new_event_date = datetime.datetime.now(  # pylint: disable=datetime-now
            datetime.timezone.utc
        ) + datetime.timedelta(days=25, hours=5)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=new_event_date,
        )

        # When
        educational_api_stock.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        booking = CollectiveBooking.query.filter_by(id=booking.id).one()
        assert booking.cancellationLimitDate == cancellation_limit_date
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.startDatetime == new_event_date.replace(tzinfo=None)

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def test_edit_offer_of_cancelled_booking(self) -> None:
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        educational_factories.EducationalYearFactory(
            beginningDate=initial_event_date - datetime.timedelta(days=100),
            expirationDate=initial_event_date + datetime.timedelta(days=100),
        )
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
            price=1200,
            numberOfTickets=30,
            startDatetime=initial_event_date,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.CANCELLED,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=5),
            totalPrice=1500,
            numberOfTickets=35,
            bookingLimitDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=5, hours=16),
        )

        # When
        educational_api_stock.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.startDatetime == new_stock_data.startDatetime.replace(tzinfo=None)
        assert stock.bookingLimitDatetime == new_stock_data.bookingLimitDatetime.replace(tzinfo=None)
        assert stock.price == 1500
        assert stock.numberOfTickets == 35

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    @time_machine.travel("2020-01-05 10:00:00")
    def test_edit_offer_of_other_status_booking(self) -> None:
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        initial_event_date = datetime.datetime.utcnow() - datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 1, 10), expirationDate=datetime.datetime(2020, 12, 12)
        )
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
            price=1200,
            numberOfTickets=30,
            startDatetime=initial_event_date,  # 2020-01-10 10:00:00
            bookingLimitDatetime=initial_booking_limit_date,  # 2020-01-08 10:00:00
        )

        educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.CANCELLED,
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.PENDING,
            educationalYear=educational_year,
        )

        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=5),  # 2020-01-12 15:00:00+00:00
            endDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=5),  # 2020-01-12 15:00:00+00:00
            totalPrice=1500,
            numberOfTickets=35,
            bookingLimitDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=5, hours=16),  # 2020-01-11 02:00:00+00:00
        )

        # When
        with pytest.raises(offers_exceptions.ApiErrors) as error:
            educational_api_stock.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        assert error.value.errors == {"global": ["Les évènements passés ne sont pas modifiables"]}

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def test_edit_price_or_ticket_number_if_status_confirmed(self):
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=10)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        booking = educational_factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CONFIRMED)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
            collectiveBookings=[booking],
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            totalPrice=1500,
            numberOfTickets=35,
        )

        # When
        with pytest.raises(exceptions.PriceRequesteCantBedHigherThanActualPrice):
            educational_api_stock.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.price == 1200

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", educational_testing.STATUSES_NOT_ALLOWING_EDIT_DETAILS)
    def test_cannot_increase_price(self, status):
        offer = educational_factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        price = offer.collectiveStock.price
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(totalPrice=price + 100)

        with pytest.raises(exceptions.CollectiveOfferForbiddenAction):
            educational_api_stock.edit_collective_stock(
                stock=offer.collectiveStock, stock_data=new_stock_data.dict(exclude_unset=True)
            )

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_cannot_increase_price_ended(self):
        offer = educational_factories.EndedCollectiveOfferFactory(booking_is_confirmed=True)
        price = offer.collectiveStock.price
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(totalPrice=price + 100)

        with pytest.raises(exceptions.CollectiveOfferForbiddenAction):
            educational_api_stock.edit_collective_stock(
                stock=offer.collectiveStock, stock_data=new_stock_data.dict(exclude_unset=True)
            )

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", STATUSES_NOT_ALLOWING_EDIT_DATES)
    def test_cannot_edit_dates(self, status):
        offer = educational_factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        new_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=5)
        for date_field in ("bookingLimitDatetime", "startDatetime", "endDatetime"):
            kwargs = {date_field: new_date}
            new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(**kwargs)

            with pytest.raises(exceptions.CollectiveOfferForbiddenAction):
                educational_api_stock.edit_collective_stock(
                    stock=offer.collectiveStock, stock_data=new_stock_data.dict(exclude_unset=True)
                )

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_cannot_edit_dates_ended(self):
        offer = educational_factories.EndedCollectiveOfferFactory(booking_is_confirmed=True)

        new_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=5)
        for date_field in ("bookingLimitDatetime", "startDatetime", "endDatetime"):
            kwargs = {date_field: new_date}
            new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(**kwargs)

            with pytest.raises(exceptions.CollectiveOfferForbiddenAction):
                educational_api_stock.edit_collective_stock(
                    stock=offer.collectiveStock, stock_data=new_stock_data.dict(exclude_unset=True)
                )

    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", STATUSES_NOT_ALLOWING_EDIT_DISCOUNT)
    def test_cannot_lower_price_and_edit_price_details(self, status):
        offer = educational_factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        changes = [
            {"totalPrice": offer.collectiveStock.price - 100},
            {"educationalPriceDetail": "yes"},
            {"numberOfTickets": 1200},
        ]
        for change in changes:
            new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(**change)

            with pytest.raises(exceptions.CollectiveOfferForbiddenAction):
                educational_api_stock.edit_collective_stock(
                    stock=offer.collectiveStock, stock_data=new_stock_data.dict(exclude_unset=True)
                )
