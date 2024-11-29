from datetime import date
from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import models as dms_models
from pcapi.core.users import ds as users_ds
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models

from . import ds_fixtures


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="instructor")
def instructor_fixture():
    return users_factories.AdminFactory(
        email="instructeur@example.com",
        backoffice_profile__dsInstructorId="SW5wdHK1Y3RleRItFeA2aEs",
    )


class SyncInstructorIdsTest:
    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_GET_INSTRUCTORS,
    )
    def test_sync_instructor_ids(self, mocked_get_instructors):
        admin_1 = users_factories.AdminFactory(email="one@example.com", backoffice_profile__dsInstructorId="ABC")
        admin_2 = users_factories.AdminFactory(email="two@example.com")
        admin_3 = users_factories.AdminFactory(email="three@example.com")
        admin_4 = users_factories.AdminFactory(email="four@example.com")

        users_ds.sync_instructor_ids(12345)

        mocked_get_instructors.assert_called_once_with(
            dms_api.GET_INSTRUCTORS_QUERY_NAME, variables={"demarcheNumber": 12345}
        )

        assert admin_1.backoffice_profile.dsInstructorId == "SW5wdHK1Y3RleRItFDU4MaEs"
        assert admin_2.backoffice_profile.dsInstructorId == "SW5wdHK1Y3RleRItMTAvMEI="
        assert admin_3.backoffice_profile.dsInstructorId == "SW5wdHK1Y3RleRItMRAkOCgz"
        assert admin_4.backoffice_profile.dsInstructorId is None


