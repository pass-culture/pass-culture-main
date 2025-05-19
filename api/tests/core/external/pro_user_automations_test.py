from unittest.mock import patch

import pytest
from brevo_python import RequestContactImport

from pcapi import settings
from pcapi.core.external.automations.pro_user import pro_no_active_offers_since_40_days_automation
from pcapi.core.external.automations.pro_user import pro_no_bookings_since_40_days_automation
from pcapi.core.external.automations.pro_user import update_pro_contacts_list_for_live_show_churned_40_days_ago
from pcapi.core.external.automations.pro_user import update_pro_contacts_list_for_live_show_last_booking_40_days_ago


pytestmark = pytest.mark.usefixtures("db_session")


DEFAULT_EMAILS = ["alice@example.com", "beatrice@example.com"]


def mocked_bq_rows():
    return [
        {"venue_booking_email": DEFAULT_EMAILS[0]},
        {"venue_booking_email": DEFAULT_EMAILS[1]},
    ]


def build_expected_called_params(list_id):
    return RequestContactImport(
        file_url=None,
        file_body=f"EMAIL\n{DEFAULT_EMAILS[0]}\n{DEFAULT_EMAILS[1]}",
        list_ids=[list_id],
        notify_url=f"{settings.API_URL}/webhooks/sendinblue/importcontacts/{list_id}/1",
        new_list=None,
        email_blacklist=False,
        sms_blacklist=False,
        update_existing_contacts=True,
        empty_contacts_attributes=False,
    )


class BaseProAutomations:
    MOCK_RUN_BQ_QUERY_PATH = "pcapi.connectors.big_query.TestingBackend.run_query"
    MOCK_IMPORT_CONTACT_PATH = (
        "pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.import_contacts"
    )

    @property
    def func(self):
        raise NotImplementedError("func")

    @property
    def id(self):
        raise NotImplementedError("id")

    def test_automation(self):
        with patch(self.MOCK_RUN_BQ_QUERY_PATH) as mock_run_query:
            mock_run_query.return_value = mocked_bq_rows()

            with patch(self.MOCK_IMPORT_CONTACT_PATH) as mock_import_contacts:
                assert type(self).func()

                expected_params = build_expected_called_params(self.id)
                mock_import_contacts.assert_called_once_with(expected_params)


class ChurnedProEmailTest(BaseProAutomations):
    func = pro_no_active_offers_since_40_days_automation
    id = settings.SENDINBLUE_PRO_NO_ACTIVE_OFFERS_40_DAYS_ID


class NoBookingsProEmailTest(BaseProAutomations):
    func = pro_no_bookings_since_40_days_automation
    id = settings.SENDINBLUE_PRO_NO_BOOKINGS_40_DAYS_ID


class UpdateProContactsListForLiveShowChurned40DaysAgoTest(BaseProAutomations):
    func = update_pro_contacts_list_for_live_show_churned_40_days_ago
    id = settings.SENDINBLUE_PRO_MARKETING_LIVE_SHOW_EMAIL_CHURNED_40_DAYS_AGO


class UpdateProContactsListForLiveShowLastBooking40DaysAgoTest(BaseProAutomations):
    func = update_pro_contacts_list_for_live_show_last_booking_40_days_ago
    id = settings.SENDINBLUE_PRO_MARKETING_LIVE_SHOW_EMAIL_LAST_BOOKING_40_DAYS_AGO
