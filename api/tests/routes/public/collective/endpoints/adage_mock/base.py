import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIRestrictedEnvEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


class AdageMockEndpointHelper(PublicAPIRestrictedEnvEndpointHelper):
    default_factory = factories.PendingCollectiveBookingFactory

    def setup_base_resource(self, *, factory=None, provider=None, venue=None, deposit=None) -> models.CollectiveBooking:
        venue = venue or self.setup_venue()
        deposit = deposit or factories.EducationalDepositFactory()
        factory = factory or self.default_factory
        offer = factories.CollectiveOfferFactory(provider=provider, venue=venue)
        return factory(
            collectiveStock__collectiveOffer=offer,
            educationalInstitution=deposit.educationalInstitution,
            educationalYear=deposit.educationalYear,
        )

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        pending_booking = self.setup_base_resource()
        self.assert_request_has_expected_result(
            client.with_explicit_token(plain_api_key),
            url_params={"booking_id": pending_booking.id},
            expected_status_code=404,
            expected_error_json={"code": "BOOKING_NOT_FOUND"},
        )

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        pending_booking = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        self.assert_request_has_expected_result(
            client.with_explicit_token(plain_api_key),
            url_params={"booking_id": pending_booking.id},
            expected_status_code=404,
            expected_error_json={"code": "BOOKING_NOT_FOUND"},
        )
