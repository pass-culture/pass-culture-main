from datetime import date
from datetime import datetime
from datetime import timedelta
import decimal

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as user_models
from pcapi.core.users.exceptions import InvalidUserRoleException
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.repository import repository


pytestmark = pytest.mark.usefixtures("db_session")


class UserTest:
    class DepositTest:
        def test_return_none_if_no_deposits_exists(self):
            user = users_factories.UserFactory()

            assert user.deposit == None

        def test_return_expired_deposit_if_only_expired_deposits_exists(self):
            user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18))
            user.add_beneficiary_role()
            yesterday = datetime.utcnow() - timedelta(days=1)
            users_factories.DepositGrantFactory(user=user, expirationDate=yesterday)

            assert user.deposit.type == finance_models.DepositType.GRANT_18

        def test_return_last_expired_deposit_if_only_expired_deposits_exists(self):
            with freeze_time(datetime.utcnow() - relativedelta(years=3)):
                user = users_factories.UnderageBeneficiaryFactory()

            users_factories.DepositGrantFactory(user=user)

            assert user.deposit.type == finance_models.DepositType.GRANT_18

    class UserRoleTest:
        def test_has_admin_role(self):
            user = users_factories.AdminFactory()

            assert user.has_admin_role
            assert user_models.User.query.filter(user_models.User.has_admin_role.is_(False)).all() == []
            assert user_models.User.query.filter(user_models.User.has_admin_role.is_(True)).all() == [user]

        def test_has_beneficiary_role(self):
            user = users_factories.BeneficiaryGrant18Factory()

            assert user.has_beneficiary_role
            assert user_models.User.query.filter(user_models.User.has_beneficiary_role.is_(False)).all() == []
            assert user_models.User.query.filter(user_models.User.has_beneficiary_role.is_(True)).all() == [user]

        def test_has_beneficiary_role_with_legacy_property(self):
            user = users_factories.UserFactory(roles=[user_models.UserRole.BENEFICIARY])

            assert user.has_beneficiary_role
            assert user_models.User.query.filter(user_models.User.has_beneficiary_role.is_(False)).all() == []
            assert user_models.User.query.filter(user_models.User.has_beneficiary_role.is_(True)).all() == [user]

        def test_has_pro_role(self):
            user = users_factories.ProFactory()

            assert user.has_pro_role
            assert user_models.User.query.filter(user_models.User.has_pro_role.is_(False)).all() == []
            assert user_models.User.query.filter(user_models.User.has_pro_role.is_(True)).all() == [user]

        def test_has_test_role(self):
            user = users_factories.UserFactory(roles=[user_models.UserRole.TEST])

            assert user.has_test_role
            assert user_models.User.query.filter(user_models.User.has_test_role.is_(False)).all() == []
            assert user_models.User.query.filter(user_models.User.has_test_role.is_(True)).all() == [user]

        def test_add_role_on_new_user(self):
            user = user_models.User()

            user.add_pro_role()

            assert user.has_pro_role

        def test_add_admin_role(self):
            user = users_factories.UserFactory.build()

            user.add_admin_role()

            assert user.has_admin_role

        def test_add_admin_role_only_once(self):
            user = users_factories.UserFactory.build()
            user.add_admin_role()

            user.add_admin_role()

            assert user.has_admin_role
            assert len(user.roles) == 1

        def test_add_beneficiary_role(self):
            user = users_factories.UserFactory.build()

            user.add_beneficiary_role()

            assert user.has_beneficiary_role

        def test_add_beneficiary_role_only_once(self):
            user = users_factories.UserFactory.build()
            user.add_beneficiary_role()

            user.add_beneficiary_role()

            assert user.has_beneficiary_role
            assert len(user.roles) == 1

        def test_add_pro_role(self):
            user = users_factories.UserFactory.build()

            user.add_pro_role()

            assert user.has_pro_role

        def test_add_pro_role_only_once(self):
            user = users_factories.UserFactory.build()
            user.add_pro_role()

            user.add_pro_role()

            assert user.has_pro_role
            assert len(user.roles) == 1

        def test_add_test_role(self):
            user = users_factories.UserFactory.build()

            user.add_test_role()

            assert user.has_test_role

        def test_cannot_add_beneficiary_role_to_an_admin(self):
            user = users_factories.AdminFactory()

            with pytest.raises(InvalidUserRoleException):
                user.add_beneficiary_role()

                assert not user.has_beneficiary_role
                assert user.has_admin_role

        def test_cannot_add_admin_role_to_a_beneficiary(self):
            user = users_factories.BeneficiaryGrant18Factory.build()

            with pytest.raises(InvalidUserRoleException):
                user.add_admin_role()

                assert user.has_beneficiary_role
                assert not user.has_admin_role

        def test_remove_admin_role(self):
            user = users_factories.AdminFactory.build()

            user.remove_admin_role()

            assert not user.has_admin_role

        def test_remove_admin_role_when_user_is_not_admin(self):
            user = users_factories.BeneficiaryGrant18Factory.build()

            user.remove_admin_role()

            assert user.has_beneficiary_role
            assert not user.has_admin_role

        def test_remove_beneficiary_role(self):
            user = users_factories.BeneficiaryGrant18Factory.build()

            user.remove_beneficiary_role()

            assert not user.has_beneficiary_role

        def test_remove_beneficiary_role_when_user_is_not_beneficiary(self):
            user = users_factories.ProFactory.build()

            user.remove_beneficiary_role()

            assert user.has_pro_role
            assert not user.has_beneficiary_role

        def test_remove_pro_role(self):
            user = users_factories.ProFactory.build()

            user.remove_pro_role()

            assert not user.has_pro_role

        def test_remove_pro_role_when_user_is_not_pro(self):
            user = users_factories.BeneficiaryGrant18Factory.build()

            user.remove_pro_role()

            assert user.has_beneficiary_role
            assert not user.has_pro_role

    class UserAgeTest:
        @pytest.mark.parametrize(
            "birth_date,today,latest_birthday",
            [
                (date(2000, 1, 1), date(2019, 12, 31), date(2019, 1, 1)),
                (date(2000, 1, 1), date(2020, 1, 1), date(2020, 1, 1)),
                (date(2000, 1, 1), date(2020, 1, 2), date(2020, 1, 1)),
                # february 29th, leap year
                (date(2000, 2, 29), date(2020, 2, 28), date(2019, 2, 28)),
                (date(2000, 2, 29), date(2020, 3, 1), date(2020, 2, 29)),
                # february 29th, previous year is a leap year
                (date(2000, 2, 29), date(2021, 2, 27), date(2020, 2, 29)),
                (date(2000, 2, 29), date(2021, 2, 28), date(2021, 2, 28)),
                (date(2000, 2, 29), date(2021, 3, 1), date(2021, 2, 28)),
            ],
        )
        def test_get_birthday_with_leap_year(self, birth_date, today, latest_birthday):
            with freeze_time(today):
                assert user_models._get_latest_birthday(birth_date) == latest_birthday

    class EligibilityTest:
        def test_received_pass_15_17(self):
            dateOfBirth = datetime.utcnow() - relativedelta(years=16, days=1)
            user = users_factories.UserFactory(dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth)
            user.add_beneficiary_role()
            yesterday = datetime.utcnow() - timedelta(days=1)
            users_factories.DepositGrantFactory(user=user, expirationDate=yesterday)
            assert user.received_pass_15_17 is True
            assert user.received_pass_18 is False

        def test_received_pass_18(self):
            dateOfBirth = datetime.utcnow() - relativedelta(years=18, days=1)
            user = users_factories.UserFactory(dateOfBirth=dateOfBirth, validatedBirthDate=dateOfBirth)
            user.add_beneficiary_role()
            yesterday = datetime.utcnow() - timedelta(days=1)
            users_factories.DepositGrantFactory(user=user, expirationDate=yesterday)

            assert user.received_pass_15_17 is False
            assert user.received_pass_18 is True

        def test_received_pass_15_17_and_18(self):
            dateOfBirth16 = datetime.utcnow() - relativedelta(years=16, days=1)
            dateOfBirth18 = datetime.utcnow() - relativedelta(years=18, days=1)
            user = users_factories.UserFactory(dateOfBirth=dateOfBirth16, validatedBirthDate=dateOfBirth16)
            user.add_beneficiary_role()
            yesterday = datetime.utcnow() - timedelta(days=1)
            users_factories.DepositGrantFactory(user=user, expirationDate=yesterday)

            assert user.received_pass_15_17 is True

            user.dateOfBirth = dateOfBirth18
            user.validatedBirthDate = dateOfBirth18

            users_factories.DepositGrantFactory(user=user, expirationDate=yesterday)
            assert user.received_pass_18 is True

        def test_not_eligible_when_19(self):
            user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=19, days=1))
            assert user.eligibility is None

        def test_eligible_when_19_with_subscription_attempt_at_18(self):
            user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=19))
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=datetime.utcnow() - relativedelta(years=1),
                user=user,
                type=fraud_models.FraudCheckType.DMS,
                status=fraud_models.FraudCheckStatus.KO,
                eligibilityType=user_models.EligibilityType.AGE18,
            )
            assert user.eligibility is user_models.EligibilityType.AGE18

        def test_eligible_when_19_with_subscription_attempt_at_18_without_account(self):
            user_19_yo_birth_date = datetime.utcnow() - relativedelta(years=19, months=3)
            dms_registration_date_by_18_yo = datetime.utcnow() - relativedelta(months=6)
            user_account_creation_date_by_19_yo = datetime.utcnow()

            user = users_factories.UserFactory(dateOfBirth=user_19_yo_birth_date)
            dms_content_before_account_creation = fraud_factories.DMSContentFactory(
                user=user,
                registration_datetime=dms_registration_date_by_18_yo,
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                dateCreated=user_account_creation_date_by_19_yo,  # the fraud_check was created when user validated its email
                user=user,
                type=fraud_models.FraudCheckType.DMS,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=user_models.EligibilityType.AGE18,
                resultContent=dms_content_before_account_creation,
            )
            assert user.eligibility is user_models.EligibilityType.AGE18

    def test_hasPhysicalVenue(self):
        user = users_factories.UserFactory()
        assert not user.hasPhysicalVenues

        offerer = offerers_factories.UserOffererFactory(user=user).offerer
        assert not user.hasPhysicalVenues

        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        assert not user.hasPhysicalVenues

        offerers_factories.VenueFactory(managingOfferer=offerer)
        assert user.hasPhysicalVenues

    def test_full_name(self):
        # hybrid property: check both Python and SQL expressions

        user = users_factories.UserFactory()
        expected_full_name = f"{user.firstName} {user.lastName}"
        assert user.full_name == expected_full_name
        assert db.session.query(user_models.User.full_name).filter_by(id=user.id).scalar() == expected_full_name

        no_name_user = users_factories.UserFactory(firstName="", lastName="")
        assert no_name_user.full_name == no_name_user.email
        assert db.session.query(user_models.User.full_name).filter_by(id=no_name_user.id).scalar() == no_name_user.email

    def test_pro_validation_status(self):
        user = users_factories.UserFactory()
        assert user.proValidationStatus is None

        offerers_factories.UserOffererFactory(user=user, validationStatus=ValidationStatus.NEW)
        assert user.proValidationStatus == ValidationStatus.NEW

        offerers_factories.UserOffererFactory(user=user, validationStatus=ValidationStatus.PENDING)
        assert user.proValidationStatus == ValidationStatus.PENDING

        offerers_factories.UserOffererFactory(user=user, validationStatus=ValidationStatus.VALIDATED)
        assert user.proValidationStatus == ValidationStatus.VALIDATED

        offerers_factories.UserOffererFactory(user=user, validationStatus=ValidationStatus.NEW)
        offerers_factories.UserOffererFactory(user=user, validationStatus=ValidationStatus.PENDING)
        assert user.proValidationStatus == ValidationStatus.VALIDATED


