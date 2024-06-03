import datetime

import pytest
import time_machine

from pcapi.core.educational import exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.api import stock as educational_api_stock
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.serialization import collective_stock_serialize


@pytest.mark.usefixtures("db_session")
class EditCollectiveOfferStocksTest:
    def test_should_update_all_fields_when_all_changed(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            endDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=5),
            endDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=7),
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
        assert stock.endDatetime == new_stock_data.endDatetime.replace(tzinfo=None)
        assert stock.bookingLimitDatetime == new_stock_data.bookingLimitDatetime.replace(tzinfo=None)
        assert stock.price == 1500
        assert stock.numberOfTickets == 35

    def test_should_update_some_fields_and_keep_non_edited_ones(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            endDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=5),
            endDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
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
        assert stock.endDatetime == new_stock_data.endDatetime.replace(tzinfo=None)
        assert stock.bookingLimitDatetime == initial_booking_limit_date
        assert stock.price == 1200
        assert stock.numberOfTickets == 35

    def test_should_replace_bookingLimitDatetime_with_new_event_datetime_if_provided_but_none(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            endDatetime=initial_event_date,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_event_datetime = datetime.datetime.now(  # pylint: disable=datetime-now
            datetime.timezone.utc
        ) + datetime.timedelta(days=7, hours=5)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=new_event_datetime,
            endDatetime=new_event_datetime,
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
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            # beginningDatetime=initial_event_date,
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

    def test_should_not_allow_stock_edition_when_booking_status_is_REIMBURSED_or_USED(self) -> None:
        # Given
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            price=1500,
            # beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=2),
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
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            # beginningDatetime=initial_event_date,
            startDatetime=initial_event_date,
            endDatetime=initial_event_date,
        )
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
            # beginningDatetime=new_event_date,
            startDatetime=new_event_date,
            endDatetime=new_event_date,
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

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_allow_stock_edition_and_not_modify_cancellation_limit_date_when_booking_cancelled(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=20)
        cancellation_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            endDatetime=initial_event_date,
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
            endDatetime=new_event_date,
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
        assert stock.endDatetime == new_event_date.replace(tzinfo=None)


@pytest.mark.usefixtures("db_session")
class returnErrorTest:
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
    def test_should_not_allow_stock_edition_when_beginningDatetime_not_provided_and_bookingLimitDatetime_set_after_existing_event_datetime(
        self,
    ) -> None:
        # Given
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=datetime.datetime(2021, 12, 10),
            endDatetime=datetime.datetime(2021, 12, 10),
            bookingLimitDatetime=datetime.datetime(2021, 12, 5),
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
    def test_should_not_allow_stock_edition_when_bookingLimitDatetime_not_provided_and_beginningDatetime_set_before_existing_event_datetime(
        self,
    ) -> None:
        # Given
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=datetime.datetime(2021, 12, 10),
            endDatetime=datetime.datetime(2021, 12, 10),
            bookingLimitDatetime=datetime.datetime(2021, 12, 5),
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime(2021, 12, 4, tzinfo=datetime.timezone.utc),
            endDatetime=datetime.datetime(2021, 12, 4, tzinfo=datetime.timezone.utc),
        )

        # When
        with pytest.raises(offers_exceptions.BookingLimitDatetimeTooLate):
            educational_api_stock.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.startDatetime == datetime.datetime(2021, 12, 10)
        assert stock.endDatetime == datetime.datetime(2021, 12, 10)

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_allow_stock_edition_and_not_modify_cancellation_limit_date_when_booking_cancelled(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=20)
        cancellation_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            endDatetime=initial_event_date,
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
            endDatetime=new_event_date,
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
        assert stock.endDatetime == new_event_date.replace(tzinfo=None)

    def test_edit_offer_of_cancelled_booking(self) -> None:
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
            price=1200,
            numberOfTickets=30,
            startDatetime=initial_event_date,
            endDatetime=initial_event_date,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.CANCELLED,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=5),
            endDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
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
        assert stock.endDatetime == new_stock_data.endDatetime.replace(tzinfo=None)
        assert stock.bookingLimitDatetime == new_stock_data.bookingLimitDatetime.replace(tzinfo=None)
        assert stock.price == 1500
        assert stock.numberOfTickets == 35

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
            endDatetime=initial_event_date,  # 2020-01-10 10:00:00
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

    def test_edit_price_or_ticket_number_if_status_confirmed(self):
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=10)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        booking = educational_factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CONFIRMED)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            endDatetime=initial_event_date,
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
