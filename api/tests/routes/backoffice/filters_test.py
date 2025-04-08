import datetime

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.routes.backoffice import filters


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class FormatRoleTest:
    @pytest.mark.parametrize(
        "role, expected",
        [
            (users_models.UserRole.ADMIN, "Admin"),
            (users_models.UserRole.ANONYMIZED, "Aucune information"),
            (users_models.UserRole.PRO, "Pro"),
            (users_models.UserRole.NON_ATTACHED_PRO, "Pro"),
            (users_models.UserRole.TEST, "Test"),
            ("invalid", "Aucune information"),
            ("", "Aucune information"),
        ],
    )
    def test_non_beneficiary_roles(self, role, expected):
        assert filters.format_role(role) == expected

    @pytest.mark.parametrize(
        "age, deposit_type, expected",
        [
            (18, finance_models.DepositType.GRANT_18, "Ancien Pass 18"),
            (15, finance_models.DepositType.GRANT_15_17, "Ancien Pass 15-17"),
            (18, finance_models.DepositType.GRANT_17_18, "Pass 18"),
            (17, finance_models.DepositType.GRANT_17_18, "Pass 17"),
        ],
    )
    def test_beneficiaries(self, age, deposit_type, expected):
        user = users_factories.BeneficiaryFactory(age=age)
        user.deposits[0].type = deposit_type
        result = filters.format_role(user.roles[0], user.deposits)
        assert result == expected

    @pytest.mark.parametrize(
        "age, deposit_type, expected",
        [
            (18, finance_models.DepositType.GRANT_18, "Ancien Pass 18 expiré"),
            (15, finance_models.DepositType.GRANT_15_17, "Ancien Pass 15-17 expiré"),
            (18, finance_models.DepositType.GRANT_17_18, "Pass 18 expiré"),
            (17, finance_models.DepositType.GRANT_17_18, "Pass 17 expiré"),
        ],
    )
    def test_ex_beneficiaries(self, age, deposit_type, expected):
        user = users_factories.BeneficiaryFactory(age=age)
        user.deposits[0].type = deposit_type
        user.deposits[0].expirationDate = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        result = filters.format_role(user.roles[0], user.deposits)
        assert result == expected

    def test_deposit_order(self):
        user = users_factories.BeneficiaryFactory(age=17)
        user.deposits[0].type = finance_models.DepositType.GRANT_17_18
        recredit = finance_factories.RecreditFactory(
            deposit__version=3,
            deposit__expirationDate=user.deposits[0].expirationDate + datetime.timedelta(days=2),
            recreditType=finance_models.RecreditType.RECREDIT_17,
        )
        user.deposits.append(recredit.deposit)
        result = filters.format_role(user.roles[0], user.deposits)
        assert result == "Pass 17"


class FormatDepositUsedTest:

    @pytest.mark.parametrize(
        "deposit_type, expected",
        [
            (
                finance_models.DepositType.GRANT_18,
                '<span class="badge text-secondary bg-secondary-subtle">Ancien Pass 18</span>',
            ),
            (
                finance_models.DepositType.GRANT_15_17,
                '<span class="badge text-secondary bg-secondary-subtle">Ancien Pass 15-17</span>',
            ),
            (finance_models.DepositType.GRANT_17_18, "Aucune information"),  # cannot exist but it should not crash
        ],
    )
    def test_legacy_bookings(self, deposit_type, expected):
        booking = bookings_factories.UsedBookingFactory()
        booking.usedRecreditType = None
        booking.deposit.type = deposit_type
        result = filters.format_deposit_used(booking)
        assert result == expected

    @pytest.mark.parametrize(
        "recredit_type, expected",
        [
            (
                bookings_models.BookingRecreditType.RECREDIT_18,
                '<span class="badge text-secondary bg-secondary-subtle">Pass 18</span>',
            ),
            (
                bookings_models.BookingRecreditType.RECREDIT_17,
                '<span class="badge text-secondary bg-secondary-subtle">Pass 17</span>',
            ),
        ],
    )
    def test_new_bookings(self, recredit_type, expected):
        booking = bookings_factories.UsedBookingFactory(usedRecreditType=recredit_type)
        result = filters.format_deposit_used(booking)
        assert result == expected
