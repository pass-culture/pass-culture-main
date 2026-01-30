import decimal
from datetime import date
from datetime import datetime
from datetime import timedelta

import pytest
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import time_machine
from dateutil.relativedelta import relativedelta

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
from pcapi.connectors.dms import models as dms_models
from pcapi.core.finance import deposit_api
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as user_models
from pcapi.core.users import repository as users_repository
from pcapi.core.users.exceptions import InvalidUserRoleException
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import date as date_utils
from pcapi.utils.repository import transaction


@pytest.mark.usefixtures("db_session")
class UserTest:
    class DepositTest:
        def test_return_none_if_no_deposits_exists(self):
            user = users_factories.UserFactory()

            assert user.deposit is None

        def test_return_expired_deposit_if_only_expired_deposits_exists(self):
            user = users_factories.UserFactory(dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18))
            user.add_beneficiary_role()
            yesterday = date_utils.get_naive_utc_now() - timedelta(days=1)
            users_factories.DepositGrantFactory(user=user, expirationDate=yesterday)

            assert user.deposit.type == finance_models.DepositType.GRANT_17_18

        def test_return_last_expired_deposit_if_only_expired_deposits_exists(self):
            with time_machine.travel(date_utils.get_naive_utc_now() - relativedelta(years=3)):
                user = users_factories.UnderageBeneficiaryFactory(
                    deposit__expirationDate=date_utils.get_naive_utc_now() + relativedelta(years=2)
                )

            users_factories.DepositGrantFactory(user=user)

            assert user.deposit.type == finance_models.DepositType.GRANT_17_18

    class UserRoleTest:
        def test_has_admin_role(self):
            user = users_factories.AdminFactory()

            assert user.has_admin_role
            assert db.session.query(user_models.User).filter(user_models.User.has_admin_role.is_(False)).all() == []
            assert db.session.query(user_models.User).filter(user_models.User.has_admin_role.is_(True)).all() == [user]

        def test_has_beneficiary_role(self):
            user = users_factories.BeneficiaryGrant18Factory()

            assert user.has_beneficiary_role
            assert (
                db.session.query(user_models.User).filter(user_models.User.has_beneficiary_role.is_(False)).all() == []
            )
            assert db.session.query(user_models.User).filter(user_models.User.has_beneficiary_role.is_(True)).all() == [
                user
            ]

        def test_has_beneficiary_role_with_legacy_property(self):
            user = users_factories.UserFactory(roles=[user_models.UserRole.BENEFICIARY])

            assert user.has_beneficiary_role
            assert (
                db.session.query(user_models.User).filter(user_models.User.has_beneficiary_role.is_(False)).all() == []
            )
            assert db.session.query(user_models.User).filter(user_models.User.has_beneficiary_role.is_(True)).all() == [
                user
            ]

        def test_has_pro_role(self):
            user = users_factories.ProFactory()

            assert user.has_pro_role
            assert db.session.query(user_models.User).filter(user_models.User.has_pro_role.is_(False)).all() == []
            assert db.session.query(user_models.User).filter(user_models.User.has_pro_role.is_(True)).all() == [user]

        def test_has_test_role(self):
            user = users_factories.UserFactory(roles=[user_models.UserRole.TEST])

            assert user.has_test_role
            assert db.session.query(user_models.User).filter(user_models.User.has_test_role.is_(False)).all() == []
            assert db.session.query(user_models.User).filter(user_models.User.has_test_role.is_(True)).all() == [user]

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
            with time_machine.travel(today):
                assert user_models._get_latest_birthday(birth_date) == latest_birthday

    class EligibilityTest:
        def test_eligible_when_19_with_subscription_attempt_at_18_without_account(self):
            user_19_yo_birth_date = date_utils.get_naive_utc_now() - relativedelta(years=19, months=3)
            dms_registration_date_by_18_yo = date_utils.get_naive_utc_now() - relativedelta(months=6)
            user_account_creation_date_by_19_yo = date_utils.get_naive_utc_now()

            user = users_factories.UserFactory(dateOfBirth=user_19_yo_birth_date)
            dms_content_before_account_creation = subscription_factories.DMSContentFactory(
                user=user,
                registration_datetime=dms_registration_date_by_18_yo,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                dateCreated=user_account_creation_date_by_19_yo,  # the fraud_check was created when user validated its email
                user=user,
                type=subscription_models.FraudCheckType.DMS,
                status=subscription_models.FraudCheckStatus.OK,
                eligibilityType=user_models.EligibilityType.AGE17_18,
                resultContent=dms_content_before_account_creation,
            )
            assert user.eligibility is user_models.EligibilityType.AGE17_18

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

        offerers_factories.NewUserOffererFactory(user=user)
        assert user.proValidationStatus == ValidationStatus.NEW

        offerers_factories.PendingUserOffererFactory(user=user)
        assert user.proValidationStatus == ValidationStatus.PENDING

        offerers_factories.UserOffererFactory(user=user)
        assert user.proValidationStatus == ValidationStatus.VALIDATED

        offerers_factories.NewUserOffererFactory(user=user)
        offerers_factories.PendingUserOffererFactory(user=user)
        assert user.proValidationStatus == ValidationStatus.VALIDATED


