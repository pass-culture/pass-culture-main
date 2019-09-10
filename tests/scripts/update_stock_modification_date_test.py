from datetime import datetime

from models import PcObject, Booking, Stock
from scripts.fill_date_used_for_bookings import fill_date_used_for_bookings
from scripts.update_stock_modification_date import update_stock_modification_date
from tests.conftest import clean_database
from tests.test_utils import create_booking, create_user, create_deposit, create_booking_activity, save_all_activities, \
    create_stock, create_offer_with_thing_product, create_stock_activity, create_venue, create_offerer


class UpdateStockModificationDateTest:
    @clean_database
    def test_should_change_modified_date_using_the_update_activity(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, available=10, date_modified=datetime(2019, 10, 13))
        PcObject.save(stock)

        activity = create_stock_activity(
            stock=stock,
            verb='update',
            issued_at=datetime(2019, 10, 21),
            data={"available": 32}
        )
        save_all_activities(activity)

        # When
        update_stock_modification_date()

        # Then
        updated_stock = Stock.query.first()
        assert updated_stock.dateModified == datetime(2019, 10, 21)

    @clean_database
    def test_should_change_modified_date_using_the_very_last_update_activity(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, available=10, date_modified=datetime(2019, 10, 13))
        PcObject.save(stock)

        first_activity = create_stock_activity(
            stock=stock,
            verb='update',
            issued_at=datetime(2019, 10, 21),
            data={"available": 32}
        )

        second_activity = create_stock_activity(
            stock=stock,
            verb='update',
            issued_at=datetime(2019, 12, 25),
            data={"available": 32}
        )
        save_all_activities(first_activity, second_activity)

        # When
        update_stock_modification_date()

        # Then
        updated_stock = Stock.query.first()
        assert updated_stock.dateModified == datetime(2019, 12, 25)

    @clean_database
    def test_should_change_modified_date_for_every_stock(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        first_stock = create_stock(offer=offer, available=10, date_modified=datetime(2019, 10, 13))
        second_stock = create_stock(offer=offer, available=10, date_modified=datetime(2018, 10, 13))
        PcObject.save(first_stock, second_stock)

        activity_for_first_stock = create_stock_activity(
            stock=first_stock,
            verb='update',
            issued_at=datetime(2019, 10, 21),
            data={"available": 32}
        )

        activity_for_second_stock = create_stock_activity(
            stock=second_stock,
            verb='update',
            issued_at=datetime(2018, 11, 16),
            data={"available": 32}
        )
        save_all_activities(activity_for_first_stock, activity_for_second_stock)

        # When
        update_stock_modification_date()

        # Then
        first_updated_stock = Stock.query.get(first_stock.id)
        second_updated_stock = Stock.query.get(second_stock.id)
        assert first_updated_stock.dateModified == datetime(2019, 10, 21)
        assert second_updated_stock.dateModified == datetime(2018, 11, 16)

