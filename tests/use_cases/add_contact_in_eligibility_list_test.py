from unittest.mock import MagicMock

import pytest

from pcapi.domain.beneficiary_contact.beneficiary_contact import BeneficiaryContact
from pcapi.infrastructure.services.notification.mailjet_notification_service import MailjetNotificationService
from pcapi.use_cases.add_contact_in_eligiblity_list import AddContactInEligibilityList


class AddContactInEligibilityListTest:
    def setup_method(self):
        self.notification_service = MailjetNotificationService()
        self.notification_service.create_mailing_contact = MagicMock()
        self.notification_service.add_contact_to_eligible_soon_list = MagicMock()
        self.add_contact_in_eligibility_list = AddContactInEligibilityList(
            notification_service=self.notification_service
        )

    def test_create_mailing_contact(self, app):
        # Given
        contact_email = "beneficiary@example.com"
        contact_date_of_birth = "2003-03-05"
        contact_department_code = "98"
        beneficiary_contact = BeneficiaryContact(contact_email, contact_date_of_birth, contact_department_code)

        # When
        self.add_contact_in_eligibility_list.execute(
            contact_email=contact_email,
            contact_date_of_birth=contact_date_of_birth,
            contact_department_code=contact_department_code,
        )

        # Then
        beneficiary_contact_params = self.notification_service.create_mailing_contact.call_args[0][0]
        self.notification_service.create_mailing_contact.assert_called_once()
        assert isinstance(beneficiary_contact_params, BeneficiaryContact)
        assert beneficiary_contact_params.email == contact_email
        assert beneficiary_contact_params.date_of_birth == contact_date_of_birth
        assert beneficiary_contact_params.department_code == contact_department_code

    def test_add_contact_to_eligible_soon_list(self, app):
        # Given
        contact_email = "beneficiary@example.com"
        contact_date_of_birth = "2003-03-05"
        contact_department_code = "98"
        beneficiary_contact = BeneficiaryContact(contact_email, contact_date_of_birth, contact_department_code)

        # When
        self.add_contact_in_eligibility_list.execute(
            contact_email=contact_email,
            contact_date_of_birth=contact_date_of_birth,
            contact_department_code=contact_department_code,
        )

        # Then
        beneficiary_contact_params = self.notification_service.add_contact_to_eligible_soon_list.call_args[0][0]
        self.notification_service.add_contact_to_eligible_soon_list.assert_called_once()
        assert isinstance(beneficiary_contact_params, BeneficiaryContact)
        assert beneficiary_contact_params.email == contact_email
        assert beneficiary_contact_params.date_of_birth == contact_date_of_birth
        assert beneficiary_contact_params.department_code == contact_department_code
