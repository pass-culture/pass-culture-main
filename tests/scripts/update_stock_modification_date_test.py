from datetime import datetime

from pcapi.model_creators.activity_creators import create_stock_activity
from pcapi.model_creators.activity_creators import save_all_activities
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import StockSQLEntity
from pcapi.models.db import db
from pcapi.repository import repository
from pcapi.scripts.update_stock_modification_date import update_stock_modification_date_sql_version

from tests.conftest import clean_database


class UpdateStockModificationDateTest:
    @clean_database
    def test_should_change_modified_date_using_the_update_activity(self, app):
        # Given
        db.engine.execute("ALTER TABLE stock DISABLE TRIGGER stock_update_modification_date;")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(date_modified=datetime(2019, 10, 13), offer=offer, quantity=10)
        repository.save(stock)

        activity = create_stock_activity(
            stock=stock, verb="update", issued_at=datetime(2019, 10, 21), data={"quantity": 32}
        )
        save_all_activities(activity)

        # When
        update_stock_modification_date_sql_version()

        # Then
        updated_stock = StockSQLEntity.query.first()
        assert updated_stock.dateModified == datetime(2019, 10, 21)
        db.engine.execute("ALTER TABLE stock ENABLE TRIGGER stock_update_modification_date;")

    @clean_database
    def test_should_change_modified_date_using_the_very_last_update_activity(self, app):
        # Given
        db.engine.execute("ALTER TABLE stock DISABLE TRIGGER stock_update_modification_date;")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(date_modified=datetime(2019, 10, 13), offer=offer, quantity=10)
        repository.save(stock)

        first_activity = create_stock_activity(
            stock=stock, verb="update", issued_at=datetime(2019, 10, 21), data={"quantity": 32}
        )

        second_activity = create_stock_activity(
            stock=stock, verb="update", issued_at=datetime(2019, 12, 25), data={"quantity": 32}
        )
        save_all_activities(first_activity, second_activity)

        # When
        update_stock_modification_date_sql_version()

        # Then
        updated_stock = StockSQLEntity.query.first()
        assert updated_stock.dateModified == datetime(2019, 12, 25)
        db.engine.execute("ALTER TABLE stock ENABLE TRIGGER stock_update_modification_date;")

    @clean_database
    def test_should_change_modified_date_for_every_stock(self, app):
        # Given
        db.engine.execute("ALTER TABLE stock DISABLE TRIGGER stock_update_modification_date;")
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        first_stock = create_stock(date_modified=datetime(2019, 10, 13), offer=offer, quantity=10)
        second_stock = create_stock(date_modified=datetime(2018, 10, 13), offer=offer, quantity=10)
        repository.save(first_stock, second_stock)

        activity_for_first_stock = create_stock_activity(
            stock=first_stock, verb="update", issued_at=datetime(2019, 10, 21), data={"quantity": 32}
        )

        activity_for_second_stock = create_stock_activity(
            stock=second_stock, verb="update", issued_at=datetime(2018, 11, 16), data={"quantity": 32}
        )
        save_all_activities(activity_for_first_stock, activity_for_second_stock)

        # When
        update_stock_modification_date_sql_version()

        # Then
        first_updated_stock = StockSQLEntity.query.get(first_stock.id)
        second_updated_stock = StockSQLEntity.query.get(second_stock.id)
        assert first_updated_stock.dateModified == datetime(2019, 10, 21)
        assert second_updated_stock.dateModified == datetime(2018, 11, 16)
        db.engine.execute("ALTER TABLE stock ENABLE TRIGGER stock_update_modification_date;")
