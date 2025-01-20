import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.models import db
from pcapi.scripts.provider_clean_old_integration_data.main import _clean_id_a_provider_for_provider
from pcapi.scripts.provider_clean_old_integration_data.main import clean_old_provider_data


@pytest.mark.usefixtures("db_session")
def test_clean_old_provider_data():
    provider_1 = providers_factories.ProviderFactory(name="Old Provider that should be deprecated")
    provider_already_deprecated = providers_factories.ProviderFactory(name="[DÉPRÉCIÉ] Old Provider")
    provider_3 = providers_factories.ProviderFactory()
    offer_provider_1 = offers_factories.ThingOfferFactory(lastProvider=provider_1, idAtProvider="12345")
    offer_provider_2 = offers_factories.EventOfferFactory(lastProvider=provider_already_deprecated, idAtProvider=None)
    offer_provider_3 = offers_factories.ThingOfferFactory(lastProvider=provider_3, idAtProvider="offerId3")

    clean_old_provider_data([provider_1.id, provider_already_deprecated.id])

    db.session.refresh(offer_provider_1)
    db.session.refresh(offer_provider_2)
    db.session.refresh(offer_provider_3)

    # should be deprecated
    assert provider_1.name == "[DÉPRÉCIÉ] Old Provider that should be deprecated"
    assert not provider_1.enabledForPro
    assert not provider_1.isActive
    assert not offer_provider_1.idAtProvider
    assert provider_already_deprecated.name == "[DÉPRÉCIÉ] Old Provider"
    assert not provider_already_deprecated.enabledForPro
    assert not provider_already_deprecated.isActive
    assert not offer_provider_2.idAtProvider

    # should stay the same
    assert offer_provider_3.idAtProvider
    assert provider_3.enabledForPro
    assert provider_3.isActive


@pytest.mark.usefixtures("db_session")
def test_clean_id_at_providers():
    provider_1 = providers_factories.ProviderFactory(name="Old Provider that should be deprecated")
    provider_3 = providers_factories.ProviderFactory()
    offer_provider_1 = offers_factories.ThingOfferFactory(lastProvider=provider_1, idAtProvider="12345")
    offer_provider_2 = offers_factories.ThingOfferFactory(lastProvider=provider_1, idAtProvider="12346")
    offer_provider_3 = offers_factories.ThingOfferFactory(lastProvider=provider_1, idAtProvider="12347")
    offer_provider_4 = offers_factories.ThingOfferFactory(lastProvider=provider_3, idAtProvider="offerId3")

    _clean_id_a_provider_for_provider(provider_1.id, batch_size=2)

    # should be deprecated
    assert not offer_provider_1.idAtProvider
    assert not offer_provider_2.idAtProvider
    assert not offer_provider_3.idAtProvider

    # should stay the same
    assert offer_provider_4.idAtProvider
