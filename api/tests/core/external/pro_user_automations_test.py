from unittest.mock import patch

import pytest
from sib_api_v3_sdk import RequestContactImport

from pcapi import settings
from pcapi.core.external.automations.pro_user import pro_no_active_offers_since_40_days_automation
from pcapi.core.external.automations.pro_user import pro_no_bookings_since_40_days_automation


pytestmark = pytest.mark.usefixtures("db_session")


class ChurnedProEmailTest:
    @patch("pcapi.connectors.big_query.TestingBackend.run_query")
    @patch("pcapi.core.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
    def test_get_churned_pro_email(self, mock_import_contacts, mock_run_query):
        mock_run_query.return_value = [
            {"venue_booking_email": "alice@example.com"},
            {"venue_booking_email": "beatrice@example.com"},
        ]

        automation_exit_code = pro_no_active_offers_since_40_days_automation()

        mock_import_contacts.assert_called_once_with(
            RequestContactImport(
                file_url=None,
                file_body="EMAIL\nalice@example.com\nbeatrice@example.com",
                list_ids=[settings.SENDINBLUE_PRO_NO_ACTIVE_OFFERS_40_DAYS_ID],
                notify_url=f"{settings.API_URL}/webhooks/sendinblue/importcontacts/{settings.SENDINBLUE_PRO_NO_ACTIVE_OFFERS_40_DAYS_ID}/1",
                new_list=None,
                email_blacklist=False,
                sms_blacklist=False,
                update_existing_contacts=True,
                empty_contacts_attributes=False,
            )
        )
        assert automation_exit_code is True


class NoBookingsProEmailTest:
    @patch("pcapi.connectors.big_query.TestingBackend.run_query")
    @patch("pcapi.core.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
    def test_get_no_bookings_pro_email(self, mock_import_contacts, mock_run_query):
        mock_run_query.return_value = [
            {"venue_booking_email": "alice@example.com"},
            {"venue_booking_email": "beatrice@example.com"},
        ]

        automation_exit_code = pro_no_bookings_since_40_days_automation()

        mock_import_contacts.assert_called_once_with(
            RequestContactImport(
                file_url=None,
                file_body="EMAIL\nalice@example.com\nbeatrice@example.com",
                list_ids=[settings.SENDINBLUE_PRO_NO_BOOKINGS_40_DAYS_ID],
                notify_url=f"{settings.API_URL}/webhooks/sendinblue/importcontacts/{settings.SENDINBLUE_PRO_NO_BOOKINGS_40_DAYS_ID}/1",
                new_list=None,
                email_blacklist=False,
                sms_blacklist=False,
                update_existing_contacts=True,
                empty_contacts_attributes=False,
            )
        )
        assert automation_exit_code is True