@pytest.mark.usefixtures("db_session")
class HasAccessTest:
    def test_does_not_have_access_if_not_attached(self):
        offerer = offerers_factories.OffererFactory()
        user = users_factories.UserFactory()

        assert not users_repository.has_access(user, offerer.id)

    def test_does_not_have_access_if_not_validated(self):
        user_offerer = offerers_factories.NewUserOffererFactory()
        offerer = user_offerer.offerer
        user = user_offerer.user

        assert not users_repository.has_access(user, offerer.id)

    def test_has_access(self):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer
        user = user_offerer.user

        assert users_repository.has_access(user, offerer.id)

    def test_has_access_if_admin(self):
        offerer = offerers_factories.OffererFactory()
        admin = users_factories.AdminFactory()

        assert users_repository.has_access(admin, offerer.id)


@pytest.mark.usefixtures("db_session")
class CalculateAgeTest:
    @time_machine.travel("2018-06-01")
    def test_user_age(self):
        assert users_factories.UserFactory.build(dateOfBirth=None).age is None
        assert users_factories.UserFactory.build(dateOfBirth=datetime(2000, 6, 1, 5, 1)).age == 18  # happy birthday
        assert users_factories.UserFactory.build(dateOfBirth=datetime(1999, 7, 1)).age == 18
        assert users_factories.UserFactory.build(dateOfBirth=datetime(2000, 7, 1)).age == 17
        assert users_factories.UserFactory.build(dateOfBirth=datetime(1999, 5, 1)).age == 19


@pytest.mark.usefixtures("db_session")
class UserDepositVersionTest:
    def test_return_the_deposit(self):
        user = users_factories.BeneficiaryGrant18Factory(deposit__version=1)
        assert user.deposit_version == 1

    def test_when_no_deposit(self):
        user = users_factories.UserFactory()
        for deposit in user.deposits:
            db.session.delete(deposit)
        db.session.commit()
        assert user.deposit_version is None


