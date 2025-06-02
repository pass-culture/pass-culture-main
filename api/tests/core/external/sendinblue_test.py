import warnings
from copy import deepcopy
from datetime import datetime
from unittest.mock import call
from unittest.mock import patch

import pytest
from brevo_python.models.request_contact_import import RequestContactImport

import pcapi.core.users.testing as sendinblue_testing
from pcapi import settings
from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.core.external.sendinblue import SendinblueUserUpdateData
from pcapi.core.external.sendinblue import add_contacts_to_list
from pcapi.core.external.sendinblue import build_file_body
from pcapi.core.external.sendinblue import format_cultural_survey_answers
from pcapi.core.external.sendinblue import format_pro_attributes
from pcapi.core.external.sendinblue import format_user_attributes
from pcapi.core.external.sendinblue import import_contacts_in_sendinblue
from pcapi.core.external.sendinblue import make_update_request
from pcapi.tasks.serialization import sendinblue_tasks

from . import common_pro_attributes
from . import common_user_attributes


# Do not use this identifier with production account when running skipped tests
SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID = 18

pytestmark = pytest.mark.usefixtures("db_session")


class FormatUserAttributesTest:
    def test_format_attributes(self):
        formatted_attributes = format_user_attributes(common_user_attributes)

        assert formatted_attributes == {
            "BOOKED_OFFER_CATEGORIES": "CINEMA,LIVRE",
            "BOOKED_OFFER_CATEGORIES_COUNT": 2,
            "BOOKED_OFFER_SUBCATEGORIES": "ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR",
            "BOOKING_COUNT": 4,
            "BOOKING_VENUES_COUNT": 3,
            "DATE_CREATED": datetime(2021, 2, 6),
            "DATE_OF_BIRTH": datetime(2003, 5, 6),
            "DEPARTMENT_CODE": "12",
            "DEPOSITS_COUNT": 1,
            "DEPOSIT_ACTIVATION_DATE": None,
            "DEPOSIT_EXPIRATION_DATE": None,
            "ELIGIBILITY": "age-18",
            "FIRSTNAME": "First name",
            "HAS_COLLECTIVE_OFFERS": None,
            "HAS_COMPLETED_ID_CHECK": True,
            "INITIAL_CREDIT": 500,
            "CREDIT": 480,
            "IS_ACTIVE_PRO": None,
            "IS_BENEFICIARY": True,
            "IS_BENEFICIARY_18": True,
            "IS_CURRENT_BENEFICIARY": True,
            "IS_FORMER_BENEFICIARY": False,
            "IS_OPEN_TO_PUBLIC": None,
            "IS_ELIGIBLE": True,
            "IS_EMAIL_VALIDATED": True,
            "IS_PRO": False,
            "IS_UNDERAGE_BENEFICIARY": False,
            "LAST_BOOKING_DATE": datetime(2021, 5, 6),
            "LAST_FAVORITE_CREATION_DATE": None,
            "LAST_RECREDIT_TYPE": None,
            "LAST_VISIT_DATE": None,
            "LASTNAME": "Last name",
            "MARKETING_EMAIL_SUBSCRIPTION": True,
            "MOST_BOOKED_OFFER_SUBCATEGORY": "CINE_PLEIN_AIR",
            "MOST_BOOKED_MOVIE_GENRE": "COMEDY",
            "MOST_BOOKED_MUSIC_TYPE": "900",
            "MOST_FAVORITE_OFFER_SUBCATEGORIES": "CINE_PLEIN_AIR,SUPPORT_PHYSIQUE_FILM",
            "PERMANENT_THEME_PREFERENCE": "cinema",
            "POSTAL_CODE": None,
            "PRODUCT_BRUT_X_USE_DATE": datetime(2021, 5, 6),
            "USER_ID": 1,
            "DMS_APPLICATION_SUBMITTED": None,
            "DMS_APPLICATION_APPROVED": None,
            "HAS_BOOKINGS": None,
            "HAS_INDIVIDUAL_OFFERS": None,
            "HAS_OFFERS": None,
            "HAS_BANNER_URL": None,
            "IS_BOOKING_EMAIL": None,
            "IS_PERMANENT": None,
            "IS_USER_EMAIL": None,
            "IS_VIRTUAL": None,
            "OFFERER_NAME": None,
            "OFFERER_TAG": None,
            "USER_IS_ATTACHED": None,
            "USER_IS_CREATOR": None,
            "VENUE_COUNT": None,
            "VENUE_LABEL": None,
            "VENUE_NAME": None,
            "VENUE_TYPE": None,
            "IS_EAC": None,
            "EAC_MEG": None,
            "ACHIEVEMENTS": "",
        }

    def test_format_pro_attributes(self):
        formatted_attributes = format_user_attributes(common_pro_attributes)

        assert formatted_attributes == {
            "BOOKED_OFFER_CATEGORIES": None,
            "BOOKED_OFFER_CATEGORIES_COUNT": None,
            "BOOKED_OFFER_SUBCATEGORIES": None,
            "BOOKING_COUNT": None,
            "BOOKING_VENUES_COUNT": None,
            "DATE_CREATED": None,
            "DATE_OF_BIRTH": None,
            "DEPARTMENT_CODE": "04,06",
            "DEPOSITS_COUNT": None,
            "DEPOSIT_ACTIVATION_DATE": None,
            "DEPOSIT_EXPIRATION_DATE": None,
            "ELIGIBILITY": None,
            "FIRSTNAME": "First name",
            "HAS_COLLECTIVE_OFFERS": False,
            "HAS_COMPLETED_ID_CHECK": None,
            "INITIAL_CREDIT": None,
            "CREDIT": None,
            "IS_ACTIVE_PRO": True,
            "IS_BENEFICIARY": None,
            "IS_BENEFICIARY_18": None,
            "IS_CURRENT_BENEFICIARY": None,
            "IS_FORMER_BENEFICIARY": None,
            "IS_ELIGIBLE": None,
            "IS_EMAIL_VALIDATED": None,
            "IS_PRO": True,
            "IS_UNDERAGE_BENEFICIARY": None,
            "LAST_BOOKING_DATE": None,
            "LAST_FAVORITE_CREATION_DATE": None,
            "LAST_RECREDIT_TYPE": None,
            "LAST_VISIT_DATE": None,
            "LASTNAME": "Last name",
            "MARKETING_EMAIL_SUBSCRIPTION": True,
            "MOST_BOOKED_OFFER_SUBCATEGORY": None,
            "MOST_BOOKED_MOVIE_GENRE": None,
            "MOST_BOOKED_MUSIC_TYPE": None,
            "MOST_FAVORITE_OFFER_SUBCATEGORIES": None,
            "PERMANENT_THEME_PREFERENCE": "",
            "POSTAL_CODE": "04000,06400",
            "PRODUCT_BRUT_X_USE_DATE": None,
            "USER_ID": 2,
            "DMS_APPLICATION_SUBMITTED": False,
            "DMS_APPLICATION_APPROVED": True,
            "HAS_BANNER_URL": True,
            "HAS_BOOKINGS": True,
            "HAS_INDIVIDUAL_OFFERS": True,
            "HAS_OFFERS": True,
            "IS_BOOKING_EMAIL": True,
            "IS_PERMANENT": True,
            "IS_OPEN_TO_PUBLIC": True,
            "IS_USER_EMAIL": True,
            "IS_VIRTUAL": False,
            "OFFERER_NAME": "Offerer Name 1,Offerer Name 2",
            "OFFERER_TAG": "top-acteur,collectivite",
            "USER_IS_ATTACHED": False,
            "USER_IS_CREATOR": True,
            "VENUE_COUNT": 2,
            "VENUE_LABEL": "Venue Label",
            "VENUE_NAME": "Venue Name 1,Venue Name 2",
            "VENUE_TYPE": "BOOKSTORE,MOVIE",
            "IS_EAC": False,
            "EAC_MEG": False,
            "ACHIEVEMENTS": None,
        }

    def test_new_format_pro_attributes(self):
        formatted_attributes = format_pro_attributes(common_pro_attributes)

        assert formatted_attributes == {
            "FIRSTNAME": "First name",
            "IS_ACTIVE_PRO": True,
            "IS_PRO": True,
            "LASTNAME": "Last name",
            "DMS_APPLICATION_SUBMITTED": False,
            "DMS_APPLICATION_APPROVED": True,
            "HAS_BANNER_URL": True,
            "HAS_BOOKINGS": True,
            "HAS_COLLECTIVE_OFFERS": False,
            "HAS_INDIVIDUAL_OFFERS": True,
            "HAS_OFFERS": True,
            "IS_EAC": False,
            "IS_EAC_MEG": False,
            "IS_OPEN_TO_PUBLIC": True,
            "IS_BOOKING_EMAIL": True,
            "IS_PERMANENT": True,
            "IS_USER_EMAIL": True,
            "IS_VIRTUAL": False,
            "MARKETING_EMAIL_SUBSCRIPTION": True,
            "OFFERER_NAME": "Offerer Name 1,Offerer Name 2",
            "OFFERER_TAG": "top-acteur,collectivite",
            "USER_ID": 2,
            "USER_IS_ATTACHED": False,
            "USER_IS_CREATOR": True,
            "VENUE_COUNT": 2,
            "VENUE_LABEL": "Venue Label",
            "VENUE_NAME": "Venue Name 1,Venue Name 2",
            "VENUE_TYPE": "BOOKSTORE,MOVIE",
        }

    def test_format_user_attributes_with_achievements_sendinblue(self):
        attributes = deepcopy(common_user_attributes)
        attributes.achievements = [
            "FIRST_MOVIE_BOOKING",
            "FIRST_BOOKING",
        ]

        formatted = format_user_attributes(attributes)

        assert formatted["ACHIEVEMENTS"] == "FIRST_MOVIE_BOOKING,FIRST_BOOKING"