class HasAccessTest:
    def test_does_not_have_access_if_not_attached(self):
        offerer = offerers_factories.OffererFactory()
        user = users_factories.UserFactory()

        assert not user.has_access(offerer.id)

    def test_does_not_have_access_if_not_validated(self):
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()
        offerer = user_offerer.offerer
        user = user_offerer.user

        assert not user.has_access(offerer.id)

    def test_has_access(self):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer
        user = user_offerer.user

        assert user.has_access(offerer.id)

    def test_has_access_if_admin(self):
        offerer = offerers_factories.OffererFactory()
        admin = users_factories.AdminFactory()

        assert admin.has_access(offerer.id)


class CalculateAgeTest:
    @freeze_time("2018-06-01")
    def test_user_age(self):
        assert users_factories.UserFactory.build(dateOfBirth=None).age is None
        assert users_factories.UserFactory.build(dateOfBirth=datetime(2000, 6, 1, 5, 1)).age == 18  # happy birthday
        assert users_factories.UserFactory.build(dateOfBirth=datetime(1999, 7, 1)).age == 18
        assert users_factories.UserFactory.build(dateOfBirth=datetime(2000, 7, 1)).age == 17
        assert users_factories.UserFactory.build(dateOfBirth=datetime(1999, 5, 1)).age == 19