@pytest.mark.usefixtures("db_session")
class UserWalletBalanceTest:
    def test_balance_is_0_with_no_deposits_and_no_bookings(self):
        user = users_factories.UserFactory()

        assert user.wallet_balance == 0

    def test_balance_ignores_expired_deposits(self):
        user = users_factories.BeneficiaryGrant18Factory(deposit__expirationDate=datetime(2000, 1, 1))

        assert user.wallet_balance == 0

    def test_balance(self):
        user = users_factories.BeneficiaryFactory(deposit__amount=300)
        bookings_factories.UsedBookingFactory(user=user, quantity=1, amount=10)
        bookings_factories.UsedBookingFactory(user=user, quantity=2, amount=20)
        bookings_factories.BookingFactory(user=user, quantity=3, amount=30)
        bookings_factories.CancelledBookingFactory(user=user, quantity=4, amount=40)

        assert user.wallet_balance == 300 - (10 + 2 * 20 + 3 * 30)

    def test_real_balance_with_only_used_bookings(self):
        user = users_factories.BeneficiaryFactory(deposit__amount=300)
        bookings_factories.BookingFactory(user=user, quantity=1, amount=30)

        assert user.wallet_balance == 300 - 30

    def test_balance_when_expired(self):
        user = users_factories.BeneficiaryGrant18Factory()
        bookings_factories.UsedBookingFactory(user=user, quantity=1, amount=10)
        deposit = user.deposit
        deposit.expirationDate = datetime(2000, 1, 1)

        assert user.wallet_balance == 0


