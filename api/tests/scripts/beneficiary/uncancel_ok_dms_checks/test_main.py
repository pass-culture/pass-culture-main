from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.fraud.factories import BeneficiaryFraudCheckFactory
from pcapi.core.fraud.factories import DMSContentFactory
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import UserRole
from pcapi.scripts.uncancel_ok_dms_checks.main import uncancel_ok_dms_checks


@pytest.mark.usefixtures("db_session")
def test_uncancel_ok_dms_check():
    _script_author = UserFactory(id=6721024)
    seventeen_years_ago = datetime.utcnow() - relativedelta(years=17)
    user = UserFactory(age=17, validatedBirthDate=seventeen_years_ago, roles=[UserRole.UNDERAGE_BENEFICIARY])
    content = DMSContentFactory(state="accepte")
    BeneficiaryFraudCheckFactory(
        user=user, type=FraudCheckType.DMS, resultContent=content, eligibilityType=EligibilityType.UNDERAGE
    )

    (id_check,) = [fraud_check for fraud_check in user.beneficiaryFraudChecks if fraud_check.type == FraudCheckType.DMS]
    id_check.status = FraudCheckStatus.CANCELED

    uncancel_ok_dms_checks(not_dry=True)

    assert id_check.status == FraudCheckStatus.OK
