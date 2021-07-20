import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.users.factories import UserFactory
from pcapi.scripts.suspend_fraudulent_beneficiary_users import suspend_fraudulent_beneficiary_users_by_email_providers


class SuspendFraudulentBeneficiaryUsersByEmailProvidersTest:
    @pytest.mark.usefixtures("db_session")
    def test_suspend_users_in_given_emails_providers_list(self):
        # Given
        fraudulent_emails_providers = ["example.com"]
        admin_user = UserFactory(isBeneficiary=False, isAdmin=True)
        fraudulent_user = UserFactory(
            isBeneficiary=True,
            email="jesuisunefraude@example.com",
        )
        BookingFactory(user=fraudulent_user, stock__price=1)
        BookingFactory(user=fraudulent_user, stock__price=2)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(
            fraudulent_emails_providers, admin_user.email, dry_run=False
        )

        # Then
        assert not fraudulent_user.isActive

    @pytest.mark.usefixtures("db_session")
    def test_cancel_bookings_of_suspended_users(self):
        # Given
        fraudulent_emails_providers = ["example.com"]
        admin_user = UserFactory(isBeneficiary=False, isAdmin=True)
        fraudulent_user = UserFactory(
            isBeneficiary=True,
            email="jesuisunefraude@example.com",
        )
        booking_1 = BookingFactory(user=fraudulent_user, stock__price=1)
        booking_2 = BookingFactory(user=fraudulent_user, stock__price=2)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(
            fraudulent_emails_providers, admin_user.email, dry_run=False
        )

        # Then
        assert not fraudulent_user.isActive
        assert booking_1.isCancelled
        assert booking_1.status is BookingStatus.CANCELLED
        assert booking_2.isCancelled
        assert booking_2.status is BookingStatus.CANCELLED

    @pytest.mark.usefixtures("db_session")
    def test_does_not_cancel_booking_when_not_cancellable(self):
        # Given
        fraudulent_emails_providers = ["example.com"]
        admin_user = UserFactory(isBeneficiary=False, isAdmin=True)
        fraudulent_user = UserFactory(
            isBeneficiary=True,
            email="jesuisunefraude@example.com",
        )
        uncancellable_booking = BookingFactory(user=fraudulent_user, stock__price=1, isUsed=True)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(
            fraudulent_emails_providers, admin_user.email, dry_run=False
        )

        # Then
        assert not fraudulent_user.isActive
        assert not uncancellable_booking.isCancelled
        assert uncancellable_booking.status is not BookingStatus.CANCELLED

    @pytest.mark.usefixtures("db_session")
    def test_only_suspend_beneficiary_users_in_given_emails_providers_list(self):
        # Given
        fraudulent_emails_providers = ["example.com"]
        admin_user = UserFactory(isBeneficiary=False, isAdmin=True)
        beneficiary_fraudulent_user = UserFactory(isBeneficiary=True, email="jesuisunefraude@example.com")
        beneficiary_fraudulent_user_with_uppercase_domain = UserFactory(
            isBeneficiary=True, email="jesuisunefraude@EXAmple.com"
        )
        beneficiary_fraudulent_user_with_subdomain = UserFactory(
            isBeneficiary=True, email="jesuisunefraude@sub.example.com"
        )
        non_beneficiary_fraudulent_user = UserFactory(isBeneficiary=False, email="jesuisuneautrefraude@example.com")
        BookingFactory(user=beneficiary_fraudulent_user, stock__price=1)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(
            fraudulent_emails_providers, admin_user.email, dry_run=False
        )

        # Then
        assert not beneficiary_fraudulent_user.isActive
        assert not beneficiary_fraudulent_user_with_uppercase_domain.isActive
        assert not beneficiary_fraudulent_user_with_subdomain.isActive
        assert non_beneficiary_fraudulent_user.isActive

    @pytest.mark.usefixtures("db_session")
    def test_dont_suspend_users_not_in_given_emails_providers_list(self):
        # Given
        fraudulent_emails_providers = ["gmoil.com"]
        admin_user = UserFactory(isBeneficiary=False, isAdmin=True)
        non_fraudulent_user = UserFactory(isBeneficiary=True, email="jenesuispasunefraude@example.com")
        BookingFactory(user=non_fraudulent_user, stock__price=1)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(
            fraudulent_emails_providers, admin_user.email, dry_run=False
        )

        # Then
        assert non_fraudulent_user.isActive