@pytest.mark.usefixtures("db_session")
class SQLFunctionsTest:
    def test_wallet_balance(self):
        with time_machine.travel(date_utils.get_naive_utc_now() - relativedelta(years=2, days=2)):
            user = users_factories.UnderageBeneficiaryFactory(
                subscription_age=16, deposit__expirationDate=date_utils.get_naive_utc_now() + relativedelta(months=2)
            )
            # disable trigger because deposit.expirationDate > now() is False in database time
            db.session.execute(sa.text("ALTER TABLE booking DISABLE TRIGGER booking_update;"))
            bookings_factories.BookingFactory(user=user, amount=18)
            db.session.execute(sa.text("ALTER TABLE booking ENABLE TRIGGER booking_update;"))

        deposit_api.upsert_deposit(user, "test", user_models.EligibilityType.AGE18)

        bookings_factories.UsedBookingFactory(user=user, amount=10)
        bookings_factories.BookingFactory(user=user, amount=1)

        assert db.session.query(sa.func.get_wallet_balance(user.id, False)).first()[0] == decimal.Decimal(289)
        assert db.session.query(sa.func.get_wallet_balance(user.id, True)).first()[0] == decimal.Decimal(290)

    def test_wallet_balance_no_deposit(self):
        user = users_factories.UserFactory()

        assert db.session.query(sa.func.get_wallet_balance(user.id, False)).first()[0] == 0

    def test_wallet_balance_multiple_deposits(self):
        user = users_factories.UserFactory(age=18)
        expiration_date = date_utils.get_naive_utc_now() + relativedelta(years=3)
        users_factories.DepositGrantFactory(
            user=user,
            type=finance_models.DepositType.GRANT_15_17,
            expirationDate=expiration_date,
            amount=decimal.Decimal("3"),
        )
        newest_deposit = users_factories.DepositGrantFactory(
            user=user,
            type=finance_models.DepositType.GRANT_18,
            expirationDate=expiration_date + relativedelta(weeks=1),
            amount=decimal.Decimal("123"),
        )

        (wallet_balance,) = db.session.query(sa.func.get_wallet_balance(user.id, False)).first()

        assert wallet_balance == newest_deposit.amount

    def test_wallet_balance_expired_deposit(self):
        with time_machine.travel(date_utils.get_naive_utc_now() - relativedelta(years=2, days=2)):
            user = users_factories.UnderageBeneficiaryFactory(
                subscription_age=16, deposit__expirationDate=date_utils.get_naive_utc_now() + relativedelta(months=2)
            )
            # disable trigger because deposit.expirationDate > now() is False in database time
            db.session.execute(sa.text("ALTER TABLE booking DISABLE TRIGGER booking_update;"))
            bookings_factories.BookingFactory(user=user, amount=18)
            db.session.execute(sa.text("ALTER TABLE booking ENABLE TRIGGER booking_update;"))

        assert db.session.query(sa.func.get_wallet_balance(user.id, False)).first()[0] == 0

    @pytest.mark.parametrize(
        "initial_amount", (decimal.Decimal("150"), decimal.Decimal("152.45"), decimal.Decimal("152.55"))
    )
    def test_deposit_balance(self, initial_amount):
        user = users_factories.BeneficiaryFactory(age=18, deposit__amount=initial_amount)
        deposit = user.deposit

        bookings_factories.UsedBookingFactory(deposit=deposit, amount=10)
        bookings_factories.BookingFactory(deposit=deposit, amount=1)

        assert db.session.query(sa.func.get_deposit_balance(deposit.id, False)).first()[0] == initial_amount - 11
        assert db.session.query(sa.func.get_deposit_balance(deposit.id, True)).first()[0] == initial_amount - 10

    def test_deposit_balance_on_cancelled_bookings(self):
        user = users_factories.BeneficiaryFactory(age=18)
        deposit = user.deposit
        initial_amount = deposit.amount

        bookings_factories.CancelledBookingFactory(deposit=deposit, amount=10)
        bookings_factories.CancelledBookingFactory(deposit=deposit, amount=20)

        assert db.session.query(sa.func.get_deposit_balance(deposit.id, False)).first()[0] == initial_amount
        assert db.session.query(sa.func.get_deposit_balance(deposit.id, True)).first()[0] == initial_amount

    def test_deposit_balance_on_only_used_bookings(self):
        user = users_factories.BeneficiaryFactory(age=18)
        deposit = user.deposit
        initial_amount = deposit.amount

        bookings_factories.BookingFactory(deposit=deposit, amount=10)
        bookings_factories.BookingFactory(deposit=deposit, amount=20)

        assert db.session.query(sa.func.get_deposit_balance(deposit.id, True)).first()[0] == initial_amount
        assert db.session.query(sa.func.get_deposit_balance(deposit.id, False)).first()[0] == initial_amount - 10 - 20

    def test_deposit_balance_wrong_id(self):
        with pytest.raises(sa_exc.InternalError) as exc:
            db.session.query(sa.func.get_deposit_balance(None, False)).first()[0]

        assert "the deposit was not found" in str(exc)

    def test_deposit_bookings_with_incident(self):
        deposit = users_factories.BeneficiaryFactory(age=18).deposit

        bookings_factories.BookingFactory(deposit=deposit, amount=20)
        bookings_factories.UsedBookingFactory(deposit=deposit, amount=45)

        booking_reimbursed = bookings_factories.ReimbursedBookingFactory(deposit=deposit, amount=35)
        booking_reimbursed_2 = bookings_factories.ReimbursedBookingFactory(deposit=deposit, amount=40)

        incident = finance_factories.FinanceIncidentFactory()

        finance_factories.IndividualBookingFinanceIncidentFactory(booking=booking_reimbursed, incident=incident)

        # partial booking finance incident
        finance_factories.IndividualBookingFinanceIncidentFactory(
            booking=booking_reimbursed_2, incident=incident, newTotalAmount=3000
        )  # +10 on user's wallet

        author = users_factories.UserFactory()
        finance_api.validate_finance_overpayment_incident(incident, force_debit_note=False, author=author)

        assert incident.status == finance_models.IncidentStatus.VALIDATED

        # All bookings that are not cancelled
        assert (
            db.session.query(sa.func.get_deposit_balance(deposit.id, False)).first()[0]
            == 150 - 20 - 45 - 35 - 40 + 35 + 10
        )
        assert (
            db.session.query(sa.func.get_deposit_balance(deposit.id, True)).first()[0] == 150 - 45 - 35 - 40 + 35 + 10
        )

        assert booking_reimbursed.status == bookings_models.BookingStatus.CANCELLED
        assert booking_reimbursed_2.status == bookings_models.BookingStatus.REIMBURSED

    def test_deposit_bookings_without_associated_incident(self):
        # Given
        deposit = users_factories.BeneficiaryFactory(age=18).deposit
        incident = finance_factories.FinanceIncidentFactory()

        bookings_factories.BookingFactory(deposit=deposit, amount=20)
        bookings_factories.ReimbursedBookingFactory(deposit=deposit, amount=40)
        bookings_factories.ReimbursedBookingFactory(deposit=deposit, amount=30)

        # When
        author = users_factories.UserFactory()
        finance_api.validate_finance_overpayment_incident(incident, force_debit_note=False, author=author)

        # Then
        assert incident.status == finance_models.IncidentStatus.VALIDATED
        assert db.session.query(sa.func.get_deposit_balance(deposit.id, False)).first()[0] == 150 - 20 - 40 - 30
        assert db.session.query(sa.func.get_deposit_balance(deposit.id, True)).first()[0] == 150 - 40 - 30

    def test_deposit_bookings_when_incident_is_cancelled(self):
        deposit = users_factories.BeneficiaryFactory(age=18).deposit
        incident = finance_factories.FinanceIncidentFactory()

        bookings_factories.BookingFactory(deposit=deposit, amount=20)
        booking_reimbursed = bookings_factories.ReimbursedBookingFactory(deposit=deposit, amount=35)
        booking_reimbursed_2 = bookings_factories.ReimbursedBookingFactory(deposit=deposit, amount=40)

        finance_factories.IndividualBookingFinanceIncidentFactory(booking=booking_reimbursed, incident=incident)
        finance_factories.IndividualBookingFinanceIncidentFactory(
            booking=booking_reimbursed_2, incident=incident, newTotalAmount=3000
        )  # +10 on user's wallet

        author = users_factories.UserFactory()
        finance_api.cancel_finance_incident(
            incident=incident, comment="Cancellation for the purpose of this test", author=author
        )

        assert incident.status == finance_models.IncidentStatus.CANCELLED

        assert (
            db.session.query(sa.func.get_deposit_balance(deposit.id, False)).first()[0] == 150 - 20 - 35 - 40 + 35 + 10
        )
        assert db.session.query(sa.func.get_deposit_balance(deposit.id, True)).first()[0] == 150 - 35 - 40 + 35 + 10


