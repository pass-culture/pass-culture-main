from datetime import date
from datetime import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest
from sib_api_v3_sdk import RemoveContactFromList
from sib_api_v3_sdk import RequestContactImport

from pcapi import settings
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.users.external import user_automations
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole


@pytest.mark.usefixtures("db_session")
class UserAutomationsTest:
    def _create_users_around_18(self):
        today = datetime.combine(date.today(), datetime.min.time())

        users_factories.BeneficiaryGrant18Factory(
            email="marc+test@example.net",
            dateOfBirth=today - relativedelta(days=user_automations.DAYS_IN_18_YEARS - 29),
        )
        users_factories.BeneficiaryGrant18Factory(
            email="fabien+test@example.net",
            dateOfBirth=today - relativedelta(days=user_automations.DAYS_IN_18_YEARS - 30),
        )
        users_factories.BeneficiaryGrant18Factory(
            email="daniel+test@example.net",
            dateOfBirth=today - relativedelta(days=user_automations.DAYS_IN_18_YEARS - 31),
        )
        users_factories.UserFactory(email="bernard+test@example.net", dateOfBirth=today - relativedelta(years=20))
        users_factories.ProFactory(
            email="pro+test@example.net", dateOfBirth=today - relativedelta(days=user_automations.DAYS_IN_18_YEARS - 30)
        )
        users_factories.UnderageBeneficiaryFactory(
            email="gerard+test@example.net",
            dateOfBirth=today - relativedelta(days=user_automations.DAYS_IN_18_YEARS - 30),
        )

    @freeze_time("2021-08-01 10:00:00")
    def test_get_emails_who_will_turn_eighteen_in_one_month(self):
        self._create_users_around_18()

        result = user_automations.get_emails_who_will_turn_eighteen_in_one_month()
        assert sorted(result) == ["fabien+test@example.net", "gerard+test@example.net"]
        assert len(User.query.all()) == 6

    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.process_api.ProcessApi.get_process")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.remove_contact_from_list")
    def test_user_turned_eighteen_automation(
        self, mock_remove_contact_from_list, mock_import_contacts, mock_get_process
    ):
        self._create_users_around_18()

        result = user_automations.users_turned_eighteen_automation()

        mock_remove_contact_from_list.assert_called_once_with(
            settings.SENDINBLUE_AUTOMATION_YOUNG_18_IN_1_MONTH_LIST_ID,
            RemoveContactFromList(emails=None, ids=None, all=True),
        )

        mock_import_contacts.assert_called_once()
        assert mock_import_contacts.call_args.args[0].file_url == None
        assert mock_import_contacts.call_args.args[0].file_body in (
            "EMAIL\nfabien+test@example.net\ngerard+test@example.net",
            "EMAIL\ngerard+test@example.net\nfabien+test@example.net",
        )
        assert mock_import_contacts.call_args.args[0].list_ids == [
            settings.SENDINBLUE_AUTOMATION_YOUNG_18_IN_1_MONTH_LIST_ID
        ]
        assert mock_import_contacts.call_args.args[0].notify_url == None
        assert mock_import_contacts.call_args.args[0].new_list == None
        assert mock_import_contacts.call_args.args[0].email_blacklist == False
        assert mock_import_contacts.call_args.args[0].sms_blacklist == False
        assert mock_import_contacts.call_args.args[0].update_existing_contacts == True
        assert mock_import_contacts.call_args.args[0].empty_contacts_attributes == False

        mock_get_process.assert_called()

        assert result is True

    def _create_users_with_deposits(self):
        with freeze_time("2020-11-15 15:00:00"):
            user0 = users_factories.UserFactory(
                email="beneficiary0+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=17, days=5),
                roles=[UserRole.UNDERAGE_BENEFICIARY],
            )
            assert user0.deposit is None

        with freeze_time("2020-10-31 15:00:00"):
            user1 = users_factories.BeneficiaryGrant18Factory(
                email="beneficiary1+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=1),
            )
            assert user1.deposit.expirationDate == datetime(2022, 10, 31, 15, 0, 0)

        with freeze_time("2020-11-01 15:00:00"):
            user2 = users_factories.BeneficiaryGrant18Factory(
                email="beneficiary2+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=2),
            )
            assert user2.deposit.expirationDate == datetime(2022, 11, 1, 15, 0, 0)
            bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user2, quantity=1, amount=10)
            assert user2.real_wallet_balance > 0

        with freeze_time("2020-12-01 15:00:00"):
            user3 = users_factories.BeneficiaryGrant18Factory(
                email="beneficiary3+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=3),
            )
            assert user3.deposit.expirationDate == datetime(2022, 12, 1, 15, 0, 0)

        with freeze_time("2021-01-30 15:00:00"):
            user4 = users_factories.BeneficiaryGrant18Factory(
                email="beneficiary4+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=4),
            )
            assert user4.deposit.expirationDate == datetime(2023, 1, 30, 15, 0, 0)

        with freeze_time("2021-01-31 15:00:00"):
            user5 = users_factories.BeneficiaryGrant18Factory(
                email="beneficiary5+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=5),
            )
            assert user5.deposit.expirationDate == datetime(2023, 1, 31, 15, 0, 0)

        with freeze_time("2021-03-10 15:00:00"):
            user6 = users_factories.BeneficiaryGrant18Factory(
                email="beneficiary6+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=5),
            )
            assert user6.deposit.expirationDate == datetime(2023, 3, 10, 15, 0, 0)

        with freeze_time("2021-05-01 17:00:00"):
            # user6 becomes ex-beneficiary
            bookings_factories.UsedIndividualBookingFactory(
                individualBooking__user=user6, quantity=1, amount=int(user6.real_wallet_balance)
            )
            assert user6.real_wallet_balance == 0

        return [user0, user1, user2, user3, user4, user5, user6]

    def test_get_users_beneficiary_three_months_before_credit_expiration(self):
        users = self._create_users_with_deposits()

        with freeze_time("2022-10-31 16:00:00"):
            results = user_automations.get_users_beneficiary_credit_expiration_within_next_3_months()
            assert sorted([user.email for user in results]) == [user.email for user in users[1:4]]

        with freeze_time("2022-11-01 14:00:00"):
            results = user_automations.get_users_beneficiary_credit_expiration_within_next_3_months()
            assert sorted([user.email for user in results]) == [user.email for user in users[2:5]]

        with freeze_time("2022-11-02 12:00:00"):
            results = user_automations.get_users_beneficiary_credit_expiration_within_next_3_months()
            assert sorted([user.email for user in results]) == [user.email for user in users[3:6]]

        with freeze_time("2023-01-15 08:00:00"):
            results = user_automations.get_users_beneficiary_credit_expiration_within_next_3_months()
            assert sorted([user.email for user in results]) == [user.email for user in users[4:7]]

    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.process_api.ProcessApi.get_process")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.remove_contact_from_list")
    def test_users_beneficiary_credit_expiration_within_next_3_months_automation(
        self, mock_remove_contact_from_list, mock_import_contacts, mock_get_process
    ):
        users = self._create_users_with_deposits()

        with freeze_time("2022-11-01 16:00:00"):
            result = user_automations.users_beneficiary_credit_expiration_within_next_3_months_automation()

        mock_remove_contact_from_list.assert_called_once_with(
            settings.SENDINBLUE_AUTOMATION_YOUNG_EXPIRATION_M3_ID,
            RemoveContactFromList(emails=None, ids=None, all=True),
        )

        mock_import_contacts.assert_called_once()

        request_contact_import = mock_import_contacts.call_args[0][0]
        body_lines = request_contact_import.file_body.split("\n")

        assert isinstance(request_contact_import, RequestContactImport)
        assert request_contact_import.file_url == None
        assert len(body_lines) == 4
        assert body_lines[0] == "EMAIL"
        assert set(body_lines[1:]) == {users[2].email, users[3].email, users[4].email}
        assert request_contact_import.list_ids == [settings.SENDINBLUE_AUTOMATION_YOUNG_EXPIRATION_M3_ID]
        assert request_contact_import.notify_url == None
        assert request_contact_import.new_list == None
        assert request_contact_import.email_blacklist == False
        assert request_contact_import.sms_blacklist == False
        assert request_contact_import.update_existing_contacts == True
        assert request_contact_import.empty_contacts_attributes == False

        mock_get_process.assert_called()

        assert result is True

    def test_get_users_ex_beneficiary(self):
        users = self._create_users_with_deposits()

        with freeze_time("2022-12-01 16:00:00"):
            results = user_automations.get_users_ex_beneficiary()
            assert sorted([user.email for user in results]) == [user.email for user in users[1:3] + [users[6]]]

        with freeze_time("2022-12-02 16:00:00"):
            results = user_automations.get_users_ex_beneficiary()
            assert sorted([user.email for user in results]) == [user.email for user in users[1:4] + [users[6]]]

    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.process_api.ProcessApi.get_process")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.remove_contact_from_list")
    def test_user_ex_beneficiary_automation(
        self, mock_remove_contact_from_list, mock_import_contacts, mock_get_process
    ):
        users = self._create_users_with_deposits()

        with freeze_time("2022-12-01 16:00:00"):
            result = user_automations.users_ex_beneficiary_automation()

        mock_remove_contact_from_list.assert_not_called()

        mock_import_contacts.assert_called_once()
        assert mock_import_contacts.call_args.args[0].file_url is None
        assert set(mock_import_contacts.call_args.args[0].file_body.split("\n")) == {
            "EMAIL",
            users[1].email,
            users[2].email,
            users[6].email,
        }
        assert mock_import_contacts.call_args.args[0].list_ids == [
            settings.SENDINBLUE_AUTOMATION_YOUNG_EX_BENEFICIARY_ID
        ]
        assert mock_import_contacts.call_args.args[0].notify_url == None
        assert mock_import_contacts.call_args.args[0].new_list == None
        assert mock_import_contacts.call_args.args[0].sms_blacklist == False
        assert mock_import_contacts.call_args.args[0].update_existing_contacts == True
        assert mock_import_contacts.call_args.args[0].empty_contacts_attributes == False

        mock_get_process.assert_called()

        assert result is True

    def test_get_email_for_inactive_user_since_thirty_days(self):
        with freeze_time("2021-08-01 15:00:00") as frozen_time:
            beneficiary = users_factories.BeneficiaryGrant18Factory(
                email="fabien+test@example.net", lastConnectionDate=datetime(2021, 8, 1)
            )
            not_beneficiary = users_factories.UserFactory(
                email="marc+test@example.net", lastConnectionDate=datetime(2021, 8, 2)
            )
            users_factories.ProFactory(email="pierre+test@example.net", lastConnectionDate=datetime(2021, 8, 1))
            users_factories.UserFactory(email="daniel+test@example.net", lastConnectionDate=datetime(2021, 8, 3))
            users_factories.UserFactory(email="billy+test@example.net", dateCreated=datetime(2021, 7, 31))
            users_factories.UserFactory(email="gerard+test@example.net", dateCreated=datetime(2021, 9, 1))

            frozen_time.move_to("2021-09-01 15:00:01")
            results = user_automations.get_email_for_inactive_user_since_thirty_days()
            assert sorted(results) == sorted([beneficiary.email, not_beneficiary.email])

    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.process_api.ProcessApi.get_process")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.remove_contact_from_list")
    def test_users_inactive_since_30_days_automation(
        self, mock_remove_contact_from_list, mock_import_contacts, mock_get_process
    ):
        with freeze_time("2021-08-01 15:00:00") as frozen_time:
            users_factories.BeneficiaryGrant18Factory(
                email="fabien+test@example.net", lastConnectionDate=datetime(2021, 8, 1)
            )
            users_factories.ProFactory(email="pierre+test@example.net", lastConnectionDate=datetime(2021, 8, 1))
            users_factories.UserFactory(email="daniel+test@example.net", lastConnectionDate=datetime(2021, 8, 4))
            users_factories.UserFactory(email="billy+test@example.net", dateCreated=datetime(2021, 7, 31))
            users_factories.UserFactory(email="gerard+test@example.net", dateCreated=datetime(2021, 9, 1))

            frozen_time.move_to("2021-09-02 15:00:01")

            result = user_automations.users_inactive_since_30_days_automation()

            mock_remove_contact_from_list.assert_called_once_with(
                settings.SENDINBLUE_AUTOMATION_YOUNG_INACTIVE_30_DAYS_LIST_ID,
                RemoveContactFromList(emails=None, ids=None, all=True),
            )

            mock_import_contacts.assert_called_once_with(
                RequestContactImport(
                    file_url=None,
                    file_body="EMAIL\nfabien+test@example.net",
                    list_ids=[settings.SENDINBLUE_AUTOMATION_YOUNG_INACTIVE_30_DAYS_LIST_ID],
                    notify_url=None,
                    new_list=None,
                    email_blacklist=False,
                    sms_blacklist=False,
                    update_existing_contacts=True,
                    empty_contacts_attributes=False,
                )
            )

            mock_get_process.assert_called()

            assert result is True

    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.process_api.ProcessApi.get_process")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.remove_contact_from_list")
    def test_users_inactive_since_30_days_automation_no_result(
        self, mock_remove_contact_from_list, mock_import_contacts, mock_get_process
    ):
        with freeze_time("2021-08-01 15:00:00") as frozen_time:
            users_factories.BeneficiaryGrant18Factory(
                email="fabien+test@example.net", lastConnectionDate=datetime(2021, 8, 1)
            )
            users_factories.UserFactory(email="marc+test@example.net", lastConnectionDate=datetime(2021, 8, 1))
            users_factories.UserFactory(email="daniel+test@example.net", lastConnectionDate=datetime(2021, 8, 2))
            users_factories.UserFactory(email="billy+test@example.net", dateCreated=datetime(2021, 7, 31))
            users_factories.UserFactory(email="gerard+test@example.net", dateCreated=datetime(2021, 9, 1))

            frozen_time.move_to("2021-08-30 15:00:01")

            result = user_automations.users_inactive_since_30_days_automation()

            mock_remove_contact_from_list.assert_called_once_with(
                settings.SENDINBLUE_AUTOMATION_YOUNG_INACTIVE_30_DAYS_LIST_ID,
                RemoveContactFromList(emails=None, ids=None, all=True),
            )

            mock_import_contacts.assert_not_called()
            mock_get_process.assert_called()

            assert result is True

    def test_get_email_for_users_created_one_year_ago_per_month(self):
        matching_users = []

        users_factories.UserFactory(email="fabien+test@example.net", dateCreated=datetime(2021, 7, 31))
        matching_users.append(
            users_factories.UserFactory(email="pierre+test@example.net", dateCreated=datetime(2021, 8, 1))
        )
        matching_users.append(
            users_factories.UserFactory(email="marc+test@example.net", dateCreated=datetime(2021, 8, 10))
        )
        matching_users.append(
            users_factories.UserFactory(email="daniel+test@example.net", dateCreated=datetime(2021, 8, 31))
        )
        users_factories.UserFactory(email="billy+test@example.net", dateCreated=datetime(2021, 9, 1))
        users_factories.UserFactory(email="gerard+test@example.net", dateCreated=datetime(2021, 9, 21))

        # matching: from 2021-08-01 to 2021-08-31
        with freeze_time("2022-08-10 15:00:00"):
            results = user_automations.get_email_for_users_created_one_year_ago_per_month()
            assert sorted(results) == sorted([user.email for user in matching_users])

    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.process_api.ProcessApi.get_process")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.remove_contact_from_list")
    def test_users_nearly_one_year_with_pass_automation(
        self, mock_remove_contact_from_list, mock_import_contacts, mock_get_process
    ):
        users_factories.UserFactory(email="fabien+test@example.net", dateCreated=datetime(2021, 8, 31))
        users_factories.UserFactory(email="pierre+test@example.net", dateCreated=datetime(2021, 9, 1))
        users_factories.UserFactory(email="daniel+test@example.net", dateCreated=datetime(2021, 10, 1))
        users_factories.UserFactory(email="gerard+test@example.net", dateCreated=datetime(2021, 10, 31))

        # matching: from 2021-09-01 to 2021-09-31
        with freeze_time("2022-09-10 15:00:00"):
            result = user_automations.users_one_year_with_pass_automation()

        mock_remove_contact_from_list.assert_called_once_with(
            settings.SENDINBLUE_AUTOMATION_YOUNG_1_YEAR_WITH_PASS_LIST_ID,
            RemoveContactFromList(emails=None, ids=None, all=True),
        )

        mock_import_contacts.assert_called_once_with(
            RequestContactImport(
                file_url=None,
                file_body="EMAIL\npierre+test@example.net",
                list_ids=[settings.SENDINBLUE_AUTOMATION_YOUNG_1_YEAR_WITH_PASS_LIST_ID],
                notify_url=None,
                new_list=None,
                email_blacklist=False,
                sms_blacklist=False,
                update_existing_contacts=True,
                empty_contacts_attributes=False,
            )
        )

        mock_get_process.assert_called()

        assert result is True

    def test_get_users_whose_credit_expired_today(self):
        users = self._create_users_with_deposits()

        with freeze_time("2022-11-01 05:00:00"):
            results = list(user_automations.get_users_whose_credit_expired_today())
            assert results == [users[1]]

        with freeze_time("2022-11-02 05:00:00"):
            results = list(user_automations.get_users_whose_credit_expired_today())
            assert results == [users[2]]

    @patch("pcapi.core.users.external.update_batch_user")
    @patch("pcapi.core.users.external.update_sendinblue_user")
    def test_users_whose_credit_expired_today_automation(self, mock_update_sendinblue, mock_update_batch):
        users = self._create_users_with_deposits()

        with freeze_time("2022-11-02 05:00:00"):
            user_automations.users_whose_credit_expired_today_automation()

        mock_update_sendinblue.assert_called_once()
        mock_update_batch.assert_called_once()

        assert mock_update_sendinblue.call_args.args[0] == users[2].email
        assert mock_update_sendinblue.call_args.args[1].is_former_beneficiary is True

        assert mock_update_batch.call_args.args[0] == users[2].id
        assert mock_update_batch.call_args.args[1].is_former_beneficiary is True

    def test_get_ex_underage_beneficiaries_who_can_no_longer_recredit(self):
        with freeze_time("2021-09-10 15:00:00"):
            user = users_factories.UnderageBeneficiaryFactory(
                email="underage+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=17, months=1),
            )
            assert user.deposit.expirationDate == datetime(2022, 8, 10)  # at birthday

        with freeze_time("2022-08-10 05:00:00"):
            results = list(user_automations.get_ex_underage_beneficiaries_who_can_no_longer_recredit())
            assert not results

        with freeze_time("2023-08-10 05:00:00"):
            results = list(user_automations.get_ex_underage_beneficiaries_who_can_no_longer_recredit())
            assert not results

        with freeze_time("2023-08-11 05:00:00"):
            results = list(user_automations.get_ex_underage_beneficiaries_who_can_no_longer_recredit())
            assert results == [user]

        with freeze_time("2023-08-12 05:00:00"):
            results = list(user_automations.get_ex_underage_beneficiaries_who_can_no_longer_recredit())
            assert not results

    @patch("pcapi.core.users.external.update_batch_user")
    @patch("pcapi.core.users.external.update_sendinblue_user")
    def test_users_whose_credit_expired_today_automation_underage(self, mock_update_sendinblue, mock_update_batch):
        with freeze_time("2021-09-10 15:00:00"):
            user = users_factories.UnderageBeneficiaryFactory(
                email="underage+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=17, months=1),
            )

        with freeze_time("2023-08-11 05:00:00"):
            user_automations.users_whose_credit_expired_today_automation()

        mock_update_sendinblue.assert_called_once()
        mock_update_batch.assert_called_once()

        assert mock_update_sendinblue.call_args.args[0] == user.email
        assert mock_update_sendinblue.call_args.args[1].is_former_beneficiary is True

        assert mock_update_batch.call_args.args[0] == user.id
        assert mock_update_batch.call_args.args[1].is_former_beneficiary is True