class UserDepositVersionTest:
    def test_return_the_deposit(self):
        user = users_factories.BeneficiaryGrant18Factory(deposit__version=1)
        assert user.deposit_version == 1

    def test_when_no_deposit(self):
        user = users_factories.UserFactory()
        repository.delete(*user.deposits)
        assert user.deposit_version is None


class UserWalletBalanceTest:
    def test_balance_is_0_with_no_deposits_and_no_bookings(self):
        user = users_factories.UserFactory()

        assert user.wallet_balance == 0

    def test_balance_ignores_expired_deposits(self):
        user = users_factories.BeneficiaryGrant18Factory(deposit__expirationDate=datetime(2000, 1, 1))

        assert user.wallet_balance == 0

    def test_balance(self):
        user = users_factories.BeneficiaryGrant18Factory()
        bookings_factories.UsedBookingFactory(user=user, quantity=1, amount=10)
        bookings_factories.UsedBookingFactory(user=user, quantity=2, amount=20)
        bookings_factories.BookingFactory(user=user, quantity=3, amount=30)
        bookings_factories.CancelledBookingFactory(user=user, quantity=4, amount=40)

        assert user.wallet_balance == 300 - (10 + 2 * 20 + 3 * 30)

    def test_real_balance_with_only_used_bookings(self):
        user = users_factories.BeneficiaryGrant18Factory()
        bookings_factories.BookingFactory(user=user, quantity=1, amount=30)

        assert user.wallet_balance == 300 - 30

    def test_balance_when_expired(self):
        user = users_factories.BeneficiaryGrant18Factory()
        bookings_factories.UsedBookingFactory(user=user, quantity=1, amount=10)
        deposit = user.deposit
        deposit.expirationDate = datetime(2000, 1, 1)

        assert user.wallet_balance == 0


