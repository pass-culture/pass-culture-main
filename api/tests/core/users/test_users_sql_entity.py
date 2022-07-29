from datetime import datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
from psycopg2 import errors as psycog2_errors
import pytest
from sqlalchemy import func
import sqlalchemy.exc

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.payments import api as payments_api
from pcapi.core.payments.models import DepositType
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as user_models
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
def test_cannot_create_admin_that_can_book():
    # Given
    user = users_factories.UserFactory.build(roles=[user_models.UserRole.BENEFICIARY, user_models.UserRole.ADMIN])

    # When
    with pytest.raises(ApiErrors):
        repository.save(user)


@pytest.mark.usefixtures("db_session")
class HasAccessTest:
    def test_does_not_have_access_if_not_attached(self):
        offerer = offerers_factories.OffererFactory()
        user = users_factories.UserFactory()

        assert not user.has_access(offerer.id)

    def test_does_not_have_access_if_not_validated(self):
        user_offerer = offerers_factories.UserOffererFactory(validationToken="token")
        offerer = user_offerer.offerer
        user = user_offerer.user

        assert not user.has_access(offerer.id)

    def test_has_access(self):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer
        user = user_offerer.user

        assert user.has_access(offerer.id)

    def test_has_access_if_admin(self):
        # given
        offerer = offerers_factories.OffererFactory()
        admin = users_factories.AdminFactory()

        assert admin.has_access(offerer.id)


class WalletBalanceTest:
    @pytest.mark.usefixtures("db_session")
    def test_balance_is_0_with_no_deposits_and_no_bookings(self):
        # given
        user = users_factories.UserFactory()

        # then
        assert user.wallet_balance == 0
        assert user.real_wallet_balance == 0

    @pytest.mark.usefixtures("db_session")
    def test_balance_ignores_expired_deposits(self):
        # given
        user = users_factories.BeneficiaryGrant18Factory(deposit__expirationDate=datetime(2000, 1, 1))

        # then
        assert user.wallet_balance == 0
        assert user.real_wallet_balance == 0

    @pytest.mark.usefixtures("db_session")
    def test_balance(self):
        # given
        user = users_factories.BeneficiaryGrant18Factory()
        bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user, quantity=1, amount=10)
        bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user, quantity=2, amount=20)
        bookings_factories.IndividualBookingFactory(individualBooking__user=user, quantity=3, amount=30)
        bookings_factories.CancelledIndividualBookingFactory(individualBooking__user=user, quantity=4, amount=40)

        # then
        assert user.wallet_balance == 300 - (10 + 2 * 20 + 3 * 30)
        assert user.real_wallet_balance == 300 - (10 + 2 * 20)

    @pytest.mark.usefixtures("db_session")
    def test_real_balance_with_only_used_bookings(self):
        # given
        user = users_factories.BeneficiaryGrant18Factory()
        bookings_factories.IndividualBookingFactory(individualBooking__user=user, quantity=1, amount=30)

        # then
        assert user.wallet_balance == 300 - 30
        assert user.real_wallet_balance == 300

    @pytest.mark.usefixtures("db_session")
    def test_balance_when_expired(self):
        # given
        user = users_factories.BeneficiaryGrant18Factory()
        bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user, quantity=1, amount=10)
        deposit = user.deposit
        deposit.expirationDate = datetime(2000, 1, 1)

        # then
        assert user.wallet_balance == 0
        assert user.real_wallet_balance == 0


@pytest.mark.usefixtures("db_session")
class SQLFunctionsTest:
    def test_wallet_balance(self):
        with freeze_time(datetime.utcnow() - relativedelta(years=2, days=2)):
            user = users_factories.UnderageBeneficiaryFactory(subscription_age=16)
            # disable trigger because deposit.expirationDate > now() is False in database time
            db.session.execute("ALTER TABLE booking DISABLE TRIGGER booking_update;")
            bookings_factories.IndividualBookingFactory(individualBooking__user=user, amount=18)
            db.session.execute("ALTER TABLE booking ENABLE TRIGGER booking_update;")

        payments_api.create_deposit(user, "test", user_models.EligibilityType.AGE18)

        bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user, amount=10)
        bookings_factories.IndividualBookingFactory(individualBooking__user=user, amount=1)

        assert db.session.query(func.get_wallet_balance(user.id, False)).first()[0] == Decimal(289)
        assert db.session.query(func.get_wallet_balance(user.id, True)).first()[0] == Decimal(290)

    def test_wallet_balance_no_deposit(self):
        user = users_factories.UserFactory()

        assert db.session.query(func.get_wallet_balance(user.id, False)).first()[0] == 0

    def test_wallet_balance_multiple_deposits(self):
        user = users_factories.UserFactory()
        users_factories.DepositGrantFactory(user=user, type=DepositType.GRANT_15_17)
        users_factories.DepositGrantFactory(user=user, type=DepositType.GRANT_18)

        with pytest.raises((psycog2_errors.CardinalityViolation, sqlalchemy.exc.ProgrammingError)) as exc:
            # pylint: disable=expression-not-assigned
            db.session.query(func.get_wallet_balance(user.id, False)).first()[0]

        assert "more than one row returned by a subquery" in str(exc.value)

    def test_wallet_balance_expired_deposit(self):
        with freeze_time(datetime.utcnow() - relativedelta(years=2, days=2)):
            user = users_factories.UnderageBeneficiaryFactory(subscription_age=16)
            # disable trigger because deposit.expirationDate > now() is False in database time
            db.session.execute("ALTER TABLE booking DISABLE TRIGGER booking_update;")
            bookings_factories.IndividualBookingFactory(individualBooking__user=user, amount=18)
            db.session.execute("ALTER TABLE booking ENABLE TRIGGER booking_update;")

        assert db.session.query(func.get_wallet_balance(user.id, False)).first()[0] == 0

    def test_deposit_balance(self):
        deposit = users_factories.DepositGrantFactory()

        bookings_factories.UsedIndividualBookingFactory(individualBooking__deposit=deposit, amount=10)
        bookings_factories.IndividualBookingFactory(individualBooking__deposit=deposit, amount=1)

        assert db.session.query(func.get_deposit_balance(deposit.id, False)).first()[0] == 289
        assert db.session.query(func.get_deposit_balance(deposit.id, True)).first()[0] == 290

    def test_deposit_balance_wrong_id(self):
        with pytest.raises(sqlalchemy.exc.InternalError) as exc:
            # pylint: disable=expression-not-assigned
            db.session.query(func.get_deposit_balance(None, False)).first()[0]

        assert "the deposit was not found" in str(exc)


class CalculateAgeTest:
    @freeze_time("2018-06-01")
    def test_user_age(self):
        assert users_factories.UserFactory.build(dateOfBirth=None).age is None
        assert users_factories.UserFactory.build(dateOfBirth=datetime(2000, 6, 1, 5, 1)).age == 18  # happy birthday
        assert users_factories.UserFactory.build(dateOfBirth=datetime(1999, 7, 1)).age == 18
        assert users_factories.UserFactory.build(dateOfBirth=datetime(2000, 7, 1)).age == 17
        assert users_factories.UserFactory.build(dateOfBirth=datetime(1999, 5, 1)).age == 19


@pytest.mark.usefixtures("db_session")
class DepositVersionTest:
    def test_return_the_deposit(self):
        # given
        user = users_factories.BeneficiaryGrant18Factory(deposit__version=1)

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