class FormatCulturalSurveyAnswersTest:
    def test_format_cultural_survey_answers(self):
        cultural_survey_answers = {
            cultural_survey_models.CulturalSurveyQuestionEnum.SORTIES.value: [
                cultural_survey_models.CulturalSurveyAnswerEnum.FESTIVAL.value,
            ],
            cultural_survey_models.CulturalSurveyQuestionEnum.PROJECTIONS.value: [
                cultural_survey_models.CulturalSurveyAnswerEnum.PROJECTION_CONCERT.value,
                cultural_survey_models.CulturalSurveyAnswerEnum.PROJECTION_FESTIVAL.value,
            ],
        }

        formatted_attributes = format_cultural_survey_answers(cultural_survey_answers)

        assert formatted_attributes == {
            "INTENDED_CATEGORIES": "PROJECTION_CONCERT,PROJECTION_FESTIVAL",
        }

    def test_format_cultural_survey_answers_no_projection(self):
        answers = {
            cultural_survey_models.CulturalSurveyQuestionEnum.SORTIES.value: [
                cultural_survey_models.CulturalSurveyAnswerEnum.FESTIVAL.value,
            ],
            cultural_survey_models.CulturalSurveyQuestionEnum.FESTIVALS.value: [
                cultural_survey_models.CulturalSurveyAnswerEnum.FESTIVAL_MUSIQUE.value,
            ],
        }

        formatted_attributes = format_cultural_survey_answers(answers)

        assert formatted_attributes == {"INTENDED_CATEGORIES": ""}


