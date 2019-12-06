from models import PcObject
from models.activity import load_activity
from models.db import db
from scripts.clean_activity import delete_tables_from_activity, populate_stock_date_created_from_activity
from tests.conftest import clean_database
from tests.test_utils import create_activity, save_all_activities, create_stock, create_venue, create_offerer, \
    create_offer_with_thing_product

Activity = load_activity()


class DeleteTablesFromActivityTest:
    @clean_database
    def test_should_delete_from_activity_when_table_name_is_in_provided_list(self, app):
        # Given
        product_activity = create_activity('product', 'insert')
        save_all_activities(product_activity)

        # When
        delete_tables_from_activity(['product', 'mediation'])

        # Then
        assert Activity.query.count() == 0

    @clean_database
    def test_should_not_delete_from_activity_when_table_name_is_not_in_provided_list(self, app):
        # Given
        product_activity = create_activity('product', 'insert')
        save_all_activities(product_activity)

        # When
        delete_tables_from_activity(['bank_information'])

        # Then
        assert Activity.query.count() == 1

    @clean_database
    def test_should_delete_only_specified_tables_from_activity(self, app):
        # Given
        bank_information_activity = create_activity('bank_information', 'insert')
        product_activity = create_activity('product', 'insert')
        save_all_activities(bank_information_activity, product_activity)

        # When
        delete_tables_from_activity(['bank_information'])

        # Then
        assert Activity.query.all() == [product_activity]


class PopulateStockDateCreatedFromActivityTest:
    @clean_database
    def test_fills_stock_date_created_if_found_in_activity(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer)
        PcObject.save(stock)
        activity_issued_at = db.session.execute('''
            SELECT issued_at 
            FROM activity 
            WHERE verb = 'insert' 
            AND table_name = 'stock'
        ''')

        # When
        populate_stock_date_created_from_activity()

        # Then
        assert stock.dateCreated == activity_issued_at.first()[0]
