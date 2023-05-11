import json

from pcapi.connectors.beneficiaries import ubble
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble.api import _ubble_readable_score
from pcapi.core.fraud.ubble.api import _ubble_result_fraud_item
from pcapi.core.subscription.ubble import models as ubble_models
from pcapi.core.users import factories as user_factories

from tests.core.subscription.test_factories import UbbleIdentificationResponseFactory
from tests.test_utils import json_default


class UbbleFraudChecksTest:
    def test_ubble_reason_code_details(self, ubble_mocker):
        error_codes = list(fraud_models.UBBLE_REASON_CODE_MAPPING.keys())
        reason_codes = [fraud_models.UBBLE_REASON_CODE_MAPPING[error_code] for error_code in error_codes]
        ubble_response = UbbleIdentificationResponseFactory(error_codes=error_codes)

        with ubble_mocker(
            ubble_response.data.attributes.identification_id,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            content = ubble.get_content(ubble_response.data.attributes.identification_id)

        user = user_factories.BaseUserFactory()
        fraud_item = _ubble_result_fraud_item(user, content)
        details = set(fraud_item.detail.split(" | "))

        expected_details = {
            ubble_models.UBBLE_CODE_ERROR_MAPPING.get(reason_code).detail_message for reason_code in reason_codes
        }
        expected_details.add(f"Ubble score {_ubble_readable_score(content.score)}: {content.comment}")

        assert details == expected_details
        assert fraud_item.status == fraud_models.FraudStatus.SUSPICIOUS
        assert all(reason_code in fraud_item.reason_codes for reason_code in reason_codes)