class SyncUserAccountUpdateRequestsTest:
    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_EMAIL_CHANGED,
    )
    def test_update_email(self, mocked_get_applications):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118, "archived": False}
        )

        uaur: users_models.UserAccountUpdateRequest = users_models.UserAccountUpdateRequest.query.one()
        assert uaur.dsApplicationId == 21163559
        assert uaur.status == dms_models.GraphQLApplicationStates.draft
        assert uaur.dateCreated == datetime(2024, 11, 26, 8, 31, 35)
        assert uaur.dateLastStatusUpdate == uaur.dateCreated
        assert uaur.firstName == "Jeune"
        assert uaur.lastName == "Bénéficiaire"
        assert uaur.email == "usager@example.com"
        assert uaur.birthDate == date(2006, 2, 1)
        assert uaur.user == beneficiary
        assert uaur.updateTypes == [users_models.UserAccountUpdateType.EMAIL]
        assert uaur.oldEmail == "beneficiaire@example.com"
        assert uaur.newEmail == "nouvelle.adresse@example.com"
        assert uaur.newPhoneNumber is None
        assert uaur.newFirstName is None
        assert uaur.newLastName is None
        assert uaur.allConditionsChecked is True
        assert uaur.lastInstructor is None
        assert uaur.dateLastUserMessage is None
        assert uaur.dateLastInstructorMessage is None
        assert uaur.flags == []

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_PHONE_NUMBER_CHANGED,
    )
    def test_update_phone_number(self, mocked_get_applications, instructor):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118, "archived": False}
        )

        uaur: users_models.UserAccountUpdateRequest = users_models.UserAccountUpdateRequest.query.one()
        assert uaur.dsApplicationId == 21166546
        assert uaur.status == dms_models.GraphQLApplicationStates.on_going
        assert uaur.dateCreated == datetime(2024, 11, 26, 10, 2, 46)
        assert uaur.dateLastStatusUpdate == datetime(2024, 11, 26, 10, 3, 14)
        assert uaur.firstName == "Jeune"
        assert uaur.lastName == "Bénéficiaire"
        assert uaur.email == "beneficiaire@example.com"
        assert uaur.birthDate == date(2006, 3, 2)
        assert uaur.user == beneficiary
        assert uaur.updateTypes == [users_models.UserAccountUpdateType.PHONE_NUMBER]
        assert uaur.oldEmail is None
        assert uaur.newEmail is None
        assert uaur.newPhoneNumber == "+33610203040"
        assert uaur.newFirstName is None
        assert uaur.newLastName is None
        assert uaur.allConditionsChecked is True
        assert uaur.lastInstructor == instructor
        assert uaur.dateLastUserMessage is None
        assert uaur.dateLastInstructorMessage == datetime(2024, 11, 26, 10, 4, 5)
        assert uaur.flags == []

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_TWO_APPLICATIONS_FIRST_NAME_LAST_NAME_CHANGED,
    )
    def test_update_names_for_two_applicants(self, mocked_get_applications, instructor):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118, "archived": False}
        )

        assert users_models.UserAccountUpdateRequest.query.count() == 2

        uaur = users_models.UserAccountUpdateRequest.query.filter_by(dsApplicationId=21167090).one()
        assert uaur.status == dms_models.GraphQLApplicationStates.accepted
        assert uaur.dateCreated == datetime(2024, 11, 26, 10, 19, 35)
        assert uaur.dateLastStatusUpdate == datetime(2024, 11, 26, 10, 21, 45)
        assert uaur.firstName == "Jeune"
        assert uaur.lastName == "Bénéficiaire"
        assert uaur.email == "beneficiaire@example.com"
        assert uaur.birthDate == date(2006, 4, 3)
        assert uaur.user == beneficiary
        assert uaur.updateTypes == [users_models.UserAccountUpdateType.FIRST_NAME]
        assert uaur.oldEmail is None
        assert uaur.newEmail is None
        assert uaur.newPhoneNumber is None
        assert uaur.newFirstName == "Vieux"
        assert uaur.newLastName is None
        assert uaur.allConditionsChecked is True
        assert uaur.lastInstructor == instructor
        assert uaur.dateLastUserMessage == datetime(2024, 11, 26, 10, 22, 51)
        assert uaur.dateLastInstructorMessage is None
        assert uaur.flags == []

        uaur = users_models.UserAccountUpdateRequest.query.filter_by(dsApplicationId=21167148).one()
        assert uaur.status == dms_models.GraphQLApplicationStates.draft
        assert uaur.dateCreated == datetime(2024, 11, 26, 10, 20, 50)
        assert uaur.dateLastStatusUpdate == datetime(2024, 11, 26, 10, 22, 16)
        assert uaur.firstName == "Jeune"
        assert uaur.lastName == "Inconnu"
        assert uaur.email == "usager@example.com"
        assert uaur.birthDate == date(2006, 5, 4)
        assert uaur.user is None  # no matching user found
        assert uaur.updateTypes == [users_models.UserAccountUpdateType.LAST_NAME]
        assert uaur.oldEmail is None
        assert uaur.newEmail is None
        assert uaur.newPhoneNumber is None
        assert uaur.newFirstName is None
        assert uaur.newLastName == "Bénéficiaire"
        assert uaur.allConditionsChecked is True
        assert uaur.lastInstructor == instructor
        assert uaur.dateLastUserMessage is None
        assert uaur.dateLastInstructorMessage == datetime(2024, 11, 26, 10, 22, 16)
        assert uaur.flags == [users_models.UserAccountUpdateFlag.WAITING_FOR_CORRECTION]

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_ACCOUNT_HAS_SAME,
    )
    def test_account_has_same(self, mocked_get_applications, instructor):
        beneficiary = users_factories.UserFactory(email="jeune@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118, "archived": False}
        )

        uaur: users_models.UserAccountUpdateRequest = users_models.UserAccountUpdateRequest.query.one()
        assert uaur.dsApplicationId == 21176193
        assert uaur.status == dms_models.GraphQLApplicationStates.draft
        assert uaur.dateCreated == datetime(2024, 11, 26, 15, 14, 14)
        assert uaur.dateLastStatusUpdate == uaur.dateCreated
        assert uaur.firstName == "Jeune"
        assert uaur.lastName == "En détresse"
        assert uaur.email == "jeune@example.com"
        assert uaur.birthDate == date(2006, 7, 6)
        assert uaur.user == beneficiary
        assert uaur.updateTypes == [users_models.UserAccountUpdateType.ACCOUNT_HAS_SAME_INFO]
        assert uaur.oldEmail is None
        assert uaur.newEmail is None
        assert uaur.newPhoneNumber is None
        assert uaur.newFirstName is None
        assert uaur.newLastName is None
        assert uaur.allConditionsChecked is True
        assert uaur.lastInstructor is None
        assert uaur.dateLastUserMessage is None
        assert uaur.dateLastInstructorMessage is None
        assert uaur.flags == []

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_APPLIED_BY_PROXY,
    )
    def test_applied_by_proxy(self, mocked_get_applications, instructor):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="jeune@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118, "archived": False}
        )

        uaur: users_models.UserAccountUpdateRequest = users_models.UserAccountUpdateRequest.query.one()
        assert uaur.dsApplicationId == 21176997
        assert uaur.status == dms_models.GraphQLApplicationStates.on_going
        assert uaur.dateCreated == datetime(2024, 11, 26, 15, 43, 28)
        assert uaur.dateLastStatusUpdate == datetime(2024, 11, 26, 15, 54, 29)
        assert uaur.firstName == "Jeune"
        assert uaur.lastName == "Enfant"
        assert uaur.email == "jeune@example.com"
        assert uaur.birthDate == date(2006, 8, 7)
        assert uaur.user == beneficiary
        assert uaur.updateTypes == [users_models.UserAccountUpdateType.PHONE_NUMBER]
        assert uaur.oldEmail is None
        assert uaur.newEmail is None
        assert uaur.newPhoneNumber == "+33733445566"
        assert uaur.newFirstName is None
        assert uaur.newLastName is None
        assert uaur.allConditionsChecked is True
        assert uaur.lastInstructor == instructor
        assert uaur.dateLastUserMessage is None
        assert uaur.dateLastInstructorMessage == datetime(2024, 11, 26, 15, 55, 14)
        assert uaur.flags == []

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_CORRECTION_RESOLVED,
    )
    def test_correction_resolved(self, mocked_get_applications, instructor):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="ancienne.adresse@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118, "archived": False}
        )

        uaur: users_models.UserAccountUpdateRequest = users_models.UserAccountUpdateRequest.query.one()
        assert uaur.dsApplicationId == 21177744
        assert uaur.status == dms_models.GraphQLApplicationStates.draft
        assert uaur.dateCreated == datetime(2024, 11, 26, 16, 4, 27)
        assert uaur.dateLastStatusUpdate == datetime(2024, 11, 26, 16, 5, 32)
        assert uaur.firstName == "Jeune"
        assert uaur.lastName == "Bénéficiaire"
        assert uaur.email == "beneficiaire@example.com"
        assert uaur.birthDate == date(2006, 9, 8)
        assert uaur.user == beneficiary
        assert uaur.updateTypes == [
            users_models.UserAccountUpdateType.EMAIL,
            users_models.UserAccountUpdateType.PHONE_NUMBER,
        ]
        assert uaur.oldEmail == "ancienne.adresse@example.com"
        assert uaur.newEmail == "nouvelle.adresse@example.com"
        assert uaur.newPhoneNumber == "+33733445566"
        assert uaur.newFirstName is None
        assert uaur.newLastName is None
        assert uaur.allConditionsChecked is True
        assert uaur.lastInstructor == instructor
        assert uaur.dateLastUserMessage is None
        assert uaur.dateLastInstructorMessage == datetime(2024, 11, 26, 16, 5, 4)
        assert uaur.flags == [users_models.UserAccountUpdateFlag.CORRECTION_RESOLVED]

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_MISSING_VALUE,
    )
    def test_missing_value(self, mocked_get_applications):
        users_factories.BeneficiaryGrant18Factory(email="ancienne.adresse@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118, "archived": False}
        )

        uaur: users_models.UserAccountUpdateRequest = users_models.UserAccountUpdateRequest.query.one()
        assert uaur.dsApplicationId == 21179224
        assert uaur.status == dms_models.GraphQLApplicationStates.draft
        assert uaur.dateCreated == datetime(2024, 11, 26, 17, 19, 42)
        assert uaur.dateLastStatusUpdate == uaur.dateCreated
        assert uaur.firstName == "Jeune"
        assert uaur.lastName == "Bénéficiaire"
        assert uaur.email == "nouvelle.adresse@example.com"
        assert uaur.birthDate is None  # birth date missing
        assert uaur.user is None  # old email missing => no matching
        assert uaur.updateTypes == [
            users_models.UserAccountUpdateType.EMAIL,
            users_models.UserAccountUpdateType.PHONE_NUMBER,
        ]
        assert uaur.oldEmail is None  # old email missing
        assert uaur.newEmail == "nouvelle.adresse@example.com"
        assert uaur.newPhoneNumber is None  # new phone number missing
        assert uaur.newFirstName is None
        assert uaur.newLastName is None
        assert uaur.allConditionsChecked is True
        assert uaur.lastInstructor is None
        assert uaur.dateLastUserMessage is None
        assert uaur.dateLastInstructorMessage is None
        assert uaur.flags == [users_models.UserAccountUpdateFlag.MISSING_VALUE]

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_INVALID_VALUE,
    )
    def test_invalid_value(self, mocked_get_applications):
        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118, "archived": False}
        )

        uaur: users_models.UserAccountUpdateRequest = users_models.UserAccountUpdateRequest.query.one()
        assert uaur.dsApplicationId == 21193637
        assert uaur.status == dms_models.GraphQLApplicationStates.draft
        assert uaur.dateCreated == datetime(2024, 11, 27, 14, 25, 3)
        assert uaur.dateLastStatusUpdate == uaur.dateCreated
        assert uaur.updateTypes == [users_models.UserAccountUpdateType.PHONE_NUMBER]
        assert uaur.newPhoneNumber == "0700000000"
        assert uaur.flags == [users_models.UserAccountUpdateFlag.INVALID_VALUE]

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_EMAIL_CHANGED,
    )
    def test_duplicate_new_email(self, mocked_get_applications):
        users_factories.UserFactory(email="nouvelle.adresse@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118, "archived": False}
        )

        uaur: users_models.UserAccountUpdateRequest = users_models.UserAccountUpdateRequest.query.one()
        assert uaur.dsApplicationId == 21163559
        assert uaur.flags == [users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL]

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_ARCHIVED,
    )
    def test_delete_archived(self, mocked_get_applications):
        users_factories.EmailUpdateRequestFactory(dsApplicationId=21168276)

        users_ds.sync_user_account_update_requests(104118, None, archived=True)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118, "archived": True}
        )

        assert users_models.UserAccountUpdateRequest.query.count() == 0
