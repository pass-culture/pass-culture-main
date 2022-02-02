from copy import deepcopy
from datetime import datetime
from unittest.mock import call
from unittest.mock import patch

import pytest
from sib_api_v3_sdk.models.remove_contact_from_list import RemoveContactFromList
from sib_api_v3_sdk.models.request_contact_import import RequestContactImport

from pcapi import settings
from pcapi.core.users.external.sendinblue import SendinblueUserUpdateData
from pcapi.core.users.external.sendinblue import add_contacts_to_list
from pcapi.core.users.external.sendinblue import build_file_body
from pcapi.core.users.external.sendinblue import format_user_attributes
from pcapi.core.users.external.sendinblue import import_contacts_in_sendinblue
from pcapi.core.users.external.sendinblue import make_update_request
from pcapi.tasks.serialization.sendinblue_tasks import UpdateSendinblueContactRequest

from . import common_pro_attributes
from . import common_user_attributes


# Do not use this identifier with production account when running skipped tests
SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID = 18
SENDINBLUE_PRO_TESTING_CONTACT_LIST_ID = 12

pytestmark = pytest.mark.usefixtures("db_session")


class FormatUserAttributesTest:
    def test_format_attributes(self):
        formatted_attributes = format_user_attributes(common_user_attributes)

        assert formatted_attributes == {
            "BOOKED_OFFER_CATEGORIES": "CINEMA,LIVRE",
            "BOOKED_OFFER_SUBCATEGORIES": "ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR",
            "BOOKING_COUNT": 4,
            "DATE_CREATED": datetime(2021, 2, 6),
            "DATE_OF_BIRTH": datetime(2003, 5, 6),
            "DEPARTMENT_CODE": "12",
            "DEPOSIT_ACTIVATION_DATE": None,
            "DEPOSIT_EXPIRATION_DATE": None,
            "ELIGIBILITY": "age-18",
            "FIRSTNAME": "First name",
            "HAS_COMPLETED_ID_CHECK": True,
            "INITIAL_CREDIT": 500,
            "CREDIT": 480,
            "IS_BENEFICIARY": True,
            "IS_BENEFICIARY_18": True,
            "IS_ELIGIBLE": True,
            "IS_EMAIL_VALIDATED": True,
            "IS_PRO": False,
            "IS_UNDERAGE_BENEFICIARY": False,
            "LAST_BOOKING_DATE": datetime(2021, 5, 6),
            "LAST_FAVORITE_CREATION_DATE": None,
            "LAST_VISIT_DATE": None,
            "LASTNAME": "Last name",
            "MARKETING_EMAIL_SUBSCRIPTION": True,
            "POSTAL_CODE": None,
            "PRODUCT_BRUT_X_USE_DATE": datetime(2021, 5, 6),
            "USER_ID": 1,
            "DMS_APPLICATION_SUBMITTED": None,
            "DMS_APPLICATION_APPROVED": None,
            "HAS_BOOKINGS": None,
            "HAS_OFFERS": None,
            "IS_BOOKING_EMAIL": None,
            "IS_PERMANENT": None,
            "IS_USER_EMAIL": None,
            "IS_VIRTUAL": None,
            "OFFERER_NAME": None,
            "USER_IS_ATTACHED": None,
            "USER_IS_CREATOR": None,
            "VENUE_COUNT": None,
            "VENUE_LABEL": None,
            "VENUE_NAME": None,
            "VENUE_TYPE": None,
        }

    def test_format_pro_attributes(self):
        formatted_attributes = format_user_attributes(common_pro_attributes)

        assert formatted_attributes == {
            "BOOKED_OFFER_CATEGORIES": None,
            "BOOKED_OFFER_SUBCATEGORIES": None,
            "BOOKING_COUNT": None,
            "DATE_CREATED": None,
            "DATE_OF_BIRTH": None,
            "DEPARTMENT_CODE": "04,06",
            "DEPOSIT_ACTIVATION_DATE": None,
            "DEPOSIT_EXPIRATION_DATE": None,
            "ELIGIBILITY": None,
            "FIRSTNAME": "First name",
            "HAS_COMPLETED_ID_CHECK": None,
            "INITIAL_CREDIT": None,
            "CREDIT": None,
            "IS_BENEFICIARY": None,
            "IS_BENEFICIARY_18": None,
            "IS_ELIGIBLE": None,
            "IS_EMAIL_VALIDATED": None,
            "IS_PRO": True,
            "IS_UNDERAGE_BENEFICIARY": None,
            "LAST_BOOKING_DATE": None,
            "LAST_FAVORITE_CREATION_DATE": None,
            "LAST_VISIT_DATE": None,
            "LASTNAME": "Last name",
            "MARKETING_EMAIL_SUBSCRIPTION": True,
            "POSTAL_CODE": None,
            "PRODUCT_BRUT_X_USE_DATE": None,
            "USER_ID": 2,
            "DMS_APPLICATION_SUBMITTED": False,
            "DMS_APPLICATION_APPROVED": True,
            "HAS_BOOKINGS": True,
            "HAS_OFFERS": True,
            "IS_BOOKING_EMAIL": True,
            "IS_PERMANENT": True,
            "IS_USER_EMAIL": True,
            "IS_VIRTUAL": False,
            "OFFERER_NAME": "Offerer Name 1,Offerer Name 2",
            "USER_IS_ATTACHED": False,
            "USER_IS_CREATOR": True,
            "VENUE_COUNT": 2,
            "VENUE_LABEL": "Venue Label",
            "VENUE_NAME": "Venue Name 1,Venue Name 2",
            "VENUE_TYPE": "BOOKSTORE,MOVIE",
        }


