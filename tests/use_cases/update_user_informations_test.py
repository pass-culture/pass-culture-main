import pytest

from datetime import datetime
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user
from models import User
from use_cases.update_user_informations import AlterableUserInformations, update_user_informations

class UpdateUserInformationsTest:
    @clean_database
    def test_should_save_any_allowed_parameters(self, app):
        # Given
        user = create_user()
        repository.save(user)

        user_informations = AlterableUserInformations(
            id=user.id,
            has_seen_tutorials=False,
            cultural_survey_id=None,
            cultural_survey_filled_date=datetime(2020, 4, 22),
            department_code='76',
            email='son@goku.dbz',
            needs_to_fill_cultural_survey=True,
            phone_number='06 66 66 66 66',
            postal_code='76530',
            public_name='Son Goku',
        )

        # When
        update_user_informations(user_informations)

        # Then
        saved_user = User.query.filter(User.id==user_informations.id).one()
        assert saved_user.hasSeenTutorials == False
        assert saved_user.culturalSurveyId == None
        assert saved_user.culturalSurveyFilledDate == datetime(2020, 4, 22)
        assert saved_user.departementCode == '76'
        assert saved_user.email == 'son@goku.dbz'
        assert saved_user.needsToFillCulturalSurvey == True
        assert saved_user.phoneNumber == '06 66 66 66 66'
        assert saved_user.postalCode == '76530'
        assert saved_user.publicName == 'Son Goku'

    @clean_database
    def test_should_return_user_with_proper_infos(self, app):
        # Given
        user = create_user()
        repository.save(user)

        user_informations = AlterableUserInformations(
            id=user.id,
            has_seen_tutorials=True,
            cultural_survey_id=None,
            cultural_survey_filled_date=datetime(2020, 4, 22),
            department_code='27',
            email='han@solo.sw',
            needs_to_fill_cultural_survey=False,
            phone_number='05 55 55 55 55',
            postal_code='27200',
            public_name='Han Solo',
        )

        # When
        user = update_user_informations(user_informations)

        # Then
        assert user.hasSeenTutorials == True
        assert user.culturalSurveyId == None
        assert user.culturalSurveyFilledDate == datetime(2020, 4, 22)
        assert user.departementCode == '27'
        assert user.email == 'han@solo.sw'
        assert user.needsToFillCulturalSurvey == False
        assert user.phoneNumber == '05 55 55 55 55'
        assert user.postalCode == '27200'
        assert user.publicName == 'Han Solo'


    @clean_database
    def test_should_not_update_user_info_if_not_given(self, app):
        # Given
        user = create_user(phone_number='01 02 03 04 05')
        repository.save(user)

        user_informations = AlterableUserInformations(
            id=user.id,
            has_seen_tutorials=True,
        )

        # When
        updatedUser = update_user_informations(user_informations)

        # Then
        assert updatedUser.hasSeenTutorials == True
        assert updatedUser.phoneNumber == '01 02 03 04 05'

    @clean_database
    def test_should_not_update_user_info_in_db_if_not_given(self, app):
        # Given
        user = create_user(phone_number='01 02 03 04 05')
        repository.save(user)

        user_informations = AlterableUserInformations(
            id=user.id,
            has_seen_tutorials=True
        )

        # When
        update_user_informations(user_informations)

        # Then
        saved_user = User.query.filter(User.id==user_informations.id).one()
        assert saved_user.hasSeenTutorials == True
        assert saved_user.phoneNumber == '01 02 03 04 05'
