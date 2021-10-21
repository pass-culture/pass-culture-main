import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.factories import UsedBookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.users.factories import AdminFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.core.users.factories import UserFactory
from pcapi.scripts.suspend_fraudulent_beneficiary_users import suspend_fraudulent_beneficiary_users_by_email_providers
from pcapi.scripts.suspend_fraudulent_beneficiary_users import suspend_fraudulent_beneficiary_users_by_ids


class SuspendFraudulentBeneficiaryUsersByEmailProvidersTest:
    @pytest.mark.usefixtures("db_session")
    def test_suspend_users_in_given_emails_providers_list(self):
        # Given
        fraudulent_emails_providers = ["example.com"]
        admin_user = AdminFactory()
        fraudulent_user = BeneficiaryGrant18Factory(email="jesuisunefraude@example.com")
        BookingFactory(user=fraudulent_user, stock__price=1)
        BookingFactory(user=fraudulent_user, stock__price=2)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

        # Then
        assert not fraudulent_user.isActive

    @pytest.mark.usefixtures("db_session")
    def test_cancel_bookings_of_suspended_users(self):
        # Given
        fraudulent_emails_providers = ["example.com"]
        admin_user = AdminFactory()
        fraudulent_user = BeneficiaryGrant18Factory(email="jesuisunefraude@example.com")
        booking_1 = BookingFactory(user=fraudulent_user, stock__price=1)
        booking_2 = BookingFactory(user=fraudulent_user, stock__price=2)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

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
        admin_user = AdminFactory()
        fraudulent_user = BeneficiaryGrant18Factory(email="jesuisunefraude@example.com")
        uncancellable_booking = UsedBookingFactory(user=fraudulent_user, stock__price=1)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

        # Then
        assert not fraudulent_user.isActive
        assert not uncancellable_booking.isCancelled
        assert uncancellable_booking.status is not BookingStatus.CANCELLED

    @pytest.mark.usefixtures("db_session")
    def test_only_suspend_beneficiary_users_in_given_emails_providers_list(self):
        # Given
        fraudulent_emails_providers = ["example.com"]
        admin_user = AdminFactory()
        beneficiary_fraudulent_user = BeneficiaryGrant18Factory(email="jesuisunefraude@example.com")
        beneficiary_fraudulent_user_with_uppercase_domain = BeneficiaryGrant18Factory(
            email="jesuisunefraude@EXAmple.com"
        )
        beneficiary_fraudulent_user_with_subdomain = BeneficiaryGrant18Factory(email="jesuisunefraude@sub.example.com")
        non_beneficiary_fraudulent_user = UserFactory(email="jesuisuneautrefraude@example.com")
        BookingFactory(user=beneficiary_fraudulent_user, stock__price=1)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

        # Then
        assert not beneficiary_fraudulent_user.isActive
        assert not beneficiary_fraudulent_user_with_uppercase_domain.isActive

        # Do not handle sub-domains
        assert beneficiary_fraudulent_user_with_subdomain.isActive

        assert non_beneficiary_fraudulent_user.isActive

    @pytest.mark.usefixtures("db_session")
    def test_dont_suspend_users_not_in_given_emails_providers_list(self):
        # Given
        fraudulent_emails_providers = ["gmoil.com"]
        admin_user = AdminFactory()
        non_fraudulent_user = BeneficiaryGrant18Factory(email="jenesuispasunefraude@example.com")
        BookingFactory(user=non_fraudulent_user, stock__price=1)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

        # Then
        assert non_fraudulent_user.isActive


class SuspendFraudulentBeneficiaryUsersByIdsTest:
    @pytest.mark.usefixtures("db_session")
    def test_suspend_users_by_ids_in_given_user_ids_list(self):
        fraudulent_user_ids = [23]
        admin_user = AdminFactory()
        fraudulent_user = BeneficiaryGrant18Factory(id=23)
        fraudulent_user_booking_1 = BookingFactory(user=fraudulent_user, stock__price=1)
        fraudulent_user_booking_2 = BookingFactory(user=fraudulent_user, stock__price=2)

        suspend_fraudulent_beneficiary_users_by_ids(fraudulent_user_ids, admin_user, dry_run=False)

        assert not fraudulent_user.isActive
        assert fraudulent_user_booking_1.isCancelled
        assert fraudulent_user_booking_1.status is BookingStatus.CANCELLED
        assert fraudulent_user_booking_2.isCancelled
        assert fraudulent_user_booking_2.status is BookingStatus.CANCELLED

    @pytest.mark.usefixtures("db_session")
    def test_suspend_users_by_ids_does_not_cancel_bookings_when_not_cancellable(self):
        fraudulent_user_ids = [15]
        admin_user = AdminFactory()
        fraudulent_user = BeneficiaryGrant18Factory(id=15)
        uncancellable_booking = UsedBookingFactory(user=fraudulent_user, stock__price=1)

        suspend_fraudulent_beneficiary_users_by_ids(fraudulent_user_ids, admin_user, dry_run=False)

        assert not fraudulent_user.isActive
        assert not uncancellable_booking.isCancelled
        assert uncancellable_booking.status is not BookingStatus.CANCELLED

    @pytest.mark.usefixtures("db_session")
    def test_dont_suspend_users_not_in_given_user_ids_list(self):
        fraudulent_user_ids = [16]
        admin_user = AdminFactory()
        beneficiary = BeneficiaryGrant18Factory(id=15)

        suspend_fraudulent_beneficiary_users_by_ids(fraudulent_user_ids, admin_user, dry_run=False)

        assert beneficiary.isActive
