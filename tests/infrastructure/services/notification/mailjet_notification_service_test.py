from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from pcapi.domain.beneficiary_contact.beneficiary_contact import BeneficiaryContact
from pcapi.domain.beneficiary_contact.beneficiary_contact_exceptions import AddNewBeneficiaryContactException
from pcapi.infrastructure.services.notification.mailjet_notification_service import MailjetNotificationService


MOCK_MAILJET_LIST_ID = "mailjetListId"


class MailjetNotificationServiceTest:
    class CreateMailingContactTest:
        def setup_method(self):
            self.notification_service = MailjetNotificationService()

        @patch("pcapi.core.mails.create_contact")
        @patch("pcapi.core.mails.update_contact")
        def test_call_create_contact_from_mailing_and_add_informations(
            self, update_contact_mock, create_contact_mock, app
        ):
            # Given
            beneficiary_contact = BeneficiaryContact("beneficiary@example.com", "2003-03-05", "98")
            mock_response_create = Mock()
            mock_response_informations = Mock()
            mock_response_create.status_code = 201
            mock_response_informations.status_code = 200

            create_contact_mock.return_value = mock_response_create
            update_contact_mock.return_value = mock_response_informations

            # When
            self.notification_service.create_mailing_contact(beneficiary_contact)

            # Then
            create_contact_mock.assert_called_once_with(beneficiary_contact.email)
            update_contact_mock.assert_called_once_with(
                beneficiary_contact.email, birth_date=datetime(2003, 3, 5), department="98"
            )

        @patch("pcapi.core.mails.create_contact")
        def test_raises_error_on_creation_when_status_code_not_201_or_400(self, create_contact_mock):
            # Given
            beneficiary_contact = BeneficiaryContact("beneficiary@example.com", "2003-03-05", "98")
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.reason = "Error creating contact"

            create_contact_mock.return_value = mock_response

            # When
            with pytest.raises(AddNewBeneficiaryContactException) as error:
                self.notification_service.create_mailing_contact(beneficiary_contact)

            # Then
            assert error.value.errors["mailjet"] == ["Error creating contact"]

    class AddContactToEligibleSoonListTest:
        def setup_method(self):
            self.notification_service = MailjetNotificationService()

        @patch("pcapi.settings.MAILJET_NOT_YET_ELIGIBLE_LIST_ID", MOCK_MAILJET_LIST_ID)
        @patch("pcapi.core.mails.add_contact_to_list")
        def test_call_add_contact_to_list(self, add_contact_to_list_mock):
            # Given
            beneficiary_contact = BeneficiaryContact("beneficiary@example.com", "2003-03-05", "98")
            mock_response = Mock()
            mock_response.status_code = 201
            add_contact_to_list_mock.return_value = mock_response

            # When
            self.notification_service.add_contact_to_eligible_soon_list(beneficiary_contact)

            # Then
            add_contact_to_list_mock.assert_called_once_with(beneficiary_contact.email, MOCK_MAILJET_LIST_ID)

        @patch("pcapi.settings.MAILJET_NOT_YET_ELIGIBLE_LIST_ID", MOCK_MAILJET_LIST_ID)
        @patch("pcapi.core.mails.add_contact_to_list")
        def test_raises_error_on_list_addition_when_status_code_not_201_or_400(self, add_contact_to_list_mock):
            # Given
            beneficiary_contact = BeneficiaryContact("beneficiary@example.com", "2003-03-05", "98")
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.reason = "Error adding to list"

            add_contact_to_list_mock.return_value = mock_response
            # When
            with pytest.raises(AddNewBeneficiaryContactException) as error:
                self.notification_service.add_contact_to_eligible_soon_list(beneficiary_contact)

            # Then
            assert error.value.errors["mailjet"] == ["Error adding to list"]
