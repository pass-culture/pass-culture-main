from flask import url_for
import pytest

import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories


class GetCollectiveBookingTest:
    def test_get_collective_booking(self, client):
        vp = providers_factories.VenueProviderFactory(isActive=True)
        offerers_factories.ApiKeyFactory(provider=vp.provider, offerer=vp.venue.managingOfferer)

        booking = educational_factories.UsedCollectiveBookingFactory(collectiveStock__collectiveOffer__venue=vp.venue)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        response = client.get(url_for("pro_public_api_v2.get_collective_booking", booking_id=booking.id))

        assert response.status_code == 200
        assert response.json == {
            "id": booking.id,
            "status": booking.status.value,
            "dateUsed": booking.dateUsed.isoformat(),
            "cancellationLimitDate": booking.cancellationLimitDate.isoformat(),
            "dateCreated": booking.dateCreated.isoformat(),
            "confirmationDate": booking.confirmationDate.isoformat(),
            "educationalYear": {
                "adageId": booking.educationalYear.adageId,
                "beginningDate": booking.educationalYear.beginningDate.isoformat(),
                "expirationDate": booking.educationalYear.expirationDate.isoformat(),
            },
            "venueId": booking.venueId,
        }

    def test_not_found_if_booking_does_not_exist(self, client):
        vp = providers_factories.VenueProviderFactory(isActive=True)
        offerers_factories.ApiKeyFactory(provider=vp.provider, offerer=vp.venue.managingOfferer)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        response = client.get(url_for("pro_public_api_v2.get_collective_booking", booking_id=-1))

        assert response.status_code == 404

    def test_not_found_if_missing_access_rights(self, client):
        offerers_factories.ApiKeyFactory()
        booking = educational_factories.CollectiveBookingFactory()

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        response = client.get(url_for("pro_public_api_v2.get_collective_booking", booking_id=booking.id))

        assert response.status_code == 404
