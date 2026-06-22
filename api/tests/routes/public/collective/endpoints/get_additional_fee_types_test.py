import pytest

from pcapi.core.educational.models import CollectiveAdditionalFeeType

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")


class GetCollectiveAdditionalFeeTypesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/additional-fee-types"
    endpoint_method = "get"

    def test_get_types(self):
        plain_api_key, _ = self.setup_provider()

        response = self.make_request(plain_api_key)

        assert response.status_code == 200
        assert response.json == [{"name": fee_type.name} for fee_type in CollectiveAdditionalFeeType]
