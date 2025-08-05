import pytest
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from pcapi.core.fraud.factories import BeneficiaryFraudCheckFactory
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.users.factories import ProfileCompletedUserFactory
from pcapi.models import db
from pcapi.scripts.ubble_birth_place.main import import_ubble_v2_birth_place
from pcapi.settings import UBBLE_API_URL

from tests.connectors.beneficiaries.ubble_fixtures import build_ubble_identification_v2_response


pytestmark = pytest.mark.usefixtures("db_session")


def test_ubble_birth_place_import(requests_mock):
    user = ProfileCompletedUserFactory()
    fraud_check = BeneficiaryFraudCheckFactory(
        user=user, status=FraudCheckStatus.OK, type=FraudCheckType.UBBLE, thirdPartyId="idv_qwerty1234"
    )
    requests_mock.get(
        f"{UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
        json=build_ubble_identification_v2_response(),
    )

    import_ubble_v2_birth_place(not_dry=True)

    birth_place = fraud_check.source_data().get_birth_place()
    assert birth_place is not None
    assert user.birthPlace == birth_place


def test_ubble_birth_place_import_pagination(requests_mock):
    for i in range(10):
        user = ProfileCompletedUserFactory()
        fraud_check = BeneficiaryFraudCheckFactory(
            user=user, status=FraudCheckStatus.OK, type=FraudCheckType.UBBLE, thirdPartyId=f"idv_qwerty1234{i}"
        )
        requests_mock.get(
            f"{UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(),
        )

    import_ubble_v2_birth_place(not_dry=True, batch_size=2)

    ubble_fraud_check_query = (
        select(BeneficiaryFraudCheck)
        .where(BeneficiaryFraudCheck.type == FraudCheckType.UBBLE)
        .options(joinedload(BeneficiaryFraudCheck.user))
    )
    for fraud_check in db.session.scalars(ubble_fraud_check_query).all():
        birth_place = fraud_check.source_data().get_birth_place()
        assert birth_place is not None
        assert fraud_check.user.birthPlace == birth_place
