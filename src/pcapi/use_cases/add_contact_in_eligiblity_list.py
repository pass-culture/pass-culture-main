from pcapi.domain.beneficiary_contact.beneficiary_contact import BeneficiaryContact
from pcapi.domain.services.notification.notification_service import NotificationService


class AddContactInEligibilityList:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def execute(self, contact_email: str, contact_date_of_birth: str, contact_department_code: str):
        beneficiary_contact = BeneficiaryContact(contact_email, contact_date_of_birth, contact_department_code)
        self.notification_service.create_mailing_contact(beneficiary_contact)
        self.notification_service.add_contact_to_eligible_soon_list(beneficiary_contact)