class BulkImportUsersDataTest:
    def setup_method(self):
        eren_attributes = deepcopy(common_user_attributes)
        mikasa_attributes = deepcopy(common_user_attributes)
        mikasa_attributes.is_pro = True
        mikasa_attributes.has_collective_offers = True
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

        self.expected_header = "ACHIEVEMENTS;BOOKED_OFFER_CATEGORIES;BOOKED_OFFER_CATEGORIES_COUNT;BOOKED_OFFER_SUBCATEGORIES;BOOKING_COUNT;BOOKING_VENUES_COUNT;CREDIT;DATE_CREATED;DATE_OF_BIRTH;DEPARTMENT_CODE;DEPOSITS_COUNT;DEPOSIT_ACTIVATION_DATE;DEPOSIT_EXPIRATION_DATE;DMS_APPLICATION_APPROVED;DMS_APPLICATION_SUBMITTED;EAC_MEG;ELIGIBILITY;FIRSTNAME;HAS_BANNER_URL;HAS_BOOKINGS;HAS_COLLECTIVE_OFFERS;HAS_COMPLETED_ID_CHECK;HAS_INDIVIDUAL_OFFERS;HAS_OFFERS;INITIAL_CREDIT;IS_ACTIVE_PRO;IS_BENEFICIARY;IS_BENEFICIARY_18;IS_BOOKING_EMAIL;IS_CURRENT_BENEFICIARY;IS_EAC;IS_EAC_MEG;IS_ELIGIBLE;IS_EMAIL_VALIDATED;IS_FORMER_BENEFICIARY;IS_OPEN_TO_PUBLIC;IS_PERMANENT;IS_PRO;IS_UNDERAGE_BENEFICIARY;IS_USER_EMAIL;IS_VIRTUAL;LASTNAME;LAST_BOOKING_DATE;LAST_FAVORITE_CREATION_DATE;LAST_RECREDIT_TYPE;LAST_VISIT_DATE;MARKETING_EMAIL_SUBSCRIPTION;MOST_BOOKED_MOVIE_GENRE;MOST_BOOKED_MUSIC_TYPE;MOST_BOOKED_OFFER_SUBCATEGORY;MOST_FAVORITE_OFFER_SUBCATEGORIES;OFFERER_NAME;OFFERER_TAG;PERMANENT_THEME_PREFERENCE;POSTAL_CODE;PRODUCT_BRUT_X_USE_DATE;USER_ID;USER_IS_ATTACHED;USER_IS_CREATOR;VENUE_COUNT;VENUE_LABEL;VENUE_NAME;VENUE_TYPE;EMAIL"
        self.eren_expected_file_body = ";CINEMA,LIVRE;2;ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR;4;3;480.00;06-02-2021;06-05-2003;12;1;;;;;;age-18;First name;;;;Yes;;;500;;Yes;Yes;;Yes;;Yes;Yes;No;;;No;No;;;Last name;06-05-2021;;;;Yes;COMEDY;900;CINE_PLEIN_AIR;CINE_PLEIN_AIR,SUPPORT_PHYSIQUE_FILM;;;cinema;;06-05-2021;1;;;;;;;eren.yeager@shinganshina.paradis"
        self.mikasa_expected_file_body = ";CINEMA,LIVRE;2;ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR;4;3;480.00;06-02-2021;06-05-2003;12;1;;;;;;age-18;First name;;;Yes;Yes;;;500;;Yes;Yes;;Yes;;Yes;Yes;No;;;Yes;No;;;Last name;06-05-2021;;;;Yes;COMEDY;900;CINE_PLEIN_AIR;CINE_PLEIN_AIR,SUPPORT_PHYSIQUE_FILM;;;cinema;;06-05-2021;2;;;;;;;mikasa.ackerman@shinganshina.paradis"
        self.armin_expected_file_body = ";CINEMA,LIVRE;2;ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR;4;3;480.00;06-02-2021;06-05-2003;12;1;;;;;;age-18;First name;;;;Yes;;;500;;Yes;Yes;;Yes;;Yes;Yes;No;;;No;No;;;Last name;06-05-2021;;;;Yes;COMEDY;900;CINE_PLEIN_AIR;CINE_PLEIN_AIR,SUPPORT_PHYSIQUE_FILM;;;cinema;;06-05-2021;3;;;;;;;armin.arlert@shinganshina.paradis"

    def test_build_file_body(self):
        expected = (
            f"{self.expected_header}\n"
            f"{self.eren_expected_file_body}\n"
            f"{self.mikasa_expected_file_body}\n"
            f"{self.armin_expected_file_body}"
        )
        result = build_file_body(self.users_data)
        assert result == expected

    @patch("pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.import_contacts")
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

        expected_young_call = RequestContactImport(
            **expected_common_params,
        )
        expected_young_call.list_ids = [settings.SENDINBLUE_YOUNG_CONTACT_LIST_ID]
        expected_young_call.file_body = (
            f"{self.expected_header}\n{self.eren_expected_file_body}\n{self.armin_expected_file_body}"
        )

        expected_pro_call = RequestContactImport(
            **expected_common_params,
        )
        expected_pro_call.list_ids = None
        expected_pro_call.file_body = f"{self.expected_header}\n{self.mikasa_expected_file_body}"

        mock_import_contacts.assert_has_calls([call(expected_young_call), call(expected_pro_call)], any_order=True)

    @pytest.mark.parametrize("use_pro_subaccount", [True, False])
    @patch("pcapi.core.external.sendinblue.brevo_python.api.contacts_api.ContactsApi.import_contacts")
    def test_add_contacts_to_list(self, mock_import_contacts, use_pro_subaccount):
        result = add_contacts_to_list(
            ["eren.yeager@shinganshina.paradis", "armin.arlert@shinganshina.paradis"],
            SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID,
            use_pro_subaccount=use_pro_subaccount,
        )

        mock_import_contacts.assert_called_once_with(
            RequestContactImport(
                file_url=None,
                file_body="EMAIL\neren.yeager@shinganshina.paradis\narmin.arlert@shinganshina.paradis",
                list_ids=[SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID],
                notify_url=f"{settings.API_URL}/webhooks/sendinblue/importcontacts/{SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID}/1",
                new_list=None,
                email_blacklist=False,
                sms_blacklist=False,
                update_existing_contacts=True,
                empty_contacts_attributes=False,
            )
        )

        assert result is True

    @pytest.mark.skip(reason="For dev and debug only - this test sends data to sendinblue")
    # @pytest.mark.settings(API_URL="http://dev.external.ip:5001", SENDINBLUE_API_KEY="...")
    def test_add_contacts_to_list_without_mock(self):
        # Avoid pytest.PytestUnraisableExceptionWarning: Exception ignored in: <ssl.SSLSocket ...>
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

        result = add_contacts_to_list(
            ["eren.yeager@shinganshina.paradis", "armin.arlert@shinganshina.paradis"],
            SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID,
        )

        assert result is True

    def _test_add_many_contacts_to_list_without_mock(self, count: int, prefix: str):
        # Avoid pytest.PytestUnraisableExceptionWarning: Exception ignored in: <ssl.SSLSocket ...>
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

        # 40 characters per email address
        test_time = datetime.utcnow().strftime("%y%m%d.%H%M")
        thousands_emails = (f"test.{prefix}.{test_time}.{i:06d}@example.net" for i in range(1, count + 1))

        result = add_contacts_to_list(thousands_emails, SENDINBLUE_AUTOMATION_TEST_CONTACT_LIST_ID)

        assert result is True

    @pytest.mark.skip(reason="For dev and debug only - this test sends data to sendinblue")
    # @pytest.mark.settings(API_URL="http://dev.external.ip:5001", SENDINBLUE_API_KEY="...")
    def test_add_200k_contacts_to_list_without_mock(self):
        # 200k contacts: a single 8MB import request
        self._test_add_many_contacts_to_list_without_mock(200000, "200k")

    @pytest.mark.skip(reason="For dev and debug only - this test sends data to sendinblue")
    # @pytest.mark.settings(API_URL="http://dev.external.ip:5001", SENDINBLUE_API_KEY="...")
    def test_add_500k_contacts_to_list_without_mock(self):
        # 500k contacts: several import requests
        # Use with caution, ingestion may take 10, 20, 25 minutes... before calling webhook
        self._test_add_many_contacts_to_list_without_mock(500000, "500k")

    @pytest.mark.skip(reason="For dev and debug only - this test sends data to sendinblue")
    @pytest.mark.settings(IS_RUNNING_TESTS=False, IS_DEV=False, IS_TESTING=True)
    def test_update_pro_contact_without_mock(self):
        # Avoid pytest.PytestUnraisableExceptionWarning: Exception ignored in: <ssl.SSLSocket ...>
        warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

        # This test helps to check data received in Sendinblue dashboard manually.
        # Note that SENDINBLUE_API_KEY must be filled in settings.
        make_update_request(
            sendinblue_tasks.UpdateSendinblueContactRequest(
                email=f"test.pro.{datetime.utcnow().strftime('%y%m%d.%H%M')}@example.net",
                use_pro_subaccount=True,
                attributes=format_user_attributes(common_pro_attributes),
                contact_list_ids=None,
                emailBlacklisted=False,
            )
        )

    def test_make_update_request(self):
        email = f"test.pro.{datetime.utcnow().strftime('%y%m%d.%H%M')}@example.net"
        attributes = format_user_attributes(common_pro_attributes)

        make_update_request(
            sendinblue_tasks.UpdateSendinblueContactRequest(
                email=email,
                use_pro_subaccount=True,
                attributes=attributes,
                contact_list_ids=None,
                emailBlacklisted=False,
            )
        )

        assert sendinblue_testing.sendinblue_requests[0] == {
            "email": email,
            "attributes": attributes,
            "emailBlacklisted": False,
            "use_pro_subaccount": True,
        }
