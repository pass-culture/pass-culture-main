import factory
import pytest

from pcapi.core.offerers.factories import ProviderFactory
from pcapi.core.offers.factories import ThingProductFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.providers.models import Provider
from pcapi.core.testing import BaseFactory
from pcapi.scripts.migrate_id_at_providers import OfferScript
from pcapi.scripts.migrate_id_at_providers import migrate_id_at_providers


def create_offer(siret, isbn, provider_id) -> OfferScript:
    return OfferFactory(idAtProvidersToMigrate=f"{isbn}@{siret}", lastProviderId=provider_id)


def create_provider(idx) -> Provider:
    return ProviderFactory(id=idx)


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
        provider = create_provider(idx=123)
        siret = "532336401"
        isbn = "123456789"
        isbn2 = "987654321"
        first_offer = create_offer(provider_id=provider.id, siret=siret, isbn=isbn)
        second_offer = create_offer(provider_id=provider.id, siret=siret, isbn=isbn2)
        nb_offer_per_page = 1

        # When
        expected = migrate_id_at_providers(nb_offer_per_page)

        # Then
        assert expected == 2

        updated_offer = OfferScript.query.get(first_offer.id)
        assert updated_offer.idAtProvider == isbn
        assert updated_offer.idAtProvidersToMigrate == f"{isbn}@{siret}"

        second_updated_offer = OfferScript.query.get(second_offer.id)
        assert second_updated_offer.idAtProvider == isbn2
        assert second_updated_offer.idAtProvidersToMigrate == f"{isbn2}@{siret}"
