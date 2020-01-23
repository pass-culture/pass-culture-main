from datetime import datetime

from models import Stock
from models.db import db
from repository import repository
from scripts.update_stock_modification_date import update_stock_modification_date_sql_version
from tests.conftest import clean_database
from tests.model_creators.activity_creators import create_stock_activity, save_all_activities
from tests.model_creators.generic_creators import create_stock, create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product


class UpdateStockModificationDateTest:
    @clean_database
    def test_should_change_modified_date_using_the_update_activity(self, app):
        # Given
        db.engine.execute("ALTER TABLE stock DISABLE TRIGGER stock_update_modification_date;")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, available=10, date_modified=datetime(2019, 10, 13))
        repository.save(stock)

        activity = create_stock_activity(
            stock=stock,
            verb='update',
            issued_at=datetime(2019, 10, 21),
            data={"available": 32}
        )
        save_all_activities(activity)

        # When
        update_stock_modification_date_sql_version()

        # Then
        updated_stock = Stock.query.first()
        assert updated_stock.dateModified == datetime(2019, 10, 21)
        db.engine.execute("ALTER TABLE stock ENABLE TRIGGER stock_update_modification_date;")

    @clean_database
    def test_should_change_modified_date_using_the_very_last_update_activity(self, app):
        # Given
        db.engine.execute("ALTER TABLE stock DISABLE TRIGGER stock_update_modification_date;")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, available=10, date_modified=datetime(2019, 10, 13))
        repository.save(stock)

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
        update_stock_modification_date_sql_version()

        # Then
        updated_stock = Stock.query.first()
        assert updated_stock.dateModified == datetime(2019, 12, 25)
        db.engine.execute("ALTER TABLE stock ENABLE TRIGGER stock_update_modification_date;")

    @clean_database
    def test_should_change_modified_date_for_every_stock(self, app):
        # Given
        db.engine.execute("ALTER TABLE stock DISABLE TRIGGER stock_update_modification_date;")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        first_stock = create_stock(offer=offer, available=10, date_modified=datetime(2019, 10, 13))
        second_stock = create_stock(offer=offer, available=10, date_modified=datetime(2018, 10, 13))
        repository.save(first_stock, second_stock)

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
        update_stock_modification_date_sql_version()

        # Then
        first_updated_stock = Stock.query.get(first_stock.id)
        second_updated_stock = Stock.query.get(second_stock.id)
        assert first_updated_stock.dateModified == datetime(2019, 10, 21)
        assert second_updated_stock.dateModified == datetime(2018, 11, 16)
        db.engine.execute("ALTER TABLE stock ENABLE TRIGGER stock_update_modification_date;")
