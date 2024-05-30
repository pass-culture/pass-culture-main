import argparse

# pylint: disable=unused-import
from pcapi.core.bookings import api as bookings_api
import pcapi.core.providers.api as providers_api
import pcapi.core.providers.models as providers_models
from pcapi.flask_app import app


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser(description="Create venue provider with fake siret")
    parser.add_argument("--venue-id", type=int, help="The venue id", required=True)
    parser.add_argument("--fake-siret", type=str, help="The fake siret", required=True)
    args = parser.parse_args()

    venue_id = args.venue_id
    fake_siret = args.fake_siret
    provider_id = 63

    payload = providers_models.VenueProviderCreationPayload(venueIdAtOfferProvider=fake_siret)
    providers_api.create_venue_provider(provider_id, venue_id, payload)
