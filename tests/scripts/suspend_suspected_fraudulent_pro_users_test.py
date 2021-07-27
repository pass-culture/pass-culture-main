import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.factories import UserOffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.factories import AdminFactory
from pcapi.core.users.factories import UserFactory
from pcapi.scripts.suspend_fraudulent_pro_users import suspend_fraudulent_pro_by_email_providers


@pytest.mark.usefixtures("db_session")
def test_suspend_pros_in_given_emails_providers_list():
    # Given
    fraudulent_emails_providers = ["example.com"]
    admin_user = AdminFactory(email="admin@example.net")
    fraudulent_user = UserFactory(
        isBeneficiary=False,
        email="jesuisunefraude@example.com",
    )
    offerer = OffererFactory()
    UserOffererFactory(user=fraudulent_user, offerer=offerer)

    # When
    suspend_fraudulent_pro_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

    # Then
    assert not fraudulent_user.isActive


@pytest.mark.usefixtures("db_session")
def test_only_suspend_pro_users_in_given_emails_providers_list():
    # Given
    fraudulent_emails_providers = ["example.com"]
    admin_user = AdminFactory(email="admin@example.net")
    pro_fraudulent_user_with_uppercase_domain = UserFactory(isBeneficiary=False, email="jesuisunefraude@EXAmple.com")
    pro_fraudulent_user_with_subdomain = UserFactory(isBeneficiary=False, email="jesuisunefraude@sub.example.com")
    beneficiary_fraudulent_user = UserFactory(isBeneficiary=True, email="jesuisuneautrefraude@example.com")
    offerer1 = OffererFactory()
    UserOffererFactory(user=pro_fraudulent_user_with_uppercase_domain, offerer=offerer1)
    offerer2 = OffererFactory()
    UserOffererFactory(user=pro_fraudulent_user_with_subdomain, offerer=offerer2)

    # When
    suspend_fraudulent_pro_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

    # Then
    assert not pro_fraudulent_user_with_uppercase_domain.isActive
    assert not pro_fraudulent_user_with_subdomain.isActive
    assert beneficiary_fraudulent_user.isActive


@pytest.mark.usefixtures("db_session")
def test_dont_suspend_users_not_in_given_emails_providers_list():
    # Given
    fraudulent_emails_providers = ["example.com"]
    admin_user = AdminFactory(email="admin@example.net")
    non_fraudulent_pro = UserFactory(isBeneficiary=False, email="jenesuispasunefraude@gmoil.com")

    # When
    suspend_fraudulent_pro_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

    # Then
    assert non_fraudulent_pro.isActive


@pytest.mark.usefixtures("db_session")
def test_suspend_pro_user_with_many_offerers_and_delete_all_offerers():
    fraudulent_emails_providers = ["example.com"]
    admin_user = AdminFactory(email="admin@example.net")
    fraudulent_user = UserFactory(
        isBeneficiary=False,
        email="jesuisunefraude@example.com",
    )
    first_offerer = OffererFactory()
    UserOffererFactory(user=fraudulent_user, offerer=first_offerer)
    second_offerer = OffererFactory()
    UserOffererFactory(user=fraudulent_user, offerer=second_offerer)

    suspend_fraudulent_pro_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

    assert not fraudulent_user.isActive
    assert Offerer.query.count() == 0


@pytest.mark.usefixtures("db_session")
def test_delete_offerer_and_venue():
    # Given
    fraudulent_emails_providers = ["example.com"]
    admin_user = AdminFactory(email="admin@example.net")
    fraudulent_user = UserFactory(
        isBeneficiary=False,
        email="jesuisunefraude@example.com",
    )
    offerer = OffererFactory()
    UserOffererFactory(user=fraudulent_user, offerer=offerer)
    VenueFactory(managingOfferer=offerer)

    # When
    suspend_fraudulent_pro_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

    # Then
    assert Offerer.query.count() == 0
    assert Venue.query.count() == 0


@pytest.mark.usefixtures("db_session")
def test_cancel_bookings_when_offerer_has_one_or_more():
    # Given
    fraudulent_emails_providers = ["example.com"]
    admin_user = AdminFactory(email="admin@example.net")
    beneficiary1 = UserFactory(email="beneficiary1@example.net")
    beneficiary2 = UserFactory(email="beneficiary2@example.net")
    fraudulent_user = UserFactory(
        isBeneficiary=False,
        email="jesuisunefraude@example.com",
    )
    offerer_with_bookings = OffererFactory()
    UserOffererFactory(user=fraudulent_user, offerer=offerer_with_bookings)
    offer1 = OfferFactory(venue__managingOfferer=offerer_with_bookings)
    offer2 = OfferFactory(venue__managingOfferer=offerer_with_bookings)
    stock1 = StockFactory(offer=offer1)
    stock2 = StockFactory(offer=offer2)
    booking1 = BookingFactory(user=beneficiary1, stock=stock1)
    booking2 = BookingFactory(user=beneficiary2, stock=stock2)

    # When
    suspend_fraudulent_pro_by_email_providers(fraudulent_emails_providers, admin_user, dry_run=False)

    # Then
    assert Offerer.query.count() == 1
    assert Venue.query.count() == 2
    assert Offer.query.count() == 2
    assert Stock.query.count() == 2
    assert Booking.query.count() == 2
    assert booking1.isCancelled
    assert booking1.status is BookingStatus.CANCELLED
    assert booking1.cancellationReason is BookingCancellationReasons.FRAUD
    assert booking2.isCancelled
    assert booking2.status is BookingStatus.CANCELLED
    assert booking2.cancellationReason is BookingCancellationReasons.FRAUD
