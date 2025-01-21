from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.repository import transaction


def correct_declined_status_fraud_checks() -> None:
    with transaction():
        fraud_checks = _get_wrong_status_fraud_checks()
        for fraud_check in fraud_checks:
            fraud_check.status = FraudCheckStatus.KO


def _get_wrong_status_fraud_checks() -> list[BeneficiaryFraudCheck]:
    fraud_checks = BeneficiaryFraudCheck.query.filter(
        BeneficiaryFraudCheck.id > 24570000,  # created the day before the wrong status checks
        BeneficiaryFraudCheck.resultContent["status"].astext == "declined",
        BeneficiaryFraudCheck.status == FraudCheckStatus.SUSPICIOUS,
    ).all()
    return fraud_checks  # no pagination because < 1000 rows are returned


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    correct_declined_status_fraud_checks()
