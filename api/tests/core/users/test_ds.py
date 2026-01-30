import copy
from dataclasses import asdict
from datetime import date
from datetime import datetime
from unittest.mock import patch

import pytest
import time_machine

import pcapi.core.mails.testing as mails_testing
from pcapi import settings
from pcapi import settings as pcapi_settings
from pcapi.connectors.dms import api as dms_api
from pcapi.connectors.dms import exceptions as dms_exceptions
from pcapi.connectors.dms import models as dms_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import ds as users_ds
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db

from . import ds_fixtures


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="instructor")
def instructor_fixture():
    return users_factories.AdminFactory(
        email="instructeur@passculture.app",
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
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()
        assert uaur.dsApplicationId == 21163559
        assert uaur.dsTechnicalId == "UHJvY4VkdXKlLTI5NTgw"
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
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()
        assert uaur.dsApplicationId == 21166546
        assert uaur.dsTechnicalId == "UHJvY4VkdXKlLTI5NTgw"
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
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        assert db.session.query(users_models.UserAccountUpdateRequest).count() == 2

        uaur = db.session.query(users_models.UserAccountUpdateRequest).filter_by(dsApplicationId=21167090).one()
        assert uaur.dsTechnicalId == "UHJvY4VkdXKlLTI5NTgw"
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

        uaur = db.session.query(users_models.UserAccountUpdateRequest).filter_by(dsApplicationId=21167148).one()
        assert uaur.dsTechnicalId == "UHJvY4VkdXKlLTI5NTgx"
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

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "usager@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.UPDATE_REQUEST_NO_USER_FOUND.value)
        assert mails_testing.outbox[0]["params"]["DS_APPLICATION_NUMBER"] == uaur.dsApplicationId

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_ACCOUNT_HAS_SAME,
    )
    def test_account_has_same(self, mocked_get_applications, instructor):
        beneficiary = users_factories.UserFactory(email="jeune@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()
        assert uaur.dsApplicationId == 21176193
        assert uaur.dsTechnicalId == "UHJvY4VkdXKlLTI5NTgw"
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
        return_value=ds_fixtures.DS_RESPONSE_LOST_CREDENTIALS,
    )
    def test_lost_credentials(self, mocked_get_applications, instructor):
        beneficiary = users_factories.UserFactory(email="jeune@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()
        assert uaur.dsApplicationId == 21176193
        assert uaur.dsTechnicalId == "UHJvY4VkdXKlLTI5NTgw"
        assert uaur.status == dms_models.GraphQLApplicationStates.draft
        assert uaur.dateCreated == datetime(2024, 11, 26, 15, 14, 14)
        assert uaur.dateLastStatusUpdate == uaur.dateCreated
        assert uaur.firstName == "Jeune"
        assert uaur.lastName == "En détresse"
        assert uaur.email == "jeune@example.com"
        assert uaur.birthDate == date(2006, 7, 6)
        assert uaur.user == beneficiary
        assert uaur.updateTypes == [users_models.UserAccountUpdateType.LOST_CREDENTIALS]
        assert uaur.oldEmail is None
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
        return_value=ds_fixtures.DS_RESPONSE_APPLIED_BY_PROXY,
    )
    def test_applied_by_proxy(self, mocked_get_applications, instructor):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="jeune@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()
        assert uaur.dsApplicationId == 21176997
        assert uaur.dsTechnicalId == "UHJvY4VkdXKlLTI5NTgw"
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
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()
        assert uaur.dsApplicationId == 21177744
        assert uaur.dsTechnicalId == "UHJvY4VkdXKlLTI5NTgw"
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
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()
        assert uaur.dsApplicationId == 21179224
        assert uaur.dsTechnicalId == "UHJvY4VkdXKlLTI5NTgw"
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

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "nouvelle.adresse@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.UPDATE_REQUEST_NO_USER_FOUND.value)
        assert mails_testing.outbox[0]["params"]["DS_APPLICATION_NUMBER"] == uaur.dsApplicationId

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_INVALID_VALUE,
    )
    def test_invalid_value(self, mocked_get_applications):
        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()
        assert uaur.dsApplicationId == 21193637
        assert uaur.dsTechnicalId == "UHJvY4VkdXKlLTI5NTgw"
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
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()
        assert uaur.dsApplicationId == 21163559
        assert uaur.flags == [users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL]

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_EMAIL_CHANGED,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_DRAFT_TO_ON_GOING,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_REFUSED,
        ],
    )
    def test_update_email_already_used(self, mocked_execute_query, instructor):
        users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com")
        users_factories.BeneficiaryGrant18Factory(email="nouvelle.adresse@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 3

        mocked_execute_query.call_args_list[0].assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        assert mocked_execute_query.call_args_list[1].args == (dms_api.MAKE_ON_GOING_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[2].args == (dms_api.MAKE_REFUSED_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[2].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": settings.DMS_INSTRUCTOR_ID,
                    "disableNotification": False,
                    "motivation": "Dossier rejeté car l'email est déjà utilisé par un compte crédité",
                }
            }
        }

        assert uaur.status == dms_models.GraphQLApplicationStates.refused
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "usager@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.UPDATE_REQUEST_ALREADY_USED_EMAIL.value)
        assert mails_testing.outbox[0]["params"]["DS_APPLICATION_NUMBER"] == uaur.dsApplicationId

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_EMAIL_CHANGED_DUPLICATE,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_DRAFT_TO_ON_GOING,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_REFUSED,
        ],
    )
    def test_update_email_duplicate(self, mocked_execute_query, instructor):
        users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com")

        users_ds.sync_user_account_update_requests(104118, None)

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 3

        mocked_execute_query.call_args_list[0].assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        assert mocked_execute_query.call_args_list[1].args == (dms_api.MAKE_ON_GOING_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[2].args == (dms_api.MAKE_REFUSED_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[2].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": settings.DMS_INSTRUCTOR_ID,
                    "disableNotification": False,
                    "motivation": "Dossier rejeté car le nouvel email et l'ancien sont identiques dans le formulaire",
                }
            }
        }

        assert uaur.status == dms_models.GraphQLApplicationStates.refused
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "usager@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.UPDATE_REQUEST_DUPLICATE_EMAIL.value)
        assert mails_testing.outbox[0]["params"]["DS_APPLICATION_NUMBER"] == uaur.dsApplicationId

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_PHONE_NUMBER_CHANGED,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_REFUSED,
        ],
    )
    def test_update_phone_number_already_used(self, mocked_execute_query, instructor):
        users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com")
        users_factories.BeneficiaryGrant18Factory(phoneNumber="+33610203040")

        users_ds.sync_user_account_update_requests(104118, None)

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 2

        mocked_execute_query.call_args_list[0].assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        assert mocked_execute_query.call_args_list[1].args == (dms_api.MAKE_REFUSED_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[1].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": settings.DMS_INSTRUCTOR_ID,
                    "disableNotification": False,
                    "motivation": "Dossier rejeté car le numéro de téléphone est déjà utilisé par un compte crédité",
                }
            }
        }

        assert uaur.status == dms_models.GraphQLApplicationStates.refused
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "beneficiaire@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(
            TransactionalEmail.UPDATE_REQUEST_ALREADY_USED_PHONE_NUMBER.value
        )
        assert mails_testing.outbox[0]["params"]["DS_APPLICATION_NUMBER"] == uaur.dsApplicationId

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_PHONE_NUMBER_CHANGED,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_REFUSED,
        ],
    )
    def test_update_phone_number_duplicate(self, mocked_execute_query, instructor):
        users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com", phoneNumber="+33610203040")

        users_ds.sync_user_account_update_requests(104118, None)

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 2

        mocked_execute_query.call_args_list[0].assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        assert mocked_execute_query.call_args_list[1].args == (dms_api.MAKE_REFUSED_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[1].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": settings.DMS_INSTRUCTOR_ID,
                    "disableNotification": False,
                    "motivation": "Dossier rejeté car le numéro de téléphone est déjà enregistré sur ton compte",
                }
            }
        }

        assert uaur.status == dms_models.GraphQLApplicationStates.refused
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "beneficiaire@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(
            TransactionalEmail.UPDATE_REQUEST_DUPLICATE_PHONE_NUMBER.value
        )
        assert mails_testing.outbox[0]["params"]["DS_APPLICATION_NUMBER"] == uaur.dsApplicationId

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_FIRSTNAME_CHANGED_DUPLICATE,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_REFUSED,
        ],
    )
    def test_update_first_name_duplicate(self, mocked_execute_query, instructor):
        users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com", firstName="Vieux")

        users_ds.sync_user_account_update_requests(104118, None)

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 2

        mocked_execute_query.call_args_list[0].assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )
        assert mocked_execute_query.call_args_list[1].args == (dms_api.MAKE_REFUSED_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[1].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": settings.DMS_INSTRUCTOR_ID,
                    "disableNotification": False,
                    "motivation": "Dossier rejeté car le prénom est déjà celui enregistré sur ton compte",
                }
            }
        }

        assert uaur.status == dms_models.GraphQLApplicationStates.refused
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "beneficiaire@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(
            TransactionalEmail.UPDATE_REQUEST_DUPLICATE_FULL_NAME.value
        )
        assert mails_testing.outbox[0]["params"]["DS_APPLICATION_NUMBER"] == uaur.dsApplicationId

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_FIRSTNAME_LASTNAME_CHANGED_DUPLICATE,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_REFUSED,
        ],
    )
    def test_update_full_name_duplicate(self, mocked_execute_query, instructor):
        users_factories.BeneficiaryGrant18Factory(
            email="beneficiaire@example.com", firstName="Vieux", lastName="Machin"
        )

        users_ds.sync_user_account_update_requests(104118, None)

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 2

        mocked_execute_query.call_args_list[0].assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )
        assert mocked_execute_query.call_args_list[1].args == (dms_api.MAKE_REFUSED_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[1].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": settings.DMS_INSTRUCTOR_ID,
                    "disableNotification": False,
                    "motivation": "Dossier rejeté car les nom et prénom sont déjà ceux enregistrés sur ton compte",
                }
            }
        }

        assert uaur.status == dms_models.GraphQLApplicationStates.refused
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == "beneficiaire@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(
            TransactionalEmail.UPDATE_REQUEST_DUPLICATE_FULL_NAME.value
        )
        assert mails_testing.outbox[0]["params"]["DS_APPLICATION_NUMBER"] == uaur.dsApplicationId

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_ARCHIVED,
    )
    def test_delete_archived(self, mocked_get_applications):
        users_factories.EmailUpdateRequestFactory(dsApplicationId=21168276)

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        assert db.session.query(users_models.UserAccountUpdateRequest).count() == 0

    @time_machine.travel("2025-01-16 17:12")
    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_FIRSTNAME_CHANGED_WITH_SET_WITHOUT_CONTINUATION,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_WITHOUT_CONTINUATION,
        ],
    )
    @pytest.mark.parametrize("with_found_user", [True, False])
    def test_sync_with_set_without_continuation(self, mocked_execute_query, instructor, with_found_user):
        if with_found_user:
            beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com")
        else:
            beneficiary = None

        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21163559,
            dsTechnicalId="UHJvY4VkdXKlLTI5NTgw",
            status=dms_models.GraphQLApplicationStates.on_going,
            user=beneficiary,
        )

        users_ds.sync_user_account_update_requests(104118, None, set_without_continuation=True)

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 2
        mocked_execute_query.call_args_list[0].assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        assert mocked_execute_query.call_args_list[1].args == (dms_api.MARK_WITHOUT_CONTINUATION_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[1].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": settings.DMS_INSTRUCTOR_ID,
                    "disableNotification": False,
                    "motivation": "Dossier classé sans suite car pas de correction apportée au dossier depuis 30 jours",
                }
            }
        }

        assert uaur.status == dms_models.GraphQLApplicationStates.without_continuation
        if with_found_user:
            assert len(mails_testing.outbox) == 1
            assert mails_testing.outbox[0]["To"] == "beneficiaire@example.com"
            assert mails_testing.outbox[0]["template"] == asdict(
                TransactionalEmail.UPDATE_REQUEST_MARKED_WITHOUT_CONTINUATION.value
            )
        else:
            assert len(mails_testing.outbox) == 2
            assert mails_testing.outbox[0]["To"] == "beneficiaire@example.com"
            assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.UPDATE_REQUEST_NO_USER_FOUND.value)
            assert mails_testing.outbox[0]["params"]["DS_APPLICATION_NUMBER"] == uaur.dsApplicationId
            assert mails_testing.outbox[1]["To"] == "beneficiaire@example.com"
            assert mails_testing.outbox[1]["template"] == asdict(
                TransactionalEmail.UPDATE_REQUEST_MARKED_WITHOUT_CONTINUATION.value
            )

    @time_machine.travel("2025-01-16 17:12")
    def test_sync_with_set_without_continuation_without_user_message(self, instructor):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com")

        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21163559,
            dsTechnicalId="UHJvY4VkdXKlLTI5NTgw",
            status=dms_models.GraphQLApplicationStates.on_going,
            user=beneficiary,
        )

        sync_response = copy.deepcopy(ds_fixtures.DS_RESPONSE_EMAIL_CHANGED_WITH_SET_WITHOUT_CONTINUATION)
        for message in sync_response["demarche"]["dossiers"]["nodes"][0]["messages"]:
            if message["email"] == sync_response["demarche"]["dossiers"]["nodes"][0]["usager"]["email"]:
                message["email"] = "not an email"  # "removes" the message

        with patch(
            "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
            side_effect=[
                sync_response,
                ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_WITHOUT_CONTINUATION,
            ],
        ) as mocked_execute_query:
            users_ds.sync_user_account_update_requests(104118, None, set_without_continuation=True)

            mocked_execute_query.assert_called()
            assert mocked_execute_query.call_count == 2
            mocked_execute_query.call_args_list[0].assert_called_once_with(
                dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
            )

            assert mocked_execute_query.call_args_list[1].args == (dms_api.MARK_WITHOUT_CONTINUATION_MUTATION_NAME,)
            assert mocked_execute_query.call_args_list[1].kwargs == {
                "variables": {
                    "input": {
                        "dossierId": uaur.dsTechnicalId,
                        "instructeurId": settings.DMS_INSTRUCTOR_ID,
                        "disableNotification": False,
                        "motivation": "Dossier classé sans suite car pas de correction apportée au dossier depuis 30 jours",
                    }
                }
            }

        assert uaur.status == dms_models.GraphQLApplicationStates.without_continuation
        assert len(mails_testing.outbox) == 2
        assert mails_testing.outbox[0]["To"] == "beneficiaire@example.com"
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.UPDATE_REQUEST_NO_USER_FOUND.value)
        assert mails_testing.outbox[0]["params"]["DS_APPLICATION_NUMBER"] == uaur.dsApplicationId
        assert mails_testing.outbox[1]["To"] == "nouvelle.adresse@example.com"
        assert mails_testing.outbox[1]["template"] == asdict(
            TransactionalEmail.UPDATE_REQUEST_MARKED_WITHOUT_CONTINUATION.value
        )

    @time_machine.travel("2025-01-16 17:12")
    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_EMAIL_CHANGED_FROM_DRAFT_WITH_SET_WITHOUT_CONTINUATION,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_DRAFT_TO_ON_GOING,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_WITHOUT_CONTINUATION,
        ],
    )
    def test_sync_from_draft_with_set_without_continuation(self, mocked_execute_query, instructor):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com")

        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21163559,
            dsTechnicalId="UHJvY4VkdXKlLTI5NTgw",
            status=dms_models.GraphQLApplicationStates.draft,
            user=beneficiary,
        )

        users_ds.sync_user_account_update_requests(104118, None, set_without_continuation=True)

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 3
        mocked_execute_query.call_args_list[0].assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        assert mocked_execute_query.call_args_list[1].args == (dms_api.MAKE_ON_GOING_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[1].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": settings.DMS_INSTRUCTOR_ID,
                    "disableNotification": True,
                }
            }
        }

        assert mocked_execute_query.call_args_list[2].args == (dms_api.MARK_WITHOUT_CONTINUATION_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[2].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": settings.DMS_INSTRUCTOR_ID,
                    "disableNotification": False,
                    "motivation": "Dossier classé sans suite car pas de correction apportée au dossier depuis 30 jours",
                }
            }
        }

        assert uaur.status == dms_models.GraphQLApplicationStates.without_continuation

    @time_machine.travel("2025-01-16 17:12")
    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_EMAIL_CHANGED_WITH_SET_WITHOUT_CONTINUATION,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_WITHOUT_CONTINUATION_TO_WITHOUT_CONTINUATION,
        ],
    )
    def test_sync_with_failed_set_without_continuation(self, mocked_execute_query, instructor):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com")

        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21163559,
            dsTechnicalId="UHJvY4VkdXKlLTI5NTgw",
            status=dms_models.GraphQLApplicationStates.on_going,
            user=beneficiary,
        )

        users_ds.sync_user_account_update_requests(104118, None, set_without_continuation=True)

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 2
        mocked_execute_query.call_args_list[0].assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        assert mocked_execute_query.call_args_list[1].args == (dms_api.MARK_WITHOUT_CONTINUATION_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[1].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": settings.DMS_INSTRUCTOR_ID,
                    "disableNotification": False,
                    "motivation": "Dossier classé sans suite car pas de correction apportée au dossier depuis 30 jours",
                }
            }
        }

        assert uaur.status == dms_models.GraphQLApplicationStates.on_going

    @time_machine.travel("2025-01-16 17:12")
    @pytest.mark.parametrize(
        "status,date_last_instructor_message,date_last_user_message,date_derniere_modification_champs",
        [
            (
                dms_models.GraphQLApplicationStates.refused,
                "2024-12-12T12:12:00+01:00",  # now - 35
                "2024-12-07T12:12:00+01:00",  # now - 40
                "2024-12-10T17:12:00+01:00",  # now - 37
            ),
            (
                dms_models.GraphQLApplicationStates.on_going,
                "2024-12-27T12:12:00+01:00",  # now - 20
                "2024-12-07T12:12:00+01:00",  # now - 40
                "2024-12-10T17:12:00+01:00",  # now - 37
            ),
            (
                dms_models.GraphQLApplicationStates.on_going,
                "2024-12-12T12:12:00+01:00",  # now - 35
                "2024-12-13T12:12:00+01:00",  # now - 34
                "2024-12-10T17:12:00+01:00",  # now - 37
            ),
            (
                dms_models.GraphQLApplicationStates.on_going,
                "2024-12-12T12:12:00+01:00",  # now - 35
                "2024-12-07T12:12:00+01:00",  # now - 40
                "2024-12-13T17:12:00+01:00",  # now - 34
            ),
            (
                dms_models.GraphQLApplicationStates.on_going,
                None,
                "2024-12-07T12:12:00+01:00",  # now - 40
                "2024-12-10T17:12:00+01:00",  # now - 37
            ),
            (
                dms_models.GraphQLApplicationStates.on_going,
                "2024-12-12T12:12:00+01:00",  # now - 35
                None,
                "2024-12-13T17:12:00+01:00",  # now - 34
            ),
        ],
    )
    def test_sync_unconcerned_by_set_without_continuation(
        self,
        status,
        date_last_instructor_message,
        date_last_user_message,
        date_derniere_modification_champs,
        instructor,
    ):
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="beneficiaire@example.com")

        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21163559, dsTechnicalId="UHJvY4VkdXKlLTI5NTgw", status=status, user=beneficiary
        )
        return_value = copy.deepcopy(ds_fixtures.DS_RESPONSE_EMAIL_CHANGED_WITH_SET_WITHOUT_CONTINUATION)
        return_value["demarche"]["dossiers"]["nodes"][0]["state"] = status.value
        return_value["demarche"]["dossiers"]["nodes"][0]["dateDerniereModificationChamps"] = (
            date_derniere_modification_champs
        )
        for message in return_value["demarche"]["dossiers"]["nodes"][0]["messages"]:
            if message["email"] == beneficiary.email:
                if date_last_user_message is None:
                    message["email"] = None  # "removes" the message
                else:
                    message["createdAt"] = date_last_user_message
            elif message["email"] == instructor.email:
                if date_last_instructor_message is None:
                    message["email"] = None  # "removes" the message
                else:
                    message["createdAt"] = date_last_instructor_message

        with patch(
            "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
            return_value=return_value,
        ) as mocked_execute_query:
            users_ds.sync_user_account_update_requests(104118, None, set_without_continuation=True)

            mocked_execute_query.assert_called_once_with(
                dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
            )

        assert uaur.status == status

    @pytest.mark.parametrize("requester_user_exists", [True, False])
    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_CORRECTION_RESOLVED,
    )
    def test_update_data_when_user_has_been_set_manually(self, mocked_get_applications, requester_user_exists):
        if requester_user_exists:
            users_factories.BeneficiaryGrant18Factory(email="jeune@example.com")
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="selectionne@example.com")
        users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21177744,
            dsTechnicalId="UHJvY4VkdXKlLTI5NTgw",
            status=dms_models.GraphQLApplicationStates.on_going,
            user=beneficiary,
            flags=[users_models.UserAccountUpdateFlag.USER_SET_MANUALLY],
        )

        users_ds.sync_user_account_update_requests(104118, None)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_ACCOUNT_UPDATE_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        uaur: users_models.UserAccountUpdateRequest = db.session.query(users_models.UserAccountUpdateRequest).one()
        assert uaur.dsApplicationId == 21177744
        assert uaur.dsTechnicalId == "UHJvY4VkdXKlLTI5NTgw"
        assert uaur.firstName == "Jeune"
        assert uaur.lastName == "Bénéficiaire"
        assert uaur.email == "beneficiaire@example.com"
        assert uaur.user == beneficiary
        assert set(uaur.flags) == {
            users_models.UserAccountUpdateFlag.USER_SET_MANUALLY,
            users_models.UserAccountUpdateFlag.CORRECTION_RESOLVED,
        }