class UserLoginTest:
    # Since we are testing a deferred trigger on the User table,
    # we cannot have the db_session fixture tampering with the
    # transaction lifecycle.
    @pytest.mark.usefixtures("clean_database")
    def test_empty_password_update(self):
        with pytest.raises(sa_exc.InternalError) as exc:
            with transaction():
                user = users_factories.UserFactory()
                user.password = None
                db.session.add(user)

        assert "missingLoginMethod" in str(exc.value)
        assert user.password is not None

    @pytest.mark.usefixtures("clean_database")
    def test_empty_password_insert(self):
        with pytest.raises(sa_exc.InternalError) as exc:
            with transaction():
                new_user = user_models.User(email="test@example.com")
                db.session.add(new_user)

        assert "missingLoginMethod" in str(exc.value)
        assert db.session.query(user_models.User).count() == 0

    @pytest.mark.usefixtures("clean_database")
    def test_empty_password_update_with_sso(self):
        user = users_factories.UserFactory()
        users_factories.SingleSignOnFactory(user=user)

        with transaction():
            user.password = None
            db.session.add(user)

        assert user.password is None

    @pytest.mark.usefixtures("clean_database")
    def test_empty_password_insert_with_sso(self):
        new_user = user_models.User(email="test@example.com")
        single_sign_on = user_models.SingleSignOn(user=new_user, ssoProvider="google", ssoUserId="user_id")

        with transaction():
            new_user.password = None
            db.session.add(new_user)
            db.session.add(single_sign_on)

        saved_user = db.session.query(user_models.User).one()
        assert saved_user.password is None


@pytest.mark.usefixtures("db_session")
class UserIsCaledonianTest:
    def test_user_is_caledonian(self):
        offerer = users_factories.UserFactory(postalCode="98800")
        assert offerer.is_caledonian

    def test_user_is_not_caledonian(self):
        offerer = users_factories.UserFactory()
        assert not offerer.is_caledonian


