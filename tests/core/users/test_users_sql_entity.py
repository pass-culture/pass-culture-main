from datetime import datetime

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.models import ApiErrors
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
def test_cannot_create_admin_that_can_book(app):
    # Given
    user = users_factories.UserFactory.build(isBeneficiary=True, isAdmin=True)

    # When
    with pytest.raises(ApiErrors):
        repository.save(user)


@pytest.mark.usefixtures("db_session")
class HasAccessTest:
    def test_does_not_have_access_if_not_attached(self):
        offerer = offers_factories.OffererFactory()
        user = users_factories.UserFactory()

        assert not user.has_access(offerer.id)

    def test_does_not_have_access_if_not_validated(self, app):
        user_offerer = offers_factories.UserOffererFactory(validationToken="token")
        offerer = user_offerer.offerer
        user = user_offerer.user

        assert not user.has_access(offerer.id)

    def test_has_access(self):
        user_offerer = offers_factories.UserOffererFactory()
        offerer = user_offerer.offerer
        user = user_offerer.user

        assert user.has_access(offerer.id)

    def test_has_access_if_admin(self):
        # given
        offerer = offers_factories.OffererFactory()
        admin = users_factories.UserFactory(isAdmin=True)

        assert admin.has_access(offerer.id)


class WalletBalanceTest:
    @pytest.mark.usefixtures("db_session")
    def test_balance_is_0_with_no_deposits_and_no_bookings(self):
        # given
        user = users_factories.UserFactory()
        repository.delete(user.deposit)

        # then
        assert user.wallet_balance == 0
        assert user.real_wallet_balance == 0

    @pytest.mark.usefixtures("db_session")
    def test_balance_is_the_sum_of_deposits_if_no_bookings(self):
        # given
        user = users_factories.UserFactory(deposit__version=1)
        payments_factories.DepositFactory(user=user, version=1)

        # then
        assert user.wallet_balance == 500 + 500
        assert user.real_wallet_balance == 500 + 500

    @pytest.mark.usefixtures("db_session")
    def test_balance_count_non_expired_deposits(self):
        # given
        user = users_factories.UserFactory(deposit__version=1, deposit__expirationDate=None)

        # then
        assert user.wallet_balance == 500
        assert user.real_wallet_balance == 500

    @pytest.mark.usefixtures("db_session")
    def test_balance_ignores_expired_deposits(self):
        # given
        user = users_factories.UserFactory(deposit__version=1, deposit__expirationDate=datetime(2000, 1, 1))

        # then
        assert user.wallet_balance == 0
        assert user.real_wallet_balance == 0

    @pytest.mark.usefixtures("db_session")
    def test_balance(self):
        # given
        user = users_factories.UserFactory(deposit__version=1)
        bookings_factories.BookingFactory(user=user, isUsed=True, quantity=1, amount=10)
        bookings_factories.BookingFactory(user=user, isUsed=True, quantity=2, amount=20)
        bookings_factories.BookingFactory(user=user, isUsed=False, quantity=3, amount=30)
        bookings_factories.BookingFactory(user=user, isCancelled=True, quantity=4, amount=40)

        # then
        assert user.wallet_balance == 500 - (10 + 2 * 20 + 3 * 30)
        assert user.real_wallet_balance == 500 - (10 + 2 * 20)

    @pytest.mark.usefixtures("db_session")
    def test_real_balance_with_only_used_bookings(self):
        # given
        user = users_factories.UserFactory(deposit__version=1)
        bookings_factories.BookingFactory(user=user, isUsed=False, quantity=1, amount=30)

        # then
        assert user.wallet_balance == 500 - 30
        assert user.real_wallet_balance == 500

    @pytest.mark.usefixtures("db_session")
    def test_balance_should_not_be_negative(self):
        # given
        user = users_factories.UserFactory(deposit__version=1)
        bookings_factories.BookingFactory(user=user, isUsed=True, quantity=1, amount=10)
        deposit = user.deposit
        deposit.expirationDate = datetime(2000, 1, 1)

        # then
        assert user.wallet_balance == 0
        assert user.real_wallet_balance == 0


