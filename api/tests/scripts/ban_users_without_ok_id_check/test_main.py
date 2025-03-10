from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest
import time_machine

from pcapi.core.finance.models import DepositType
from pcapi.core.fraud.factories import BeneficiaryFraudCheckFactory
from pcapi.core.fraud.factories import BeneficiaryFraudReviewFactory
from pcapi.core.fraud.factories import HonorStatementFraudCheckFactory
from pcapi.core.fraud.factories import ProfileCompletionFraudCheckFactory
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.fraud.models import FraudReviewStatus
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.core.users.factories import DepositGrantFactory
from pcapi.core.users.models import EligibilityType
from pcapi.scripts.ban_users_without_ok_id_check.main import ban_beneficiaries_without_ok_id_check


@pytest.mark.usefixtures("db_session")
class BanUsersTest:
    def test_ban_users_with_ko_id_check(self):
        yesterday = datetime.utcnow() - relativedelta(days=1)
        last_year = datetime.utcnow() - relativedelta(years=1)
        with time_machine.travel(last_year):
            user = BeneficiaryFactory(
                age=17, beneficiaryFraudChecks__type=FraudCheckType.EDUCONNECT, deposit__expirationDate=yesterday
            )
        BeneficiaryFraudCheckFactory(
            user=user, type=FraudCheckType.DMS, status=FraudCheckStatus.KO, eligibilityType=EligibilityType.AGE18
        )
        DepositGrantFactory(user=user, type=DepositType.GRANT_18)

        ban_beneficiaries_without_ok_id_check(is_not_dry_run=True)

        assert not user.isActive

    def test_ban_users_with_missing_id_check(self):
        yesterday = datetime.utcnow() - relativedelta(days=1)
        last_year = datetime.utcnow() - relativedelta(years=1)
        with time_machine.travel(last_year):
            user = BeneficiaryFactory(
                age=17, beneficiaryFraudChecks__type=FraudCheckType.EDUCONNECT, deposit__expirationDate=yesterday
            )
        DepositGrantFactory(user=user, type=DepositType.GRANT_18)

        ban_beneficiaries_without_ok_id_check(is_not_dry_run=True)

        assert not user.isActive

    def test_do_not_ban_users_with_ok_id_check(self):
        user = BeneficiaryFactory(age=17)

        ban_beneficiaries_without_ok_id_check(is_not_dry_run=True)

        assert user.isActive

    def test_do_not_ban_users_with_ok_and_ko_id_check(self):
        tomorrow = datetime.utcnow() + relativedelta(days=1)
        yesterday = datetime.utcnow() - relativedelta(days=1)
        last_year = datetime.utcnow() - relativedelta(years=1)
        with time_machine.travel(last_year):
            user = BeneficiaryFactory(
                age=17, beneficiaryFraudChecks__type=FraudCheckType.EDUCONNECT, deposit__expirationDate=yesterday
            )
        BeneficiaryFraudCheckFactory(
            user=user, type=FraudCheckType.DMS, status=FraudCheckStatus.OK, eligibilityType=EligibilityType.AGE18
        )
        BeneficiaryFraudCheckFactory(
            user=user,
            type=FraudCheckType.DMS,
            status=FraudCheckStatus.KO,
            eligibilityType=EligibilityType.AGE18,
            dateCreated=tomorrow,
        )
        DepositGrantFactory(user=user, type=DepositType.GRANT_18)

        ban_beneficiaries_without_ok_id_check(is_not_dry_run=True)

        assert user.isActive

    def test_do_not_ban_users_with_ok_and_ko_manual_review(self):
        tomorrow = datetime.utcnow() + relativedelta(days=1)
        yesterday = datetime.utcnow() - relativedelta(days=1)
        last_year = datetime.utcnow() - relativedelta(years=1)
        with time_machine.travel(last_year):
            user = BeneficiaryFactory(
                age=17, beneficiaryFraudChecks__type=FraudCheckType.EDUCONNECT, deposit__expirationDate=yesterday
            )
        DepositGrantFactory(user=user, type=DepositType.GRANT_18)
        BeneficiaryFraudReviewFactory(user=user, review=FraudReviewStatus.OK, eligibilityType=EligibilityType.AGE18)
        BeneficiaryFraudReviewFactory(
            user=user, review=FraudReviewStatus.KO, eligibilityType=EligibilityType.AGE18, dateReviewed=tomorrow
        )

        ban_beneficiaries_without_ok_id_check(is_not_dry_run=True)

        assert user.isActive