@pytest.mark.usefixtures("db_session")
class UserAccountUpdateRequestTest:
    @pytest.mark.parametrize(
        "status,expected_result",
        [
            (dms_models.GraphQLApplicationStates.draft, True),
            (dms_models.GraphQLApplicationStates.on_going, True),
            (dms_models.GraphQLApplicationStates.accepted, False),
            (dms_models.GraphQLApplicationStates.refused, False),
            (dms_models.GraphQLApplicationStates.without_continuation, False),
        ],
    )
    def test_can_be_accepted_depending_on_status(self, status, expected_result):
        update_request = users_factories.LastNameUpdateRequestFactory(status=status)
        assert update_request.can_be_accepted is expected_result

    def test_can_be_accepted_when_user_is_empty(self):
        update_request = users_factories.PhoneNumberUpdateRequestFactory(user=None)
        assert update_request.can_be_accepted is False

    @pytest.mark.parametrize(
        "update_types,expected_result",
        [
            ([user_models.UserAccountUpdateType.FIRST_NAME], True),
            ([user_models.UserAccountUpdateType.LAST_NAME], True),
            ([user_models.UserAccountUpdateType.EMAIL], True),
            ([user_models.UserAccountUpdateType.PHONE_NUMBER], True),
            ([user_models.UserAccountUpdateType.LOST_CREDENTIALS], True),
            ([user_models.UserAccountUpdateType.ACCOUNT_HAS_SAME_INFO], False),
            ([], False),
        ],
    )
    def test_can_be_accepted_depending_on_update_types(self, update_types, expected_result):
        update_request = users_factories.UserAccountUpdateRequestFactory(updateTypes=update_types)
        assert update_request.can_be_accepted is expected_result

    @pytest.mark.parametrize(
        "flags,expected_result",
        [
            ([user_models.UserAccountUpdateFlag.MISSING_VALUE], False),
            ([user_models.UserAccountUpdateFlag.INVALID_VALUE], False),
            ([user_models.UserAccountUpdateFlag.WAITING_FOR_CORRECTION], True),
            ([user_models.UserAccountUpdateFlag.CORRECTION_RESOLVED], True),
            ([user_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL], True),
            ([], True),
        ],
    )
    def test_can_be_accepted_depending_on_flags(self, flags, expected_result):
        update_request = users_factories.EmailUpdateRequestFactory(flags=flags)
        assert update_request.can_be_accepted is expected_result

    @pytest.mark.parametrize(
        "flags,expected_result",
        [
            ([], set()),
            ([user_models.UserAccountUpdateFlag.CORRECTION_RESOLVED], set()),
            (
                [user_models.UserAccountUpdateFlag.USER_SET_MANUALLY],
                {user_models.UserAccountUpdateFlag.USER_SET_MANUALLY},
            ),
            (
                [
                    user_models.UserAccountUpdateFlag.CORRECTION_RESOLVED,
                    user_models.UserAccountUpdateFlag.USER_SET_MANUALLY,
                ],
                {user_models.UserAccountUpdateFlag.USER_SET_MANUALLY},
            ),
        ],
    )
    def test_persistent_flags(self, flags, expected_result):
        update_request = users_factories.LostCredentialsUpdateRequestFactory(flags=flags)
        assert update_request.persistent_flags == expected_result

    @pytest.mark.parametrize(
        "flags,expected_result",
        [
            ([], False),
            ([user_models.UserAccountUpdateFlag.CORRECTION_RESOLVED], False),
            ([user_models.UserAccountUpdateFlag.USER_SET_MANUALLY], True),
            (
                [
                    user_models.UserAccountUpdateFlag.CORRECTION_RESOLVED,
                    user_models.UserAccountUpdateFlag.USER_SET_MANUALLY,
                ],
                True,
            ),
        ],
    )
    def test_is_user_set_manually(self, flags, expected_result):
        update_request = users_factories.LostCredentialsUpdateRequestFactory(flags=flags)
        assert update_request.is_user_set_manually is expected_result