class SQLFunctionsTest:
    def test_wallet_balance(self):
        with freeze_time(datetime.utcnow() - relativedelta(years=2, days=2)):
            user = users_factories.UnderageBeneficiaryFactory(subscription_age=16)
            # disable trigger because deposit.expirationDate > now() is False in database time
            db.session.execute("ALTER TABLE booking DISABLE TRIGGER booking_update;")
            bookings_factories.BookingFactory(user=user, amount=18)
            db.session.execute("ALTER TABLE booking ENABLE TRIGGER booking_update;")

        finance_api.create_deposit(user, "test", user_models.EligibilityType.AGE18)

        bookings_factories.UsedBookingFactory(user=user, amount=10)
        bookings_factories.BookingFactory(user=user, amount=1)

        assert db.session.query(sa.func.get_wallet_balance(user.id, False)).first()[0] == decimal.Decimal(289)
        assert db.session.query(sa.func.get_wallet_balance(user.id, True)).first()[0] == decimal.Decimal(290)

    def test_wallet_balance_no_deposit(self):
        user = users_factories.UserFactory()

        assert db.session.query(sa.func.get_wallet_balance(user.id, False)).first()[0] == 0

    def test_wallet_balance_multiple_deposits(self):
        user = users_factories.UserFactory()
        users_factories.DepositGrantFactory(user=user, type=finance_models.DepositType.GRANT_15_17)
        users_factories.DepositGrantFactory(user=user, type=finance_models.DepositType.GRANT_18)

        with pytest.raises(sa_exc.ProgrammingError) as exc:
            # pylint: disable=expression-not-assigned
            db.session.query(sa.func.get_wallet_balance(user.id, False)).first()[0]

        assert "more than one row returned by a subquery" in str(exc.value)

    def test_wallet_balance_expired_deposit(self):
        with freeze_time(datetime.utcnow() - relativedelta(years=2, days=2)):
            user = users_factories.UnderageBeneficiaryFactory(subscription_age=16)
            # disable trigger because deposit.expirationDate > now() is False in database time
            db.session.execute("ALTER TABLE booking DISABLE TRIGGER booking_update;")
            bookings_factories.BookingFactory(user=user, amount=18)
            db.session.execute("ALTER TABLE booking ENABLE TRIGGER booking_update;")

        assert db.session.query(sa.func.get_wallet_balance(user.id, False)).first()[0] == 0

    def test_deposit_balance(self):
        deposit = users_factories.DepositGrantFactory()

        bookings_factories.UsedBookingFactory(deposit=deposit, amount=10)
        bookings_factories.BookingFactory(deposit=deposit, amount=1)

        assert db.session.query(sa.func.get_deposit_balance(deposit.id, False)).first()[0] == 289
        assert db.session.query(sa.func.get_deposit_balance(deposit.id, True)).first()[0] == 290

    def test_deposit_balance_wrong_id(self):
        with pytest.raises(sa_exc.InternalError) as exc:
            # pylint: disable=expression-not-assigned
            db.session.query(sa.func.get_deposit_balance(None, False)).first()[0]

        assert "the deposit was not found" in str(exc)


class SuperAdminTest:
    @override_settings(SUPER_ADMIN_EMAIL_ADDRESSES=["super@admin.user"], IS_PROD=True)
    def test_super_user_prod(self):
        user = users_factories.UserFactory(email="super@admin.user")
        assert user.is_super_admin()

    @override_settings(SUPER_ADMIN_EMAIL_ADDRESSES=[], IS_PROD=True)
    def test_super_user_prod_not_configured(self):
        user = users_factories.UserFactory(email="simple-admin@admin.user")
        assert user.is_super_admin() is False

    @override_settings()
    def test_super_user_not_prod_not_admin(self):
        user = users_factories.UserFactory(email="simple-user@example.com")
        assert user.is_super_admin() is False

    @override_settings()
    def test_super_user_not_prod_is_admin_is_super_admin(self):
        user = users_factories.AdminFactory()
        assert user.is_super_admin()