class SyncDeletedUserAccountUpdateRequestsTest:
    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_DELETED_APPLICATIONS,
    )
    def test_delete_update_requests(self, mocked_get_applications):
        users_factories.EmailUpdateRequestFactory(dsApplicationId=10000001)
        users_factories.EmailUpdateRequestFactory(dsApplicationId=10000002)
        users_factories.EmailUpdateRequestFactory(dsApplicationId=10000003)

        users_ds.sync_deleted_user_account_update_requests(104118)

        mocked_get_applications.assert_called_once_with(
            dms_api.GET_DELETED_APPLICATIONS_QUERY_NAME, variables={"demarcheNumber": 104118}
        )

        remaining_requests = db.session.query(users_models.UserAccountUpdateRequest).all()
        assert len(remaining_requests) == 1
        assert remaining_requests[0].dsApplicationId == 10000002


class UpdateStateTest:
    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_UPDATE_STATE_DRAFT_TO_ON_GOING,
    )
    def test_from_draft_to_on_going(self, mocked_update_state, instructor):
        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21163559,
            dsTechnicalId="UHJvY4VkdXKlLTI5NTgw",
            status=dms_models.GraphQLApplicationStates.draft,
        )

        users_ds.update_state(uaur, new_state=dms_models.GraphQLApplicationStates.on_going, instructor=instructor)

        mocked_update_state.assert_called_once_with(
            dms_api.MAKE_ON_GOING_MUTATION_NAME,
            variables={
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": instructor.backoffice_profile.dsInstructorId,
                    "disableNotification": False,
                }
            },
        )

        db.session.refresh(uaur)
        assert uaur.status == dms_models.GraphQLApplicationStates.on_going
        assert uaur.dateCreated == datetime(2024, 12, 2, 17, 16, 50)
        assert uaur.dateLastStatusUpdate == datetime(2024, 12, 2, 17, 20, 53)
        assert uaur.lastInstructor == instructor

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_ON_GOING,
    )
    def test_from_remote_on_going_to_on_going(self, mocked_update_state, instructor):
        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21163559,
            dsTechnicalId="UHJvY4VkdXKlLTI5NTgw",
            status=dms_models.GraphQLApplicationStates.on_going,
        )

        with pytest.raises(dms_exceptions.DmsGraphQLApiError) as error:
            users_ds.update_state(uaur, new_state=dms_models.GraphQLApplicationStates.on_going, instructor=instructor)

        mocked_update_state.assert_called_once_with(
            dms_api.MAKE_ON_GOING_MUTATION_NAME,
            variables={
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": instructor.backoffice_profile.dsInstructorId,
                    "disableNotification": False,
                }
            },
        )

        assert error.value.message == "Le dossier est déjà en instruction"
        assert uaur.lastInstructor != instructor

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_ACCEPTED,
    )
    def test_from_on_going_to_accepted(self, mocked_update_state, instructor):
        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21268381,
            dsTechnicalId="UHJvY4VkdXKlLTI5NTgw",
            status=dms_models.GraphQLApplicationStates.on_going,
        )

        users_ds.update_state(
            uaur, new_state=dms_models.GraphQLApplicationStates.accepted, instructor=instructor, motivation="Test"
        )

        mocked_update_state.assert_called_once_with(
            dms_api.MAKE_ACCEPTED_MUTATION_NAME,
            variables={
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": instructor.backoffice_profile.dsInstructorId,
                    "motivation": "Test",
                    "disableNotification": False,
                }
            },
        )

        db.session.refresh(uaur)
        assert uaur.status == dms_models.GraphQLApplicationStates.accepted
        assert uaur.dateCreated == datetime(2024, 12, 2, 14, 37, 29)
        assert uaur.dateLastStatusUpdate == datetime(2024, 12, 5, 11, 17, 10)
        assert uaur.lastInstructor == instructor

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_DRAFT_TO_ON_GOING,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_ACCEPTED,
        ],
    )
    def test_from_draft_to_accepted(self, mocked_execute_query, instructor):
        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21273773,
            dsTechnicalId="UHJvY4VkdXKlLTI5NTgw",
            status=dms_models.GraphQLApplicationStates.draft,
        )

        users_ds.update_state(uaur, new_state=dms_models.GraphQLApplicationStates.accepted, instructor=instructor)

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 2

        assert mocked_execute_query.call_args_list[0].args == (dms_api.MAKE_ON_GOING_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[0].kwargs["variables"] == {
            "input": {
                "dossierId": uaur.dsTechnicalId,
                "instructeurId": instructor.backoffice_profile.dsInstructorId,
                "disableNotification": True,
            }
        }

        assert mocked_execute_query.call_args_list[1].args == (dms_api.MAKE_ACCEPTED_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[1].kwargs["variables"] == {
            "input": {
                "dossierId": uaur.dsTechnicalId,
                "instructeurId": instructor.backoffice_profile.dsInstructorId,
                "disableNotification": False,
            }
        }

        db.session.refresh(uaur)
        assert uaur.status == dms_models.GraphQLApplicationStates.accepted
        assert uaur.lastInstructor == instructor

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_UPDATE_STATE_ACCEPTED_TO_ACCEPTED,
    )
    def test_from_accepted_to_accepted(self, mocked_update_state, instructor):
        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21273773,
            dsTechnicalId="RG9zc2llci0yMTI3Mzc3Mw==",
            status=dms_models.GraphQLApplicationStates.accepted,
        )

        with pytest.raises(dms_exceptions.DmsGraphQLApiError) as error:
            users_ds.update_state(uaur, new_state=dms_models.GraphQLApplicationStates.accepted, instructor=instructor)

        mocked_update_state.assert_called_once_with(
            dms_api.MAKE_ACCEPTED_MUTATION_NAME,
            variables={
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": instructor.backoffice_profile.dsInstructorId,
                    "disableNotification": False,
                }
            },
        )

        assert error.value.message == "Le dossier est déjà accepté"
        assert uaur.lastInstructor != instructor

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_WITHOUT_CONTINUATION,
    )
    def test_from_remote_on_going_to_without_continuation(self, mocked_update_state, instructor):
        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21163559,
            dsTechnicalId="UHJvY4VkdXKlLTI5NTgw",
            status=dms_models.GraphQLApplicationStates.on_going,
        )

        users_ds.update_state(
            uaur,
            new_state=dms_models.GraphQLApplicationStates.without_continuation,
            instructor=instructor,
            motivation="Test",
        )

        mocked_update_state.assert_called_once_with(
            dms_api.MARK_WITHOUT_CONTINUATION_MUTATION_NAME,
            variables={
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": instructor.backoffice_profile.dsInstructorId,
                    "disableNotification": False,
                    "motivation": "Test",
                }
            },
        )

        db.session.refresh(uaur)
        assert uaur.status == dms_models.GraphQLApplicationStates.without_continuation
        assert uaur.dateCreated == datetime(2025, 1, 15, 15, 28, 45)
        assert uaur.dateLastStatusUpdate == datetime(2025, 1, 15, 16, 54, 59)
        assert uaur.lastInstructor == instructor

    @pytest.mark.parametrize(
        "status,return_value,expected_error",
        [
            (
                dms_models.GraphQLApplicationStates.accepted,
                ds_fixtures.DS_RESPONSE_UPDATE_STATE_ACCEPTED_TO_WITHOUT_CONTINUATION,
                "Le dossier est déjà accepté",
            ),
            (
                dms_models.GraphQLApplicationStates.refused,
                ds_fixtures.DS_RESPONSE_UPDATE_STATE_REFUSED_TO_WITHOUT_CONTINUATION,
                "Le dossier est déjà refusé",
            ),
        ],
    )
    def test_from_remote_invalid_state_to_without_continuation(self, instructor, status, return_value, expected_error):
        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21163559,
            dsTechnicalId="UHJvY4VkdXKlLTI5NTgw",
            status=status,
        )

        with patch(
            "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
            return_value=return_value,
        ) as mocked_update_state:
            with pytest.raises(dms_exceptions.DmsGraphQLApiError) as error:
                users_ds.update_state(
                    uaur,
                    new_state=dms_models.GraphQLApplicationStates.without_continuation,
                    instructor=instructor,
                    motivation="Test",
                )

            mocked_update_state.assert_called_once_with(
                dms_api.MARK_WITHOUT_CONTINUATION_MUTATION_NAME,
                variables={
                    "input": {
                        "dossierId": uaur.dsTechnicalId,
                        "instructeurId": instructor.backoffice_profile.dsInstructorId,
                        "disableNotification": False,
                        "motivation": "Test",
                    }
                },
            )

        assert error.value.message == expected_error
        assert uaur.lastInstructor != instructor


