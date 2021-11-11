from datetime import date
from datetime import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

from pcapi.core.payments.models import DepositType
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as user_models
from pcapi.core.users.exceptions import InvalidUserRoleException


@pytest.mark.usefixtures("db_session")
class UserTest:
    class DepositTest:
        def test_return_none_if_no_deposits_exists(self):
            user = users_factories.UserFactory()

            assert user.deposit == None

        def test_return_expired_deposit_if_only_expired_deposits_exists(self):
            user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18))
            user.add_beneficiary_role()
            yesterday = datetime.now() - timedelta(days=1)
            users_factories.DepositGrantFactory(user=user, expirationDate=yesterday)

            assert user.deposit.type == DepositType.GRANT_18

        def test_return_last_expired_deposit_if_only_expired_deposits_exists(self):
            with freeze_time(datetime.utcnow() - relativedelta(years=3)):
                user = users_factories.UnderageBeneficiaryFactory()

            users_factories.DepositGrantFactory(user=user)

            assert user.deposit.type == DepositType.GRANT_18

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

        def test_has_admin_role_with_legacy_property(self):
            user = users_factories.UserFactory(isAdmin=True, roles=[])

            assert user.has_admin_role
            assert user_models.User.query.filter(user_models.User.has_admin_role.is_(False)).all() == []
            assert user_models.User.query.filter(user_models.User.has_admin_role.is_(True)).all() == [user]

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

        def test_add_role_on_new_user(self):
            user = user_models.User()

            user.add_pro_role()

            assert user.has_pro_role

        def test_add_admin_role(self):
            user = users_factories.UserFactory.build()

            user.add_admin_role()

            assert user.has_admin_role
            assert user.isAdmin

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

        def test_cannot_add_beneficiary_role_to_an_admin_with_legacy_property(self):
            user = users_factories.UserFactory.build(isAdmin=True, roles=[])

            with pytest.raises(InvalidUserRoleException):
                user.add_beneficiary_role()

                assert not user.has_beneficiary_role
                assert user.has_admin_role
                assert user.isAdmin

        def test_cannot_add_admin_role_to_a_beneficiary_with_legacy_property(self):
            user = users_factories.UserFactory.build(roles=[user_models.UserRole.BENEFICIARY])

            with pytest.raises(InvalidUserRoleException):
                user.add_admin_role()

                assert user.has_beneficiary_role
                assert not user.has_admin_role
                assert not user.isAdmin

        def test_remove_admin_role(self):
            user = users_factories.AdminFactory.build()

            user.remove_admin_role()

            assert not user.has_admin_role
            assert not user.isAdmin

        def test_remove_admin_role_when_user_is_not_admin(self):
            user = users_factories.BeneficiaryGrant18Factory.build()

            user.remove_admin_role()

            assert user.has_beneficiary_role
            assert not user.has_admin_role
            assert not user.isAdmin

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

    class UserTest:
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
        def test_with_leap_year(self, birth_date, today, latest_birthday):
            with freeze_time(today):
                assert user_models._get_latest_birthday(birth_date) == latest_birthday


@pytest.mark.usefixtures("db_session")
class SuperAdminTest:
    @override_settings(SUPER_ADMIN_EMAIL_ADDRESSES="super@admin.user", IS_PROD=True)
    def test_super_user_prod(self):
        user = users_factories.UserFactory(email="super@admin.user")
        assert user.is_super_admin()

    @override_settings(SUPER_ADMIN_EMAIL_ADDRESSES="", IS_PROD=True)
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