class HasPhysicalVenuesTest:
    @pytest.mark.usefixtures("db_session")
    def test_webapp_user_has_no_venue(self, app):
        # given
        user = users_factories.UserFactory.build()

        # when
        repository.save(user)

        # then
        assert user.hasPhysicalVenues is False

    @pytest.mark.usefixtures("db_session")
    def test_pro_user_has_one_digital_venue_by_default(self, app):
        # given
        user = users_factories.UserFactory.build()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        offerer_venue = create_venue(offerer, is_virtual=True, siret=None)

        # when
        repository.save(offerer_venue, user_offerer)

        # then
        assert user.hasPhysicalVenues is False

    @pytest.mark.usefixtures("db_session")
    def test_pro_user_has_one_digital_venue_and_a_physical_venue(self, app):
        # given
        user = users_factories.UserFactory.build()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        offerer_virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        offerer_physical_venue = create_venue(offerer)
        repository.save(offerer_virtual_venue, offerer_physical_venue, user_offerer)

        # then
        assert user.hasPhysicalVenues is True


class needsToSeeTutorialsTest:
    @pytest.mark.usefixtures("db_session")
    def test_beneficiary_has_to_see_tutorials_when_not_already_seen(self, app):
        # given
        user = users_factories.UserFactory.build(isBeneficiary=True, hasSeenTutorials=False)
        # when
        repository.save(user)
        # then
        assert user.needsToSeeTutorials is True

    @pytest.mark.usefixtures("db_session")
    def test_beneficiary_has_not_to_see_tutorials_when_already_seen(self, app):
        # given
        user = users_factories.UserFactory.build(isBeneficiary=True, hasSeenTutorials=True)
        # when
        repository.save(user)
        # then
        assert user.needsToSeeTutorials is False

    @pytest.mark.usefixtures("db_session")
    def test_pro_user_has_not_to_see_tutorials_when_already_seen(self, app):
        # given
        user = users_factories.UserFactory.build(isBeneficiary=False)
        # when
        repository.save(user)
        # then
        assert user.needsToSeeTutorials is False


class CalculateAgeTest:
    @freeze_time("2018-06-01")
    def test_user_age(self):
        assert users_factories.UserFactory.build(dateOfBirth=None).age is None
        assert users_factories.UserFactory.build(dateOfBirth=datetime(2000, 6, 1, 5, 1)).age == 18  # happy birthday
        assert users_factories.UserFactory.build(dateOfBirth=datetime(1999, 7, 1)).age == 18
        assert users_factories.UserFactory.build(dateOfBirth=datetime(2000, 7, 1)).age == 17
        assert users_factories.UserFactory.build(dateOfBirth=datetime(1999, 5, 1)).age == 19

    def test_eligibility_start_end_datetime(self):
        assert users_factories.UserFactory.build(dateOfBirth=None).eligibility_start_datetime is None
        assert users_factories.UserFactory.build(
            dateOfBirth=datetime(2000, 6, 1, 5, 1)
        ).eligibility_start_datetime == datetime(2018, 6, 1, 0, 0)

        assert users_factories.UserFactory.build(dateOfBirth=None).eligibility_end_datetime is None
        assert users_factories.UserFactory.build(
            dateOfBirth=datetime(2000, 6, 1, 5, 1)
        ).eligibility_end_datetime == datetime(2019, 6, 1, 0, 0)


@pytest.mark.usefixtures("db_session")
class DepositVersionTest:
    def test_return_the_deposit(self):
        # given
        user = users_factories.UserFactory(deposit__version=1)

        # then
        assert user.deposit_version == 1

    def test_when_no_deposit(self):
        # given
        user = users_factories.UserFactory()
        repository.delete(*user.deposits)

        # then
        assert user.deposit_version == None


@pytest.mark.usefixtures("db_session")
class NotificationSubscriptionsTest:
    def test_notification_subscriptions(self):
        user = users_factories.UserFactory(notificationSubscriptions={"marketing_push": False})

        assert not user.get_notification_subscriptions().marketing_push

    def test_void_notification_subscriptions(self):
        user = users_factories.UserFactory()
        assert user.notificationSubscriptions == {"marketing_push": True, "marketing_email": True}

        assert user.get_notification_subscriptions().marketing_push
