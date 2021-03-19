import pytest

from pcapi.core.bookings import factories
import pcapi.core.users.factories as users_factories
from pcapi.scripts.suspend_fraudulent_beneficiary_users import suspend_fraudulent_beneficiary_users_by_email_providers


class SuspendFraudulentBeneficiaryUsersByEmailProvidersTest:
    @pytest.mark.usefixtures("db_session")
    def test_suspend_users_in_given_emails_providers_list(self):
        # Given
        fraudulent_emails_providers = ["example.com"]
        admin_user = users_factories.UserFactory(isBeneficiary=False, isAdmin=True)
        fraudulent_user = users_factories.UserFactory(
            isBeneficiary=True,
            email="jesuisunefraude@example.com",
        )
        factories.BookingFactory(user=fraudulent_user, stock__price=1)
        factories.BookingFactory(user=fraudulent_user, stock__price=2)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

        # Then
        assert fraudulent_user.isActive is False

    @pytest.mark.usefixtures("db_session")
    def test_only_suspend_beneficiary_users_in_given_emails_providers_list(self):
        # Given
        fraudulent_emails_providers = ["example.com"]
        admin_user = users_factories.UserFactory(isBeneficiary=False, isAdmin=True)
        beneficiary_fraudulent_user = users_factories.UserFactory(
            isBeneficiary=True, email="jesuisunefraude@example.com"
        )
        non_beneficiary_fraudulent_user = users_factories.UserFactory(
            isBeneficiary=False, email="jesuisuneautrefraude@example.com"
        )
        factories.BookingFactory(user=beneficiary_fraudulent_user, stock__price=1)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

        # Then
        assert beneficiary_fraudulent_user.isActive is False
        assert non_beneficiary_fraudulent_user.isActive is True

    @pytest.mark.usefixtures("db_session")
    def test_dont_suspend_users_not_in_given_emails_providers_list(self):
        # Given
        fraudulent_emails_providers = ["gmoil.com"]
        admin_user = users_factories.UserFactory(isBeneficiary=False, isAdmin=True)
        non_fraudulent_user = users_factories.UserFactory(isBeneficiary=True, email="jenesuispasunefraude@example.com")
        factories.BookingFactory(user=non_fraudulent_user, stock__price=1)

        # When
        suspend_fraudulent_beneficiary_users_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

        # Then
        assert non_fraudulent_user.isActive is True
