from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest
import pytz

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.payments import api
from pcapi.core.payments import exceptions
from pcapi.core.payments import factories as payments_factories
from pcapi.core.payments.models import Deposit
from pcapi.core.payments.models import DepositType
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2021-02-05 09:00:00")
class CreateDepositTest:
    @pytest.mark.parametrize("age,expected_amount", [(15, Decimal(20)), (16, Decimal(30)), (17, Decimal(30))])
    def test_create_underage_deposit(self, age, expected_amount):
        with freeze_time(datetime.combine(datetime.utcnow(), time(0, 0)) - relativedelta(years=age, months=2)):
            beneficiary = users_factories.UserFactory(dateOfBirth=datetime.utcnow())
        with freeze_time(datetime.utcnow() - relativedelta(month=1)):
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=beneficiary,
                status=fraud_models.FraudCheckStatus.OK,
                type=fraud_models.FraudCheckType.EDUCONNECT,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                resultContent=fraud_factories.EduconnectContentFactory(registration_datetime=datetime.utcnow()),
            )

        deposit = api.create_deposit(beneficiary, "created by test", beneficiary.eligibility, age_at_registration=age)

        assert deposit.type == DepositType.GRANT_15_17
        assert deposit.version == 1
        assert deposit.amount == expected_amount
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2021 - (age + 1) + 18, 12, 5, 0, 0, 0)

    def test_create_18_years_old_deposit(self):
        beneficiary = users_factories.UserFactory(
            dateOfBirth=datetime.combine(datetime.utcnow(), time(0, 0)) - relativedelta(years=18, months=4)
        )

        deposit = api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)

        assert deposit.type == DepositType.GRANT_18
        assert deposit.version == 2
        assert deposit.amount == Decimal(300)
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2023, 2, 5, 9, 0, 0)

    @override_settings(IS_INTEGRATION=True)
    def test_deposit_on_integration(self):
        beneficiary = users_factories.UserFactory(
            dateOfBirth=datetime.combine(datetime.utcnow(), time(0, 0)) - relativedelta(years=18, months=4)
        )

        # When
        deposit = api.create_deposit(beneficiary, "integration_signup", users_models.EligibilityType.AGE18)

        # Then
        assert deposit.type == DepositType.GRANT_18
        assert deposit.version == 2
        assert deposit.amount == Decimal(300)
        assert deposit.user.id == beneficiary.id
        assert deposit.expirationDate == datetime(2023, 2, 5, 9, 0, 0)

    def test_deposit_created_when_another_type_already_exist_for_user(self):
        birth_date = datetime.combine(datetime.utcnow(), time(0, 0)) - relativedelta(years=18, months=4)
        with freeze_time(datetime.utcnow() - relativedelta(years=3)):
            beneficiary = users_factories.UnderageBeneficiaryFactory(dateOfBirth=birth_date)

        api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)

        assert beneficiary.deposit.type == DepositType.GRANT_18
        assert len(beneficiary.deposits) == 2

    def test_cannot_create_twice_a_deposit_of_same_type(self):
        # Given
        AGE18_ELIGIBLE_BIRTH_DATE = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - relativedelta(years=18, months=2)
        beneficiary = users_factories.BeneficiaryGrant18Factory(dateOfBirth=AGE18_ELIGIBLE_BIRTH_DATE)

        # When
        with pytest.raises(exceptions.DepositTypeAlreadyGrantedException) as error:
            api.create_deposit(beneficiary, "created by test", users_models.EligibilityType.AGE18)

        # Then
        assert Deposit.query.filter(Deposit.userId == beneficiary.id).count() == 1
        assert error.value.errors["user"] == ['Cet utilisateur a déjà été crédité de la subvention "GRANT_18".']


class CreateOffererReimbursementRuleTest:
    @freeze_time("2021-10-01 00:00:00")
    def test_create_rule(self):
        offerer = offerers_factories.OffererFactory()
        start = pytz.utc.localize(datetime.today() + timedelta(days=1))
        end = pytz.utc.localize(datetime.today() + timedelta(days=2))
        rule = api.create_offerer_reimbursement_rule(
            offerer.id, subcategories=["VOD"], rate=0.8, start_date=start, end_date=end
        )

        db.session.refresh(rule)
        assert rule.offerer == offerer
        assert rule.subcategories == ["VOD"]
        assert rule.rate == Decimal("0.8")
        assert rule.timespan.lower == datetime(2021, 10, 2, 0, 0)
        assert rule.timespan.upper == datetime(2021, 10, 3, 0, 0)

    def test_validation(self):
        # Validation is thoroughly verified in `test_validation.py`.
        # This is just an integration test.
        offerer = offerers_factories.OffererFactory()
        start = (datetime.today() + timedelta(days=1)).astimezone(pytz.utc)
        with pytest.raises(exceptions.UnknownSubcategoryForReimbursementRule):
            api.create_offerer_reimbursement_rule(offerer.id, subcategories=["UNKNOWN"], rate=0.8, start_date=start)


class CreateOfferReimbursementRuleTest:
    @freeze_time("2021-10-01 00:00:00")
    def test_create_rule(self):
        offer = offers_factories.OfferFactory()
        start = pytz.utc.localize(datetime.today() + timedelta(days=1))
        end = pytz.utc.localize(datetime.today() + timedelta(days=2))
        rule = api.create_offer_reimbursement_rule(offer.id, amount=12.34, start_date=start, end_date=end)

        db.session.refresh(rule)
        assert rule.offer == offer
        assert rule.amount == Decimal("12.34")
        assert rule.timespan.lower == datetime(2021, 10, 2, 0, 0)
        assert rule.timespan.upper == datetime(2021, 10, 3, 0, 0)

    def test_validation(self):
        # Validation is thoroughly verified in `test_validation.py`.
        # This is just an integration test.
        offer = offers_factories.OfferFactory()
        start = (datetime.today() + timedelta(days=1)).astimezone(pytz.utc)
        payments_factories.CustomReimbursementRuleFactory(offer=offer, timespan=(start, None))
        with pytest.raises(exceptions.ConflictingReimbursementRule):
            api.create_offer_reimbursement_rule(offer.id, amount=12.34, start_date=start)


class EditReimbursementRuleTest:
    def test_edit_rule(self):
        timespan = (pytz.utc.localize(datetime(2021, 1, 1)), None)
        rule = payments_factories.CustomReimbursementRuleFactory(timespan=timespan)
        end = pytz.utc.localize(datetime(2030, 10, 3, 0, 0))
        api.edit_reimbursement_rule(rule, end_date=end)

        db.session.refresh(rule)
        assert rule.timespan.lower == datetime(2021, 1, 1, 0, 0)  # unchanged
        assert rule.timespan.upper == datetime(2030, 10, 3, 0, 0)

    def test_cannot_change_existing_end_date(self):
        today = datetime.today()
        timespan = (today - timedelta(days=10), today)
        rule = payments_factories.CustomReimbursementRuleFactory(timespan=timespan)
        with pytest.raises(exceptions.WrongDateForReimbursementRule):
            api.edit_reimbursement_rule(rule, end_date=today + timedelta(days=5))

    def test_validation(self):
        # Validation is thoroughly verified in `test_validation.py`.
        # This is just an integration test.
        timespan = (datetime.today() - timedelta(days=10), None)
        rule = payments_factories.CustomReimbursementRuleFactory(timespan=timespan)
        end = pytz.utc.localize(datetime.today())
        with pytest.raises(exceptions.WrongDateForReimbursementRule):
            api.edit_reimbursement_rule(rule, end_date=end)
