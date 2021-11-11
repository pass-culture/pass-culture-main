from copy import deepcopy
from datetime import datetime
from unittest.mock import call
from unittest.mock import patch

import pytest
from sib_api_v3_sdk.models.request_contact_import import RequestContactImport

from pcapi import settings
from pcapi.core.users.external.sendinblue import SendinblueUserUpdateData
from pcapi.core.users.external.sendinblue import build_file_body
from pcapi.core.users.external.sendinblue import format_user_attributes
from pcapi.core.users.external.sendinblue import import_contacts_in_sendinblue

from . import common_user_attributes


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

        self.expected_header = "BOOKED_OFFER_CATEGORIES;BOOKED_OFFER_SUBCATEGORIES;BOOKING_COUNT;CREDIT;DATE_CREATED;DATE_OF_BIRTH;DEPARTMENT_CODE;DEPOSIT_ACTIVATION_DATE;DEPOSIT_EXPIRATION_DATE;ELIGIBILITY;FIRSTNAME;HAS_COMPLETED_ID_CHECK;INITIAL_CREDIT;IS_BENEFICIARY;IS_BENEFICIARY_18;IS_ELIGIBLE;IS_EMAIL_VALIDATED;IS_PRO;IS_UNDERAGE_BENEFICIARY;LASTNAME;LAST_BOOKING_DATE;LAST_FAVORITE_CREATION_DATE;LAST_VISIT_DATE;MARKETING_EMAIL_SUBSCRIPTION;POSTAL_CODE;PRODUCT_BRUT_X_USE_DATE;USER_ID;EMAIL"
        self.eren_expected_file_body = "CINEMA,LIVRE;ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR;4;480.00;06-02-2021;06-05-2003;12;;;age-18;First name;Yes;500;Yes;Yes;Yes;Yes;No;No;Last name;06-05-2021;;;Yes;;06-05-2021;1;eren.yeager@shinganshina.paradis"
        self.mikasa_expected_file_body = "CINEMA,LIVRE;ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR;4;480.00;06-02-2021;06-05-2003;12;;;age-18;First name;Yes;500;Yes;Yes;Yes;Yes;Yes;No;Last name;06-05-2021;;;Yes;;06-05-2021;2;mikasa.ackerman@shinganshina.paradis"
        self.armin_expected_file_body = "CINEMA,LIVRE;ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR;4;480.00;06-02-2021;06-05-2003;12;;;age-18;First name;Yes;500;Yes;Yes;Yes;Yes;No;No;Last name;06-05-2021;;;Yes;;06-05-2021;3;armin.arlert@shinganshina.paradis"

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
