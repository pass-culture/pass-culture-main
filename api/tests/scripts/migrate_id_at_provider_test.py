import pytest

from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.models import Offer
from pcapi.scripts.migrate_id_at_provider import migrate_id_at_provider

from tests.core.providers.test_api import create_offer


class MigrateIdAtProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_copy_isbn_to_id_at_providers(self, app):
        # Given
        isbn = "123456789"
        venue = VenueFactory()
        create_offer(isbn, venue)

        # When
        migrate_id_at_provider()

        # Then
        updated_offer = Offer.query.first()
        assert updated_offer.idAtProvider == isbn
        assert updated_offer.idAtProviders == isbn
