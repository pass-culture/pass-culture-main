from scripts.delete_tables_from_activity import delete_tables_from_activity
from models.activity import load_activity
from tests.conftest import clean_database
from tests.test_utils import create_activity, save_all_activities

Activity = load_activity()


@clean_database
def test_should_delete_from_activity_when_table_name_is_in_provided_list(app):
    # Given
    product_activity = create_activity("product", "insert")
    save_all_activities(product_activity)

    # When
    delete_tables_from_activity(["product", "mediation"])

    # Then
    assert Activity.query.count() == 0


@clean_database
def test_should_not_delete_from_activity_when_table_name_is_not_in_provided_list(app):
    # Given
    product_activity = create_activity("product", "insert")
    save_all_activities(product_activity)

    # When
    delete_tables_from_activity(["bank_information"])

    # Then
    assert Activity.query.count() == 1


@clean_database
def test_should_delete_only_specified_tables_from_activity(app):
    # Given
    bank_information_activity = create_activity("bank_information", "insert")
    product_activity = create_activity("product", "insert")
    save_all_activities(bank_information_activity, product_activity)

    # When
    delete_tables_from_activity(["bank_information"])

    # Then
    assert Activity.query.all() == [product_activity]
