import factory
import pytest

from pcapi.core.offers.factories import ThingProductFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.testing import BaseFactory
from pcapi.scripts.migrate_id_at_providers import OfferScript
from pcapi.scripts.migrate_id_at_providers import migrate_id_at_providers


def create_offer(isbn, siret):
    return OfferFactory(idAtProvidersToMigrate=f"{isbn}@{siret}")


class OfferFactory(BaseFactory):
    class Meta:
        model = OfferScript

    product = factory.SubFactory(ThingProductFactory)
    venue = factory.SubFactory(VenueFactory)
    subcategoryId = factory.SelfAttribute("product.subcategoryId")
    name = factory.SelfAttribute("product.name")
    description = factory.SelfAttribute("product.description")
    url = factory.SelfAttribute("product.url")
    audioDisabilityCompliant = False
    mentalDisabilityCompliant = False
    motorDisabilityCompliant = False
    visualDisabilityCompliant = False


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
        updated_offer = OfferScript.query.first()
        assert updated_offer.idAtProvider == isbn
        assert updated_offer.idAtProviders == isbn
        assert updated_offer.idAtProvidersToMigrate == f"{isbn}@{siret}"
