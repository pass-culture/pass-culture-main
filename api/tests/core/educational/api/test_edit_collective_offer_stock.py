import datetime

import pytest
import time_machine

from pcapi.core.educational import exceptions
from pcapi.core.educational import factories
from pcapi.core.educational import testing
from pcapi.core.educational.api import stock as educational_api_stock
from pcapi.core.educational.models import CollectiveAdditionalFeeType
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models import db
from pcapi.routes.serialization import collective_stock_serialize
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


class EditCollectiveOfferStocksTest:
    def test_should_update_all_fields_when_all_changed(self) -> None:
        initial_event_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=5)
        initial_booking_limit_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=3)
        factories.create_educational_year(initial_event_date)

        stock_to_be_updated = factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7, hours=5),
            endDatetime=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7, hours=5),
            bookingLimitDatetime=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=5, hours=16),
            price=1500,
            numberOfTickets=35,
        )

        educational_api_stock.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        stock = db.session.query(CollectiveStock).filter_by(id=stock_to_be_updated.id).one()
        assert stock.startDatetime == new_stock_data.startDatetime.replace(tzinfo=None)
        assert stock.bookingLimitDatetime == new_stock_data.bookingLimitDatetime.replace(tzinfo=None)
        assert stock.price == 1500
        assert stock.numberOfTickets == 35

    def test_should_update_some_fields_and_keep_non_edited_ones(self) -> None:
        initial_event_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=5)
        initial_booking_limit_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=3)
        factories.create_educational_year(initial_event_date)
        stock_to_be_updated = factories.CollectiveStockFactory(
            startDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7, hours=5),
            endDatetime=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7, hours=5),
            numberOfTickets=35,
        )

        educational_api_stock.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        stock = db.session.query(CollectiveStock).filter_by(id=stock_to_be_updated.id).one()
        assert stock.startDatetime == new_stock_data.startDatetime.replace(tzinfo=None)
        assert stock.bookingLimitDatetime == initial_booking_limit_date
        assert stock.price == 1200
        assert stock.numberOfTickets == 35

    @time_machine.travel("2020-11-17 15:00:00")
    def should_update_bookings_cancellation_limit_date_if_event_postponed(self) -> None:
        initial_event_date = datetime.datetime(2021, 12, 7, 15)
        educational_year = factories.create_educational_year(initial_event_date)
        cancellation_limit_date = datetime.datetime(2021, 11, 22, 15)
        stock_to_be_updated = factories.CollectiveStockFactory(startDatetime=initial_event_date)
        booking = factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.PENDING,
            cancellationLimitDate=cancellation_limit_date,
            confirmationLimitDate=datetime.datetime(2021, 12, 17, 15),
            educationalYear=educational_year,
        )

        data = {
            "startDatetime": datetime.datetime(2021, 12, 12, 20),
            "endDatetime": datetime.datetime(2021, 12, 12, 20),
        }

        educational_api_stock.edit_collective_stock(stock=stock_to_be_updated, stock_data=data)

        booking_updated = db.session.query(CollectiveBooking).filter_by(id=booking.id).one()
        assert booking_updated.cancellationLimitDate == datetime.datetime(2021, 11, 12, 20)

    @time_machine.travel("2020-11-17 15:00:00", tick=False)
    def should_update_bookings_cancellation_limit_date_if_startDatetime_earlier(self) -> None:
        initial_event_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=20)
        educational_year = factories.educational_year = factories.create_educational_year(initial_event_date)
        cancellation_limit_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=5)
        stock_to_be_updated = factories.CollectiveStockFactory(startDatetime=initial_event_date)
        booking = factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.PENDING,
            cancellationLimitDate=cancellation_limit_date,
            confirmationLimitDate=date_utils.get_naive_utc_now() + datetime.timedelta(days=30),
            educationalYear=educational_year,
        )

        new_event_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=5, hours=5)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=new_event_date,
            bookingLimitDatetime=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3, hours=5),
        )

        educational_api_stock.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        booking_updated = db.session.query(CollectiveBooking).filter_by(id=booking.id).one()
        assert booking_updated.cancellationLimitDate == date_utils.get_naive_utc_now()

    def test_should_update_expired_booking(self) -> None:
        now = date_utils.get_naive_utc_now()
        limit = now - datetime.timedelta(days=2)
        stock = factories.CollectiveStockFactory(
            startDatetime=now + datetime.timedelta(days=5), bookingLimitDatetime=limit
        )
        booking = factories.CollectiveBookingFactory(
            collectiveStock=stock,
            status=CollectiveBookingStatus.CANCELLED,
            cancellationReason=CollectiveBookingCancellationReasons.EXPIRED,
            cancellationDate=now - datetime.timedelta(days=1),
            confirmationLimitDate=limit,
        )

        new_limit = now + datetime.timedelta(days=1)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(bookingLimitDatetime=new_limit)
        educational_api_stock.edit_collective_stock(
            stock=stock, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        assert stock.bookingLimitDatetime == new_limit
        assert booking.status == CollectiveBookingStatus.PENDING
        assert booking.cancellationReason == None
        assert booking.cancellationDate == None
        assert booking.confirmationLimitDate == new_limit

    @pytest.mark.parametrize("status", testing.STATUSES_ALLOWING_EDIT_DETAILS)
    def test_can_increase_price(self, status):
        offer = factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            factories.CollectiveStockFactory(collectiveOffer=offer)

        price = offer.collectiveStock.price
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(price=price + 100)

        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        assert offer.collectiveStock.price == price + 100

    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    @pytest.mark.parametrize("status", testing.STATUSES_ALLOWING_EDIT_DETAILS)
    def test_can_increase_service_price(self, status):
        offer = factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            factories.CollectiveStockFactory(collectiveOffer=offer)

        price = offer.collectiveStock.price
        service_price = offer.collectiveStock.servicePrice
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            price=price + 50, servicePrice=service_price + 50, collectiveAdditionalFees=[]
        )

        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        assert offer.collectiveStock.price == price + 50
        assert offer.collectiveStock.servicePrice == service_price + 50
        assert offer.collectiveStock.collectiveAdditionalFees == []

    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    @pytest.mark.parametrize("status", testing.STATUSES_ALLOWING_EDIT_DETAILS)
    def test_can_add_fee(self, status):
        offer = factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            factories.CollectiveStockFactory(collectiveOffer=offer)

        price = offer.collectiveStock.price
        service_price = offer.collectiveStock.servicePrice
        new_fees = [{"type": CollectiveAdditionalFeeType.TRAVEL.name, "label": None, "amount": 10}]
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            price=price + 10,
            servicePrice=service_price,
            collectiveAdditionalFees=new_fees,
        )

        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        assert offer.collectiveStock.price == price + 10
        assert offer.collectiveStock.servicePrice == service_price
        assert [
            {"type": fee.type.name, "label": fee.label, "amount": fee.amount}
            for fee in offer.collectiveStock.collectiveAdditionalFees
        ] == new_fees

    @time_machine.travel("2020-11-17 15:00:00", tick=False)
    @pytest.mark.parametrize("status", testing.STATUSES_ALLOWING_EDIT_DATES)
    def test_can_edit_dates(self, status):
        factories.EducationalCurrentYearFactory()
        offer = factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            factories.CollectiveStockFactory(collectiveOffer=offer)

        new_limit = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10)
        new_start = new_limit + datetime.timedelta(days=5)
        new_end = new_limit + datetime.timedelta(days=7)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            bookingLimitDatetime=new_limit, startDatetime=new_start, endDatetime=new_end
        )
        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        assert offer.collectiveStock.bookingLimitDatetime == new_limit.replace(tzinfo=None)
        assert offer.collectiveStock.startDatetime == new_start.replace(tzinfo=None)
        assert offer.collectiveStock.endDatetime == new_end.replace(tzinfo=None)

        booking = offer.collectiveStock.lastBooking
        if booking:
            assert booking.confirmationLimitDate == new_limit.replace(tzinfo=None)

    @pytest.mark.parametrize("status", testing.STATUSES_ALLOWING_EDIT_DISCOUNT)
    def test_can_lower_price_and_edit_price_details(self, status):
        offer = factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            factories.CollectiveStockFactory(collectiveOffer=offer)

        new_price = offer.collectiveStock.price - 100
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            price=new_price, priceDetail="yes", numberOfTickets=1200
        )
        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        assert offer.collectiveStock.price == new_price
        assert offer.collectiveStock.priceDetail == "yes"
        assert offer.collectiveStock.numberOfTickets == 1200

    def test_can_lower_price_and_edit_price_details_ended(self):
        offer = factories.EndedCollectiveOfferConfirmedBookingFactory()

        new_price = offer.collectiveStock.price - 100
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            price=new_price, priceDetail="yes", numberOfTickets=1200
        )
        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        assert offer.collectiveStock.price == new_price
        assert offer.collectiveStock.priceDetail == "yes"
        assert offer.collectiveStock.numberOfTickets == 1200

    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    @pytest.mark.parametrize("status", testing.STATUSES_ALLOWING_EDIT_DISCOUNT)
    def test_can_lower_service_price(self, status):
        offer = factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            factories.CollectiveStockFactory(collectiveOffer=offer)

        price = offer.collectiveStock.price
        service_price = offer.collectiveStock.servicePrice
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            price=price - 10, servicePrice=service_price - 10, collectiveAdditionalFees=[]
        )

        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        assert offer.collectiveStock.price == price - 10
        assert offer.collectiveStock.servicePrice == service_price - 10
        assert offer.collectiveStock.collectiveAdditionalFees == []

    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    @pytest.mark.parametrize("status", testing.STATUSES_ALLOWING_EDIT_DISCOUNT)
    def test_can_lower_fee(self, status):
        offer = factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            stock = factories.CollectiveStockFactory(collectiveOffer=offer, price=100, servicePrice=50)
            factories.CollectiveAdditionalFeeFactory(collectiveStock=stock, amount=50)

        price = 100
        service_price = 50
        new_fees = [{"type": CollectiveAdditionalFeeType.TRAVEL.name, "label": None, "amount": 40}]
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            price=price - 10, servicePrice=service_price, collectiveAdditionalFees=new_fees
        )

        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )

        assert offer.collectiveStock.price == price - 10
        assert offer.collectiveStock.servicePrice == service_price
        assert [
            {"type": fee.type.name, "label": fee.label, "amount": fee.amount}
            for fee in offer.collectiveStock.collectiveAdditionalFees
        ] == new_fees

    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    def test_additional_fees(self):
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer, price=150, servicePrice=50)
        factories.CollectiveAdditionalFeeFactory(
            collectiveStock=stock, type=CollectiveAdditionalFeeType.TRAVEL, label=None, amount=40
        )
        factories.CollectiveAdditionalFeeFactory(
            collectiveStock=stock, type=CollectiveAdditionalFeeType.MEAL, label=None, amount=30
        )
        factories.CollectiveAdditionalFeeFactory(
            collectiveStock=stock, type=CollectiveAdditionalFeeType.OTHER, label="first other fee", amount=20
        )
        factories.CollectiveAdditionalFeeFactory(
            collectiveStock=stock, type=CollectiveAdditionalFeeType.OTHER, label="second other fee", amount=10
        )

        new_fees = [
            # TRAVEL amount is lowered
            {"type": CollectiveAdditionalFeeType.TRAVEL.name, "label": None, "amount": 30},
            # ACCOMMODATION is added
            {"type": CollectiveAdditionalFeeType.ACCOMMODATION.name, "label": None, "amount": 40},
            # first OTHER amount is increased
            {"type": CollectiveAdditionalFeeType.OTHER.name, "label": "first other fee", "amount": 50},
            # MEAL and second OTHER are removed
        ]
        new_price = 50 + 30 + 40 + 50
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            price=new_price, servicePrice=50, collectiveAdditionalFees=new_fees
        )

        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )
        db.session.refresh(stock)

        assert offer.collectiveStock.price == new_price
        assert offer.collectiveStock.servicePrice == 50
        assert [
            {"type": fee.type.name, "label": fee.label, "amount": fee.amount}
            for fee in sorted(stock.collectiveAdditionalFees, key=lambda f: f.amount)
        ] == new_fees

    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    def test_remove_additional_fees(self):
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer, price=150, servicePrice=50)
        factories.CollectiveAdditionalFeeFactory(
            collectiveStock=stock, type=CollectiveAdditionalFeeType.TRAVEL, label=None, amount=40
        )
        factories.CollectiveAdditionalFeeFactory(
            collectiveStock=stock, type=CollectiveAdditionalFeeType.MEAL, label=None, amount=30
        )

        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            price=50, servicePrice=50, collectiveAdditionalFees=[]
        )
        educational_api_stock.edit_collective_stock(
            stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
        )
        db.session.refresh(stock)

        assert offer.collectiveStock.price == 50
        assert offer.collectiveStock.servicePrice == 50
        assert stock.collectiveAdditionalFees == []


