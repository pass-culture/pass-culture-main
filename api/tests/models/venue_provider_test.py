import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.providers.api import activate_provider
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.models import VenueProvider
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.generic_creators import create_venue_provider
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
def test_venue_provider_nOffers():
    venue = offerers_factories.VenueFactory()
    provider1 = providers_factories.ProviderFactory()
    offers_factories.OfferFactory(venue=venue, lastProvider=provider1)
    offers_factories.OfferFactory(venue=venue, lastProvider=provider1)
    offers_factories.OfferFactory(venue=venue, lastProvider=provider1, isActive=False)  # not counted
    offers_factories.OfferFactory(venue=venue, lastProvider=None)  # not counted
    provider2 = providers_factories.ProviderFactory()
    offers_factories.OfferFactory(venue=venue, lastProvider=provider2)

    venue_provider1 = providers_factories.VenueProviderFactory(venue=venue, provider=provider1)
    venue_provider2 = providers_factories.VenueProviderFactory(venue=venue, provider=provider2)
    assert venue_provider1.nOffers == 2
    assert venue_provider2.nOffers == 1


@pytest.mark.usefixtures("db_session")
def test_raise_errors_if_venue_provider_already_exists_with_same_information(app):
    # given
    provider = providers_factories.APIProviderFactory()
    offerer = create_offerer()
    venue = create_venue(offerer, name="Librairie Titelive", siret="77567146400110")
    venue_provider = create_venue_provider(venue, provider, venue_id_at_offer_provider="775671464")
    repository.save(venue_provider)

    venue_provider2 = create_venue_provider(venue, provider, venue_id_at_offer_provider="775671464")
    # when
    with pytest.raises(ApiErrors) as errors:
        repository.save(venue_provider2)

    # then
    assert errors.value.errors["global"] == ["Votre lieu est déjà lié à cette source"]


@pytest.mark.usefixtures("db_session")
def test_should_have_attribute_matching_allocine_when_having_allocine_provider(app):
    # given
    provider = activate_provider("AllocineStocks")
    offerer = create_offerer()
    venue = create_venue(offerer)
    venue_provider = create_venue_provider(venue, provider)
    repository.save(venue_provider)

    # when
    allocine_venue_provider = VenueProvider.query.first()

    # then
    assert allocine_venue_provider.isFromAllocineProvider


@pytest.mark.usefixtures("db_session")
def test_should_not_be_matched_has_allocine_provider_with_other_provider(app):
    # given
    provider = providers_factories.APIProviderFactory()
    offerer = create_offerer()
    venue = create_venue(offerer)
    venue_provider = create_venue_provider(venue, provider)
    repository.save(venue_provider)

    # when
    allocine_venue_provider = VenueProvider.query.first()

    # then
    assert not allocine_venue_provider.isFromAllocineProvider