class BulkImportUsersDataTest:
    def setup_method(self):
        eren_attributes = deepcopy(common_user_attributes)
        mikasa_attributes = deepcopy(common_user_attributes)
        mikasa_attributes.is_pro = True
        mikasa_attributes.user_id = 2
        armin_attributes = deepcopy(common_user_attributes)
        armin_attributes.user_id = 3

        self.users_data = [
            SendinblueUserUpdateData(
                email="eren.yeager@shinganshina.paradis", attributes=format_user_attributes(eren_attributes)
            ),
            SendinblueUserUpdateData(
                email="mikasa.ackerman@shinganshina.paradis",
                attributes=format_user_attributes(mikasa_attributes),
            ),
            SendinblueUserUpdateData(
                email="armin.arlert@shinganshina.paradis",
                attributes=format_user_attributes(armin_attributes),
            ),
        ]

        self.expected_header = "BOOKED_OFFER_CATEGORIES;BOOKED_OFFER_SUBCATEGORIES;BOOKING_COUNT;CREDIT;DATE_CREATED;DATE_OF_BIRTH;DEPARTMENT_CODE;DEPOSIT_ACTIVATION_DATE;DEPOSIT_EXPIRATION_DATE;DMS_APPLICATION_APPROVED;DMS_APPLICATION_SUBMITTED;ELIGIBILITY;FIRSTNAME;HAS_BOOKINGS;HAS_COMPLETED_ID_CHECK;HAS_OFFERS;INITIAL_CREDIT;IS_BENEFICIARY;IS_BENEFICIARY_18;IS_BOOKING_EMAIL;IS_ELIGIBLE;IS_EMAIL_VALIDATED;IS_PERMANENT;IS_PRO;IS_UNDERAGE_BENEFICIARY;IS_USER_EMAIL;IS_VIRTUAL;LASTNAME;LAST_BOOKING_DATE;LAST_FAVORITE_CREATION_DATE;LAST_VISIT_DATE;MARKETING_EMAIL_SUBSCRIPTION;OFFERER_NAME;POSTAL_CODE;PRODUCT_BRUT_X_USE_DATE;USER_ID;USER_IS_ATTACHED;USER_IS_CREATOR;VENUE_COUNT;VENUE_LABEL;VENUE_NAME;VENUE_TYPE;EMAIL"
        self.eren_expected_file_body = "CINEMA,LIVRE;ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR;4;480.00;06-02-2021;06-05-2003;12;;;;;age-18;First name;;Yes;;500;Yes;Yes;;Yes;Yes;;No;No;;;Last name;06-05-2021;;;Yes;;;06-05-2021;1;;;;;;;eren.yeager@shinganshina.paradis"
        self.mikasa_expected_file_body = "CINEMA,LIVRE;ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR;4;480.00;06-02-2021;06-05-2003;12;;;;;age-18;First name;;Yes;;500;Yes;Yes;;Yes;Yes;;Yes;No;;;Last name;06-05-2021;;;Yes;;;06-05-2021;2;;;;;;;mikasa.ackerman@shinganshina.paradis"
        self.armin_expected_file_body = "CINEMA,LIVRE;ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR;4;480.00;06-02-2021;06-05-2003;12;;;;;age-18;First name;;Yes;;500;Yes;Yes;;Yes;Yes;;No;No;;;Last name;06-05-2021;;;Yes;;;06-05-2021;3;;;;;;;armin.arlert@shinganshina.paradis"

    def test_build_file_body(self):
        expected = (
            f"{self.expected_header}\n"
            f"{self.eren_expected_file_body}\n"
            f"{self.mikasa_expected_file_body}\n"
            f"{self.armin_expected_file_body}"
        )
        result = build_file_body(self.users_data)

        assert expected == result

    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
    def test_import_contacts_in_sendinblue(self, mock_import_contacts):
        import_contacts_in_sendinblue(self.users_data)

        expected_common_params = {
            "email_blacklist": False,
            "empty_contacts_attributes": False,
            "file_body": "",
            "file_url": None,
            "new_list": None,
            "notify_url": None,
            "sms_blacklist": False,
            "update_existing_contacts": True,
        }

        expected_pro_call = RequestContactImport(
            **expected_common_params,
        )
        expected_pro_call.list_ids = [settings.SENDINBLUE_YOUNG_CONTACT_LIST_ID]
        expected_pro_call.file_body = (
            f"{self.expected_header}\n{self.eren_expected_file_body}\n{self.armin_expected_file_body}"
        )

        expected_young_call = RequestContactImport(
            **expected_common_params,
        )
        expected_young_call.list_ids = [settings.SENDINBLUE_PRO_CONTACT_LIST_ID]
        expected_young_call.file_body = f"{self.expected_header}\n{self.mikasa_expected_file_body}"

        mock_import_contacts.assert_has_calls([call(expected_pro_call), call(expected_young_call)], any_order=True)

    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.process_api.ProcessApi.get_process")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.import_contacts")
    @patch("pcapi.core.users.external.sendinblue.sib_api_v3_sdk.api.contacts_api.ContactsApi.remove_contact_from_list")
    def test_add_contacts_to_list(self, mock_remove_contact_from_list, mock_import_contacts, mock_get_process):
        result = add_contacts_to_list(
            ["eren.yeager@shinganshina.paradis", "armin.arlert@shinganshina.paradis"],
            SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID,
            clear_list_first=True,
        )

        mock_remove_contact_from_list.assert_called_once_with(
            SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID, RemoveContactFromList(emails=None, ids=None, all=True)
        )

        mock_import_contacts.assert_called_once_with(
            RequestContactImport(
                file_url=None,
                file_body="EMAIL\neren.yeager@shinganshina.paradis\narmin.arlert@shinganshina.paradis",
                list_ids=[SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID],
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

    @pytest.mark.skip(reason="For dev and debug only - this test sends data to sendinblue")
    def test_add_contacts_to_list_without_mock(self):
        result = add_contacts_to_list(
            ["eren.yeager@shinganshina.paradis", "armin.arlert@shinganshina.paradis"],
            SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID,
            clear_list_first=True,
        )

        assert result is True

    def _test_add_many_contacts_to_list_without_mock(self, count: int, prefix: str):
        # 40 characters per email address
        test_time = datetime.now().strftime("%y%m%d.%H%M")
        thousands_emails = (f"test.{prefix}.{test_time}.{i:06d}@example.net" for i in range(1, count + 1))

        result = add_contacts_to_list(
            thousands_emails,
            SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID,
            clear_list_first=True,
        )

        assert result is True

    @pytest.mark.skip(reason="For dev and debug only - this test sends data to sendinblue")
    def test_add_200k_contacts_to_list_without_mock(self):
        # 200k contacts: a single 8MB import request
        self._test_add_many_contacts_to_list_without_mock(200000, "200k")

    @pytest.mark.skip(reason="For dev and debug only - this test sends data to sendinblue")
    def test_add_500k_contacts_to_list_without_mock(self):
        # 500k contacts: several import requests
        # Use with caution, test may take 10, 20, 25 minutes...
        self._test_add_many_contacts_to_list_without_mock(500000, "500k")

    @pytest.mark.skip(reason="For dev and debug only - this test sends data to sendinblue")
    def test_update_pro_contact_without_mock(self):
        # This test helps to check data received in Sendinblue dashboard manually.
        # Note that SENDINBLUE_API_KEY must be filled in settings and code under IS_RUNNING_TESTS and IS_DEV must be
        # temporarily disabled in make_update_request to really send data to Sendinblue test account.
        assert make_update_request(
            UpdateSendinblueContactRequest(
                email=f"test.pro.{datetime.now().strftime('%y%m%d.%H%M')}@example.net",
                attributes=format_user_attributes(common_pro_attributes),
                contact_list_ids=[SENDINBLUE_PRO_TESTING_CONTACT_LIST_ID],
                emailBlacklisted=False,
            )
        )
