from unittest.mock import patch

import pytest
from sib_api_v3_sdk import RequestContactImport

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
        "pcapi.core.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts"
    )

    @property
    def func(self):
        raise NotImplementedError("func")

    @property
    def base_id(self):
        raise NotImplementedError("base_id")

    @property
    def subaccount_id(self):
        raise NotImplementedError("subaccount_id")

    @pytest.mark.parametrize("with_subaccount", [False, True])
    def test_automation(self, features, with_subaccount):
        with patch(self.MOCK_RUN_BQ_QUERY_PATH) as mock_run_query:
            mock_run_query.return_value = mocked_bq_rows()

            with patch(self.MOCK_IMPORT_CONTACT_PATH) as mock_import_contacts:
                features.WIP_ENABLE_BREVO_PRO_SUBACCOUNT = with_subaccount
                assert type(self).func()  # pylint: disable=no-value-for-parameter # I don't get this code

                expected_params = build_expected_called_params(self.get_list_id(with_subaccount))
                mock_import_contacts.assert_called_once_with(expected_params)

    def get_list_id(self, with_subaccount):
        if with_subaccount:
            return self.subaccount_id
        return self.base_id


class ChurnedProEmailTest(BaseProAutomations):
    func = pro_no_active_offers_since_40_days_automation
    base_id = settings.SENDINBLUE_PRO_NO_ACTIVE_OFFERS_40_DAYS_ID
    subaccount_id = settings.SENDINBLUE_PRO_SUBACCOUNT_NO_ACTIVE_OFFERS_40_DAYS_ID


class NoBookingsProEmailTest(BaseProAutomations):
    func = pro_no_bookings_since_40_days_automation
    base_id = settings.SENDINBLUE_PRO_NO_BOOKINGS_40_DAYS_ID
    subaccount_id = settings.SENDINBLUE_PRO_SUBACCOUNT_NO_BOOKINGS_40_DAYS_ID


class UpdateProContactsListForLiveShowChurned40DaysAgoTest(BaseProAutomations):
    func = update_pro_contacts_list_for_live_show_churned_40_days_ago
    base_id = settings.SENDINBLUE_PRO_MARKETING_LIVE_SHOW_EMAIL_CHURNED_40_DAYS_AGO
    subaccount_id = settings.SENDINBLUE_PRO_SUBACCOUNT_MARKETING_LIVE_SHOW_EMAIL_CHURNED_40_DAYS_AGO


class UpdateProContactsListForLiveShowLastBooking40DaysAgoTest(BaseProAutomations):
    func = update_pro_contacts_list_for_live_show_last_booking_40_days_ago
    base_id = settings.SENDINBLUE_PRO_MARKETING_LIVE_SHOW_EMAIL_LAST_BOOKING_40_DAYS_AGO
    subaccount_id = settings.SENDINBLUE_PRO_SUBACCOUNT_MARKETING_LIVE_SHOW_EMAIL_LAST_BOOKING_40_DAYS_AGO
