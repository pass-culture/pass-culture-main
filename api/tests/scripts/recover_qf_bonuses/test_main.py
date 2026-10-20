import pytest

from pcapi.core.subscription.bonus.constants import QUOTIENT_FAMILIAL_THRESHOLD
from pcapi.core.subscription.bonus.schemas import BonusCreditPerson
from pcapi.core.subscription.bonus.schemas import QuotientFamilialContent
from pcapi.core.subscription.factories import QFBonusCreditFraudCheckFactory
from pcapi.core.subscription.factories import QuotientFamilialBonusCreditContentFactory
from pcapi.core.subscription.models import FraudCheckStatus
from pcapi.core.subscription.models import FraudReasonCode
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.scripts.recover_qf_bonuses.main import recover_qf_bonus_checks


@pytest.mark.usefixtures("db_session")
def test_qf_restarted():
    user = BeneficiaryFactory.create()
    fraud_check = QFBonusCreditFraudCheckFactory.create(
        user=user,
        status=FraudCheckStatus.KO,
        reasonCodes=[FraudReasonCode.NOT_IN_TAX_HOUSEHOLD],
        resultContent=QuotientFamilialBonusCreditContentFactory.create(
            children=[
                BonusCreditPerson(
                    last_name=user.lastName,
                    first_names=[user.firstName],
                    gender=user.gender,
                    birth_date=user.birth_date,
                )
            ]
        ).model_dump(mode="json"),
    )

    recover_qf_bonus_checks(from_fraud_check_id=0, apply=True)

    assert fraud_check.status == FraudCheckStatus.STARTED
    assert fraud_check.reasonCodes is None


@pytest.mark.usefixtures("db_session")
def test_qf_granted():
    user = BeneficiaryFactory.create()
    QFBonusCreditFraudCheckFactory.create(
        user=user,
        status=FraudCheckStatus.KO,
        reasonCodes=[FraudReasonCode.NOT_IN_TAX_HOUSEHOLD],
        resultContent=QuotientFamilialBonusCreditContentFactory.create(
            children=[
                BonusCreditPerson(
                    last_name=user.lastName,
                    first_names=[user.firstName],
                    gender=user.gender,
                    birth_date=user.birth_date,
                )
            ],
            quotient_familial=QuotientFamilialContent(
                provider="test",
                value=QUOTIENT_FAMILIAL_THRESHOLD,
                year=2026,
                month=1,
                computation_year=2026,
                computation_month=1,
            ),
        ).model_dump(mode="json"),
    )

    recover_qf_bonus_checks(from_fraud_check_id=0, apply=True)

    assert user.received_bonus_credit


@pytest.mark.usefixtures("db_session")
def test_qf_ignored_because_name_does_not_match():
    user = BeneficiaryFactory.create()
    fraud_check = QFBonusCreditFraudCheckFactory.create(
        user=user,
        status=FraudCheckStatus.KO,
        reasonCodes=[FraudReasonCode.NOT_IN_TAX_HOUSEHOLD],
        resultContent=QuotientFamilialBonusCreditContentFactory.create(
            children=[
                BonusCreditPerson(
                    last_name="abc",
                    first_names=["def"],
                    gender=user.gender,
                    birth_date=user.birth_date,
                )
            ]
        ).model_dump(mode="json"),
    )

    recover_qf_bonus_checks(from_fraud_check_id=0, apply=True)

    assert fraud_check.status == FraudCheckStatus.KO
    assert fraud_check.reasonCodes == [FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]


@pytest.mark.usefixtures("db_session")
def test_qf_ignored_because_of_reason_code():
    user = BeneficiaryFactory.create()
    fraud_check = QFBonusCreditFraudCheckFactory.create(
        user=user,
        status=FraudCheckStatus.KO,
        reasonCodes=[FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH],
        resultContent=QuotientFamilialBonusCreditContentFactory.create(
            children=[
                BonusCreditPerson(
                    last_name=user.lastName,
                    first_names=[user.firstName],
                    gender=user.gender,
                    birth_date=user.birth_date,
                )
            ]
        ).model_dump(mode="json"),
    )

    recover_qf_bonus_checks(from_fraud_check_id=0, apply=True)

    assert fraud_check.status == FraudCheckStatus.KO
    assert fraud_check.reasonCodes == [FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH]
