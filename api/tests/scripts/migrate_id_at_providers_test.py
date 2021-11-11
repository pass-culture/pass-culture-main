import pytest

from pcapi.core.offers.models import Offer
from pcapi.scripts.migrate_id_at_providers import migrate_id_at_providers

from tests.core.providers.test_api import create_offer


class MigrateIdAtProvidersTest:
    @pytest.mark.usefixtures("db_session")
    def test_extract_isbn_from_id_at_providers(self, app):
        # Given
        siret = "532336401"
        isbn = "123456789"
        create_offer(isbn, siret)

        # When
        migrate_id_at_providers()

        # Then
        updated_offer = Offer.query.first()
        assert updated_offer.idAtProvider == isbn
        assert updated_offer.idAtProviders == f"{isbn}@{siret}"
