from datetime import datetime

from models import PcObject
from models.activity import load_activity
from models.db import db
from scripts.clean_activity import delete_tables_from_activity, populate_stock_date_created_from_activity, \
    populate_cultural_survey_filled_date_from_activity
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_stock, create_offerer, create_venue
from tests.model_creators.activity_creators import create_activity, save_all_activities
from tests.model_creators.specific_creators import create_offer_with_thing_product

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
    def test_fills_stock_date_created_when_found_in_activity(self, app):
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


class PopulateCulturalSurveyFilledDateFromActivityTest:
    @clean_database
    def test_fills_cultural_survey_filled_date_from_activity(self, app):
        # Given
        user = create_user(id=1, needs_to_fill_cultural_survey=False)
        PcObject.save(user)
        modification_date = datetime(2019, 12, 1, 0, 0, 0)
        user_activity = create_activity(
            'user',
            'update',
            issued_at=modification_date,
            changed_data={'needsToFillCulturalSurvey': False},
            old_data={'id': 1}
        )
        save_all_activities(user_activity)

        # When
        populate_cultural_survey_filled_date_from_activity()

        # Then
        assert user.culturalSurveyFilledDate == modification_date

    @clean_database
    def test_does_not_fill_cultural_survey_filled_date_from_activity_when_user_id_does_not_match(self, app):
        # Given
        user = create_user(id=1, needs_to_fill_cultural_survey=False)
        PcObject.save(user)
        modification_date = datetime(2019, 12, 1, 0, 0, 0)
        user_activity = create_activity(
            'user',
            'update',
            issued_at=modification_date,
            changed_data={'id': 2, 'needsToFillCulturalSurvey': False}
        )
        save_all_activities(user_activity)

        # When
        populate_cultural_survey_filled_date_from_activity()

        # Then
        assert user.culturalSurveyFilledDate is None

    @clean_database
    def test_does_fill_cultural_survey_filled_date_with_last_matching_activity_date(self, app):
        # Given
        user = create_user(id=1, needs_to_fill_cultural_survey=True)
        PcObject.save(user)
        last_modification_date = datetime(2019, 12, 1, 0, 0, 0)
        user_activity_1 = create_activity(
            'user',
            'update',
            issued_at=datetime(2019, 10, 1, 0, 0, 0),
            changed_data={'needsToFillCulturalSurvey': False},
            old_data={'id': 1}
        )
        user_activity_2 = create_activity(
            'user',
            'update',
            issued_at=datetime(2019, 11, 1, 0, 0, 0),
            changed_data={'needsToFillCulturalSurvey': True},
            old_data={'id': 1}

        )
        user_activity_3 = create_activity(
            'user',
            'update',
            issued_at=last_modification_date,
            changed_data={'needsToFillCulturalSurvey': False},
            old_data={'id': 1}
        )
        save_all_activities(user_activity_1, user_activity_2, user_activity_3)

        # When
        populate_cultural_survey_filled_date_from_activity()

        # Then
        assert user.culturalSurveyFilledDate == last_modification_date