class ReturnErrorTest:
    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_allow_stock_edition_when_startDatetime_not_provided_and_bookingLimitDatetime_set_after_existing_event_datetime(
        self,
    ) -> None:
        stock_to_be_updated = factories.CollectiveStockFactory(
            startDatetime=datetime.datetime(2021, 12, 10), bookingLimitDatetime=datetime.datetime(2021, 12, 5)
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            bookingLimitDatetime=datetime.datetime(2021, 12, 20, tzinfo=datetime.timezone.utc)
        )

        with pytest.raises(offers_exceptions.BookingLimitDatetimeTooLate):
            educational_api_stock.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.model_dump(exclude_unset=True)
            )

        stock = db.session.query(CollectiveStock).filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == datetime.datetime(2021, 12, 5)

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_allow_stock_edition_when_bookingLimitDatetime_not_provided_and_startDatetime_set_before_existing_event_datetime(
        self,
    ) -> None:
        factories.create_educational_year(datetime.datetime(2021, 12, 10))

        stock_to_be_updated = factories.CollectiveStockFactory(
            startDatetime=datetime.datetime(2021, 12, 10), bookingLimitDatetime=datetime.datetime(2021, 12, 5)
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            startDatetime=datetime.datetime(2021, 12, 4, tzinfo=datetime.timezone.utc)
        )

        with pytest.raises(offers_exceptions.BookingLimitDatetimeTooLate):
            educational_api_stock.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.model_dump(exclude_unset=True)
            )

        stock = db.session.query(CollectiveStock).filter_by(id=stock_to_be_updated.id).one()
        assert stock.startDatetime == datetime.datetime(2021, 12, 10)

    @pytest.mark.parametrize("status", testing.STATUSES_NOT_ALLOWING_EDIT_DETAILS)
    def test_cannot_increase_price(self, status):
        offer = factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            factories.CollectiveStockFactory(collectiveOffer=offer)

        price = offer.collectiveStock.price
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(price=price + 100)

        with pytest.raises(exceptions.CollectiveOfferForbiddenAction):
            educational_api_stock.edit_collective_stock(
                stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
            )

    def test_cannot_increase_price_ended(self):
        offer = factories.EndedCollectiveOfferConfirmedBookingFactory()
        price = offer.collectiveStock.price
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(price=price + 100)

        with pytest.raises(exceptions.CollectiveOfferForbiddenAction):
            educational_api_stock.edit_collective_stock(
                stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
            )

    @pytest.mark.parametrize("status", testing.STATUSES_NOT_ALLOWING_EDIT_DATES)
    def test_cannot_edit_dates(self, status):
        offer = factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            factories.CollectiveStockFactory(collectiveOffer=offer)

        new_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=5)
        for date_field in ("bookingLimitDatetime", "startDatetime", "endDatetime"):
            kwargs = {date_field: new_date}
            new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(**kwargs)

            with pytest.raises(exceptions.CollectiveOfferForbiddenAction):
                educational_api_stock.edit_collective_stock(
                    stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
                )

    def test_cannot_edit_dates_ended(self):
        offer = factories.EndedCollectiveOfferConfirmedBookingFactory()

        new_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=5)
        for date_field in ("bookingLimitDatetime", "startDatetime", "endDatetime"):
            kwargs = {date_field: new_date}
            new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(**kwargs)

            with pytest.raises(exceptions.CollectiveOfferForbiddenAction):
                educational_api_stock.edit_collective_stock(
                    stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
                )

    @pytest.mark.parametrize("status", testing.STATUSES_NOT_ALLOWING_EDIT_DISCOUNT)
    def test_cannot_lower_price_and_edit_price_details(self, status):
        offer = factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            factories.CollectiveStockFactory(collectiveOffer=offer)

        changes = [
            {"price": offer.collectiveStock.price - 100},
            {"priceDetail": "yes"},
            {"numberOfTickets": 1200},
        ]
        for change in changes:
            new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(**change)

            with pytest.raises(exceptions.CollectiveOfferForbiddenAction):
                educational_api_stock.edit_collective_stock(
                    stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
                )

    @pytest.mark.features(WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS=True)
    @pytest.mark.parametrize("status", testing.STATUSES_NOT_ALLOWING_EDIT_DISCOUNT)
    def test_cannot_edit_price_fields(self, status):
        offer = factories.create_collective_offer_by_status(status)

        if offer.collectiveStock is None:
            factories.CollectiveStockFactory(collectiveOffer=offer)

        changes = [
            {"numberOfTeachers": 20},
            {
                "price": offer.collectiveStock.price - 10,
                "servicePrice": offer.collectiveStock.price - 10,
                "collectiveAdditionalFees": [],
            },
        ]
        for change in changes:
            new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(**change)

            with pytest.raises(exceptions.CollectiveOfferForbiddenAction):
                educational_api_stock.edit_collective_stock(
                    stock=offer.collectiveStock, stock_data=new_stock_data.model_dump(exclude_unset=True)
                )

    @time_machine.travel("2020-11-17 15:00:00")
    def test_cannot_set_end_before_stock_start(self):
        start = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10)
        factories.create_educational_year(date_time=start)
        stock = factories.CollectiveStockFactory(startDatetime=start)

        new_end = start - datetime.timedelta(days=1)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(endDatetime=new_end)

        with pytest.raises(exceptions.EndDatetimeBeforeStartDatetime):
            educational_api_stock.edit_collective_stock(
                stock=stock, stock_data=new_stock_data.model_dump(exclude_unset=True)
            )