class ArchiveTest:
    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_ARCHIVE,
    )
    def test_archive_accepted(self, mocked_execute_query, instructor):
        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21835749,
            dsTechnicalId="RG9zc2llci0yMTgzNTc0OQ==",
            status=dms_models.GraphQLApplicationStates.accepted,
        )
        other_uaur = users_factories.EmailUpdateRequestFactory()

        users_ds.archive(uaur, motivation="Test")

        mocked_execute_query.assert_called_once_with(
            dms_api.ARCHIVE_APPLICATION_QUERY_NAME,
            variables={
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": pcapi_settings.DMS_INSTRUCTOR_ID,
                }
            },
        )

        assert db.session.query(users_models.UserAccountUpdateRequest).one() == other_uaur

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_WITHOUT_CONTINUATION,
            ds_fixtures.DS_RESPONSE_ARCHIVE,
        ],
    )
    def test_archive_on_going(self, mocked_execute_query, instructor):
        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21835749,
            dsTechnicalId="RG9zc2llci0yMTgzNTc0OQ==",
            status=dms_models.GraphQLApplicationStates.on_going,
        )

        users_ds.archive(uaur, motivation="Test")

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 2
        assert mocked_execute_query.call_args_list[0].args == (dms_api.MARK_WITHOUT_CONTINUATION_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[0].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": pcapi_settings.DMS_INSTRUCTOR_ID,
                    "motivation": "Test",
                    "disableNotification": True,
                }
            }
        }
        assert mocked_execute_query.call_args_list[1].args == (dms_api.ARCHIVE_APPLICATION_QUERY_NAME,)
        assert mocked_execute_query.call_args_list[1].kwargs == {
            "variables": {"input": {"dossierId": uaur.dsTechnicalId, "instructeurId": pcapi_settings.DMS_INSTRUCTOR_ID}}
        }

        assert db.session.query(users_models.UserAccountUpdateRequest).count() == 0

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        side_effect=[
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_DRAFT_TO_ON_GOING,
            ds_fixtures.DS_RESPONSE_UPDATE_STATE_ON_GOING_TO_WITHOUT_CONTINUATION,
            ds_fixtures.DS_RESPONSE_ARCHIVE,
        ],
    )
    def test_archive_draft(self, mocked_execute_query, instructor):
        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21835749,
            dsTechnicalId="RG9zc2llci0yMTgzNTc0OQ==",
            status=dms_models.GraphQLApplicationStates.draft,
        )

        users_ds.archive(uaur, motivation="Test")

        mocked_execute_query.assert_called()
        assert mocked_execute_query.call_count == 3
        assert mocked_execute_query.call_args_list[0].args == (dms_api.MAKE_ON_GOING_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[0].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": pcapi_settings.DMS_INSTRUCTOR_ID,
                    "disableNotification": True,
                }
            }
        }
        assert mocked_execute_query.call_args_list[1].args == (dms_api.MARK_WITHOUT_CONTINUATION_MUTATION_NAME,)
        assert mocked_execute_query.call_args_list[1].kwargs == {
            "variables": {
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": pcapi_settings.DMS_INSTRUCTOR_ID,
                    "motivation": "Test",
                    "disableNotification": True,
                }
            }
        }
        assert mocked_execute_query.call_args_list[2].args == (dms_api.ARCHIVE_APPLICATION_QUERY_NAME,)
        assert mocked_execute_query.call_args_list[2].kwargs == {
            "variables": {"input": {"dossierId": uaur.dsTechnicalId, "instructeurId": pcapi_settings.DMS_INSTRUCTOR_ID}}
        }

        assert db.session.query(users_models.UserAccountUpdateRequest).count() == 0

    @patch(
        "pcapi.connectors.dms.api.DMSGraphQLClient.execute_query",
        return_value=ds_fixtures.DS_RESPONSE_ARCHIVE_ERROR_NOT_INSTRUCTED,
    )
    def test_archive_error_not_instructed(self, mocked_execute_query, instructor):
        uaur = users_factories.EmailUpdateRequestFactory(
            dsApplicationId=21835749,
            dsTechnicalId="RG9zc2llci0yMTgzNTc0OQ==",
            status=dms_models.GraphQLApplicationStates.accepted,  # wrong status in database
        )

        with pytest.raises(dms_exceptions.DmsGraphQLApiError) as error:
            users_ds.archive(uaur, motivation="Test")

        mocked_execute_query.assert_called_once_with(
            dms_api.ARCHIVE_APPLICATION_QUERY_NAME,
            variables={
                "input": {
                    "dossierId": uaur.dsTechnicalId,
                    "instructeurId": pcapi_settings.DMS_INSTRUCTOR_ID,
                }
            },
        )

        assert (
            error.value.message
            == "Un dossier ne peut être déplacé dans « à archiver » qu’une fois le traitement terminé"
        )
        assert db.session.query(users_models.UserAccountUpdateRequest).count() == 1
