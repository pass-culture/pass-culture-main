from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.repository import transaction


def delete_problematic_fraud_check() -> None:
    with transaction():
        BeneficiaryFraudCheck.query.filter(BeneficiaryFraudCheck.id == 24685364).delete()


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    delete_problematic_fraud_check()
