from datetime import date
from datetime import datetime
from unittest.mock import patch

from brevo_python import RequestContactImport
from dateutil.relativedelta import relativedelta
import pytest
import time_machine

from pcapi import settings
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.external.automations import user as user_automations
import pcapi.core.users.factories as users_factories
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

    def _create_users_with_deposits(self):
        with time_machine.travel("2032-11-15 15:00:00"):
            user0 = users_factories.UserFactory(
                email="beneficiary0+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=17, days=5),
                roles=[UserRole.UNDERAGE_BENEFICIARY],
            )
            assert user0.deposit is None

        with time_machine.travel("2032-10-31 15:00:00"):
            user1 = users_factories.BeneficiaryFactory(
                email="beneficiary1+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=1),
                deposit__expirationDate=datetime(2034, 10, 31, 23, 59, 59, 999999),
            )

        with time_machine.travel("2032-11-01 15:00:00"):
            user2 = users_factories.BeneficiaryFactory(
                email="beneficiary2+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=2),
                deposit__expirationDate=datetime(2034, 11, 1, 23, 59, 59, 999999),
            )
            bookings_factories.UsedBookingFactory(user=user2, quantity=1, amount=10)

        with time_machine.travel("2032-12-01 15:00:00"):
            user3 = users_factories.BeneficiaryFactory(
                email="beneficiary3+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=3),
                deposit__expirationDate=datetime(2034, 12, 1, 23, 59, 59, 999999),
            )

        with time_machine.travel("2033-01-30 15:00:00"):
            user4 = users_factories.BeneficiaryFactory(
                email="beneficiary4+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=4),
                deposit__expirationDate=datetime(2035, 1, 30, 23, 59, 59, 999999),
            )

        with time_machine.travel("2033-01-31 15:00:00"):
            user5 = users_factories.BeneficiaryFactory(
                email="beneficiary5+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=5),
                deposit__expirationDate=datetime(2035, 1, 31, 23, 59, 59, 999999),
            )

        with time_machine.travel("2033-03-10 15:00:00"):
            user6 = users_factories.BeneficiaryFactory(
                email="beneficiary6+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=5),
                deposit__expirationDate=datetime(2035, 3, 10, 23, 59, 59, 999999),
            )

        with time_machine.travel("2033-05-01 17:00:00"):
            # user6 becomes ex-beneficiary
            bookings_factories.UsedBookingFactory(user=user6, quantity=1, amount=user6.deposit.amount)

        return [user0, user1, user2, user3, user4, user5, user6]

    def test_get_users_ex_beneficiary(self):
        users = self._create_users_with_deposits()

        with time_machine.travel("2034-12-01 16:00:00"):
            results = user_automations.get_users_ex_beneficiary()
            assert sorted([user.email for user in results]) == [user.email for user in users[1:3] + [users[6]]]

        with time_machine.travel("2034-12-02 16:00:00"):
            results = user_automations.get_users_ex_beneficiary()
            assert sorted([user.email for user in results]) == [user.email for user in users[1:4] + [users[6]]]

    @patch("pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.import_contacts")
    def test_user_ex_beneficiary_automation(self, mock_import_contacts):
        users = self._create_users_with_deposits()

        with time_machine.travel("2034-12-01 16:00:00"):
            result = user_automations.users_ex_beneficiary_automation()

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
        assert (
            mock_import_contacts.call_args.args[0].notify_url
            == f"{settings.API_URL}/webhooks/sendinblue/importcontacts/{settings.SENDINBLUE_AUTOMATION_YOUNG_EX_BENEFICIARY_ID}/1"
        )
        assert mock_import_contacts.call_args.args[0].new_list is None
        assert mock_import_contacts.call_args.args[0].sms_blacklist is False
        assert mock_import_contacts.call_args.args[0].update_existing_contacts is True
        assert mock_import_contacts.call_args.args[0].empty_contacts_attributes is False

        assert result is True

    def test_get_email_for_users_created_one_year_ago_per_month(self):
        matching_users = []

        users_factories.UserFactory(email="fabien+test@example.net", dateCreated=datetime(2033, 7, 31))
        matching_users.append(
            users_factories.UserFactory(email="pierre+test@example.net", dateCreated=datetime(2033, 8, 1))
        )
        matching_users.append(
            users_factories.UserFactory(email="marc+test@example.net", dateCreated=datetime(2033, 8, 10))
        )
        matching_users.append(
            users_factories.UserFactory(email="daniel+test@example.net", dateCreated=datetime(2033, 8, 31))
        )
        users_factories.UserFactory(email="billy+test@example.net", dateCreated=datetime(2033, 9, 1))
        users_factories.UserFactory(email="gerard+test@example.net", dateCreated=datetime(2033, 9, 21))

        # matching: from 2033-08-01 to 2033-08-31
        with time_machine.travel("2034-08-10 15:00:00"):
            results = user_automations.get_email_for_users_created_one_year_ago_per_month()
            assert sorted(results) == sorted([user.email for user in matching_users])

    @patch("pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.import_contacts")
    def test_users_nearly_one_year_with_pass_automation(self, mock_import_contacts):
        users_factories.UserFactory(email="fabien+test@example.net", dateCreated=datetime(2033, 8, 31))
        users_factories.UserFactory(email="pierre+test@example.net", dateCreated=datetime(2033, 9, 1))
        users_factories.UserFactory(email="daniel+test@example.net", dateCreated=datetime(2033, 10, 1))
        users_factories.UserFactory(email="gerard+test@example.net", dateCreated=datetime(2033, 10, 31))

        # matching: from 2033-09-01 to 2033-09-31
        with time_machine.travel("2034-09-10 15:00:00"):
            result = user_automations.users_one_year_with_pass_automation()

        mock_import_contacts.assert_called_once_with(
            RequestContactImport(
                file_url=None,
                file_body="EMAIL\npierre+test@example.net",
                list_ids=[settings.SENDINBLUE_AUTOMATION_YOUNG_1_YEAR_WITH_PASS_LIST_ID],
                notify_url=f"{settings.API_URL}/webhooks/sendinblue/importcontacts/{settings.SENDINBLUE_AUTOMATION_YOUNG_1_YEAR_WITH_PASS_LIST_ID}/1",
                new_list=None,
                email_blacklist=False,
                sms_blacklist=False,
                update_existing_contacts=True,
                empty_contacts_attributes=False,
            )
        )

        assert result is True

    def test_get_users_whose_credit_expired_today(self):
        users = self._create_users_with_deposits()

        with time_machine.travel("2034-11-01 05:00:00"):
            results = list(user_automations.get_users_whose_credit_expired_today())
            assert results == [users[1]]

        with time_machine.travel("2034-11-02 05:00:00"):
            results = list(user_automations.get_users_whose_credit_expired_today())
            assert results == [users[2]]

    @patch("pcapi.core.external.attributes.api.update_batch_user")
    @patch("pcapi.core.external.attributes.api.update_sendinblue_user")
    def test_users_whose_credit_expired_today_automation(self, mock_update_sendinblue, mock_update_batch):
        users = self._create_users_with_deposits()

        with time_machine.travel("2034-11-02 05:00:00"):
            user_automations.users_whose_credit_expired_today_automation()

        mock_update_sendinblue.assert_called_once()
        mock_update_batch.assert_called_once()

        assert mock_update_sendinblue.call_args.args[0] == users[2].email
        assert mock_update_sendinblue.call_args.args[1].is_former_beneficiary is True

        assert mock_update_batch.call_args.args[0] == users[2].id
        assert mock_update_batch.call_args.args[1].is_former_beneficiary is True

    def test_get_ex_underage_beneficiaries_who_can_no_longer_recredit(self):
        with time_machine.travel("2033-09-10 15:00:00"):
            user = users_factories.UnderageBeneficiaryFactory(
                email="underage+test@example.net",
                dateOfBirth=datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=17, months=1),
                deposit__expirationDate=datetime(2034, 8, 10),  # at birthday, to emulate the behaviour before credit V3
            )

        with time_machine.travel("2034-08-10 05:00:00"):
            results = list(user_automations.get_ex_underage_beneficiaries_who_can_no_longer_recredit())
            assert not results

        with time_machine.travel("2035-08-10 05:00:00"):
            results = list(user_automations.get_ex_underage_beneficiaries_who_can_no_longer_recredit())
            assert not results

        with time_machine.travel("2035-08-11 05:00:00"):
            results = list(user_automations.get_ex_underage_beneficiaries_who_can_no_longer_recredit())
            assert results == [user]

        with time_machine.travel("2035-08-12 05:00:00"):
            results = list(user_automations.get_ex_underage_beneficiaries_who_can_no_longer_recredit())
            assert not results
