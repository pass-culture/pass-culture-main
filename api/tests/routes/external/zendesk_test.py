import logging
from datetime import datetime

import pytest

import pcapi.core.finance.factories as finance_factories
import pcapi.core.history.factories as history_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi import settings
from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.core.users import constants as user_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as users_testing
from pcapi.core.users.models import PhoneValidationStatusType


@pytest.mark.usefixtures("db_session")
class ZendeskWebhookTest:
    @pytest.mark.parametrize(
        "phone_number,postal_code", [("0612345678", 55270), ("06 12 34 56 78", None), ("+33612345678", 97600)]
    )
    def test_webhook_update_user_by_email(self, client, caplog, phone_number, postal_code):
        birth_year = datetime.utcnow().year - user_constants.ELIGIBILITY_AGE_18

        user = users_factories.BeneficiaryGrant18Factory(
            dateOfBirth=datetime(birth_year, 1, 2),
            phoneNumber=phone_number,
            postalCode=postal_code,
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )

        with caplog.at_level(logging.INFO):
            response = client.post(
                "/webhooks/zendesk/ticket_notification",
                json={
                    "is_new_ticket": True,
                    "ticket_id": 123,
                    "requester_id": 456,
                    "requester_email": user.email,
                    "requester_phone": None,
                },
            )

        expected_bo_url = f"{settings.BACKOFFICE_URL}/public-accounts/{user.id}"

        assert response.status_code == 204
        assert len(users_testing.zendesk_requests) == 2  # user attributes and internal note
        assert all(req["zendesk_user_id"] == 456 for req in users_testing.zendesk_requests)
        assert users_testing.zendesk_requests[0]["data"] == {
            "user": {
                "email": user.email,
                "phone": "+33612345678",
                "tags": ["BENEFICIARY", "actif", "id_check_terminé", "éligible"],
                "user_fields": {
                    "backoffice_url": expected_bo_url,
                    "user_id": user.id,
                    "first_name": user.firstName,
                    "last_name": user.lastName,
                    "postal_code": user.postalCode,
                    "date_of_birth": f"{birth_year}-01-02",
                    "suspended": "Non",
                    "email_validated": True,
                    "phone_validated": True,
                    "initial_credit": user.deposit.amount,
                    "remaining_credit": user.deposit.amount,
                },
            }
        }
        assert expected_bo_url in str(users_testing.zendesk_requests[1]["data"]["ticket"]["comment"]["html_body"])
        assert users_testing.zendesk_requests[1]["data"]["ticket"]["comment"]["public"] is False

        assert (
            caplog.records[0].message
            == "Zendesk webhook called: {'is_new_ticket': True, 'requester_id': '456', 'ticket_id': '123'}"
        )
        assert caplog.records[0].extra["is_new_ticket"] is True
        assert caplog.records[0].extra["requester_id"] == "456"
        assert caplog.records[0].extra["ticket_id"] == "123"
        assert "requester_email" not in caplog.records[0].extra
        assert "requester_phone" not in caplog.records[0].extra

    def test_webhook_update_user_by_phone(self, client):
        # not beneficiary, no credit, suspended
        user = users_factories.UserFactory(
            dateOfBirth=datetime(2004, 3, 2),
            phoneNumber="0634567890",
            phoneValidationStatus=None,
            isActive=False,
        )
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=datetime(2022, 3, 22, 15), reason=user_constants.SuspensionReason.FRAUD_HACK
        )

        response = client.post(
            "/webhooks/zendesk/ticket_notification",
            json={
                "is_new_ticket": False,
                "ticket_id": 124,
                "requester_id": 457,
                "requester_email": None,
                "requester_phone": "+33634567890",
            },
        )

        assert response.status_code == 204
        assert len(users_testing.zendesk_requests) == 1  # user attributes only (not a new ticket)
        assert users_testing.zendesk_requests[0]["zendesk_user_id"] == 457
        assert users_testing.zendesk_requests[0]["data"] == {
            "user": {
                "email": user.email,
                "phone": "+33634567890",
                "tags": ["suspendu"],
                "user_fields": {
                    "backoffice_url": f"{settings.BACKOFFICE_URL}/public-accounts/{user.id}",
                    "user_id": user.id,
                    "first_name": user.firstName,
                    "last_name": user.lastName,
                    "postal_code": user.postalCode,
                    "date_of_birth": "2004-03-02",
                    "suspended": "Oui - Fraude hacking (le 22/03/2022 à 15:00)",
                    "email_validated": True,
                    "phone_validated": False,
                    "initial_credit": 0,
                    "remaining_credit": 0,
                },
            }
        }

    def test_webhook_update_user_without_subscription_process(self, client):
        birth_year = datetime.utcnow().year - user_constants.ELIGIBILITY_AGE_18

        # first name, last name and phone number unknown
        user = users_factories.UserFactory(
            dateOfBirth=datetime(birth_year, 1, 2),
            firstName=None,
            lastName=None,
            phoneNumber=None,
            postalCode="06000",
        )

        response = client.post(
            "/webhooks/zendesk/ticket_notification",
            json={
                "is_new_ticket": True,
                "ticket_id": 125,
                "requester_id": 458,
                "requester_email": user.email,
                "requester_phone": None,
            },
        )

        expected_bo_url = f"{settings.BACKOFFICE_URL}/public-accounts/{user.id}"

        assert response.status_code == 204
        assert len(users_testing.zendesk_requests) == 2  # user attributes and internal note
        assert all(req["zendesk_user_id"] == 458 for req in users_testing.zendesk_requests)
        assert users_testing.zendesk_requests[0]["data"] == {
            "user": {
                "email": user.email,
                "phone": None,
                "tags": ["actif", "éligible"],
                "user_fields": {
                    "backoffice_url": expected_bo_url,
                    "user_id": user.id,
                    "first_name": user.firstName,
                    "last_name": user.lastName,
                    "postal_code": user.postalCode,
                    "date_of_birth": f"{birth_year}-01-02",
                    "suspended": "Non",
                    "email_validated": True,
                    "phone_validated": False,
                    "initial_credit": 0.0,
                    "remaining_credit": 0.0,
                },
            }
        }
        assert expected_bo_url in str(users_testing.zendesk_requests[1]["data"]["ticket"]["comment"]["html_body"])
        assert users_testing.zendesk_requests[1]["data"]["ticket"]["comment"]["public"] is False

    @pytest.mark.parametrize("pro_factory", [users_factories.ProFactory, users_factories.NonAttachedProFactory])
    def test_webhook_update_pro_by_user_email(self, client, pro_factory):
        pro_user = pro_factory(email="pro@example.com")
        venue = offerers_factories.VenueFactory(
            bookingEmail=pro_user.email, offererAddress__address__postalCode="75018"
        )

        response = client.post(
            "/webhooks/zendesk/ticket_notification",
            json={
                "is_new_ticket": True,
                "ticket_id": 125,
                "requester_id": 458,
                "requester_email": pro_user.email,
                "requester_phone": None,
            },
        )

        assert response.status_code == 204
        assert len(users_testing.zendesk_requests) == 2  # user attributes and internal note
        assert all(req["zendesk_user_id"] == 458 for req in users_testing.zendesk_requests)
        assert users_testing.zendesk_requests[0]["data"] == {
            "user": {
                "email": pro_user.email,
                "tags": ["PRO", "département_75"],
                "user_fields": {
                    "backoffice_url": f"{settings.BACKOFFICE_URL}/pro/user/{pro_user.id}",
                    "user_id": pro_user.id,
                    "first_name": pro_user.firstName,
                    "last_name": pro_user.lastName,
                    "postal_code": venue.offererAddress.address.postalCode,
                    "offerer_name": venue.managingOfferer.name,
                    "venue_name": venue.name,
                    "dms_application": "Aucun",
                },
            }
        }
        assert f"{settings.BACKOFFICE_URL}/pro/user/{pro_user.id}" in str(
            users_testing.zendesk_requests[1]["data"]["ticket"]["comment"]["html_body"]
        )
        assert users_testing.zendesk_requests[1]["data"]["ticket"]["comment"]["public"] is False

    def test_webhook_update_pro_by_booking_email(self, client):
        venue = offerers_factories.VenueFactory(
            bookingEmail="venue@example.com",
            offererAddress__address__postalCode="06600",
            offererAddress__address__departmentCode="06",
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue=venue,
            bankAccount=finance_factories.BankAccountFactory(status=BankAccountApplicationStatus.ACCEPTED),
        )

        response = client.post(
            "/webhooks/zendesk/ticket_notification",
            json={
                "is_new_ticket": True,
                "ticket_id": 126,
                "requester_id": 459,
                "requester_email": venue.bookingEmail,
                "requester_phone": None,
            },
        )

        assert response.status_code == 204
        assert len(users_testing.zendesk_requests) == 2  # user attributes and internal note
        assert all(req["zendesk_user_id"] == 459 for req in users_testing.zendesk_requests)
        assert users_testing.zendesk_requests[0]["data"] == {
            "user": {
                "email": venue.bookingEmail,
                "tags": ["PRO", "département_06"],
                "user_fields": {
                    "backoffice_url": f"{settings.BACKOFFICE_URL}/pro/venue/{venue.id}",
                    "user_id": None,
                    "first_name": None,
                    "last_name": None,
                    "postal_code": venue.offererAddress.address.postalCode,
                    "offerer_name": venue.managingOfferer.name,
                    "venue_name": venue.name,
                    "dms_application": "Approuvé",
                },
            }
        }
        assert f"{settings.BACKOFFICE_URL}/pro/venue/{venue.id}" in str(
            users_testing.zendesk_requests[1]["data"]["ticket"]["comment"]["html_body"]
        )
        assert users_testing.zendesk_requests[1]["data"]["ticket"]["comment"]["public"] is False

    @pytest.mark.parametrize("is_new_ticket", [True, False])
    def test_webhook_unknown_user(self, client, is_new_ticket):
        users_factories.BeneficiaryGrant18Factory()

        response = client.post(
            "/webhooks/zendesk/ticket_notification",
            json={
                "is_new_ticket": is_new_ticket,
                "ticket_id": 123,
                "requester_id": 456,
                "requester_email": "me@example.com",
                "requester_phone": None,
            },
        )

        assert response.status_code == 204
        assert len(users_testing.zendesk_requests) == 0

    def test_webhook_missing_requester_id(self, client):
        user = users_factories.BeneficiaryGrant18Factory()

        response = client.post(
            "/webhooks/zendesk/ticket_notification",
            json={"is_new_ticket": True, "ticket_id": 123, "requester_email": user.email, "requester_phone": None},
        )

        assert response.status_code == 400
        assert len(users_testing.zendesk_requests) == 0

    def test_webhook_missing_email_or_phone(self, client):
        response = client.post(
            "/webhooks/zendesk/ticket_notification",
            json={
                "is_new_ticket": False,
                "ticket_id": 123,
                "requester_id": 456,
                "requester_email": None,
                "requester_phone": None,
            },
        )

        assert response.status_code == 400
        assert len(users_testing.zendesk_requests) == 0
