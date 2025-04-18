import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as providers_factories


@pytest.fixture(name="venue_provider")
def venue_provider_fixture():
    return providers_factories.VenueProviderFactory()


@pytest.fixture(name="api_key")
def api_key_fixture(venue_provider):
    return offerers_factories.ApiKeyFactory(provider=venue_provider.provider)


@pytest.fixture(name="public_client")
def public_client_fixture(client, api_key):
    return client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    # There are no draft offers on the public API
    @pytest.mark.parametrize(
        "status",
        set(educational_testing.STATUSES_ALLOWING_ARCHIVE_OFFER) - {models.CollectiveOfferDisplayedStatus.DRAFT},
    )
    def test_archive_collective_offers(self, db_session, public_client, venue_provider, status):
        offer = educational_factories.create_collective_offer_by_status(status, provider=venue_provider.provider)

        not_modified_offer = educational_factories.create_collective_offer_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=venue_provider.provider
        )

        response = public_client.post(
            "/v2/collective/offers/archive",
            json={"ids": [offer.id]},
        )

        assert response.status_code == 204
        db_session.refresh(offer)
        assert offer.isArchived

        db_session.refresh(not_modified_offer)
        assert not_modified_offer.isActive is True
        assert not_modified_offer.isArchived is False

    def test_archive_multiple_collective_offers(self, db_session, public_client, venue_provider):
        offers = [
            educational_factories.create_collective_offer_by_status(
                models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=venue_provider.provider
            ),
            educational_factories.create_collective_offer_by_status(
                models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=venue_provider.provider
            ),
        ]
        not_modified_offer = educational_factories.create_collective_offer_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, provider=venue_provider.provider
        )

        response = public_client.post(
            "/v2/collective/offers/archive",
            json={"ids": [offer.id for offer in offers]},
        )

        assert response.status_code == 204
        for offer in offers:
            db_session.refresh(offer)
            assert offer.isActive is False
            assert offer.isArchived

        db_session.refresh(not_modified_offer)
        assert not_modified_offer.isActive is True
        assert not_modified_offer.isArchived is False


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_archive_collective_offers_with_empty_ids(self, public_client):
        response = public_client.post(
            "/v2/collective/offers/archive",
            json={"ids": []},
        )

        assert response.status_code == 400
        assert response.json == {"ids": ["ids must have at least one value"]}

    @pytest.mark.parametrize(
        "status",
        set(educational_testing.STATUSES_NOT_ALLOWING_ARCHIVE_OFFER) - {models.CollectiveOfferDisplayedStatus.ARCHIVED},
    )
    def test_archive_not_allowed_collective_offers(self, public_client, venue_provider, db_session, status):
        offer = educational_factories.create_collective_offer_by_status(status, provider=venue_provider.provider)

        response = public_client.post(
            "/v2/collective/offers/archive",
            json={"ids": [offer.id]},
        )

        assert response.status_code == 400
        assert response.json == {"global": ["Cette action n'est pas autorisée sur une des offres"]}
        db_session.refresh(offer)
        assert offer.isArchived is False

    def test_archive_archived_collective_offers(self, public_client, venue_provider, db_session):
        offer = educational_factories.ArchivedPublishedCollectiveOfferFactory(provider=venue_provider.provider)

        response = public_client.post(
            "/v2/collective/offers/archive",
            json={"ids": [offer.id]},
        )

        assert response.status_code == 400
        db_session.refresh(offer)
        assert offer.isArchived is True


@pytest.mark.usefixtures("db_session")
class Returns404Test:

    def test_archive_collective_offers_with_wrong_provider(self, db_session, public_client):
        provider2 = providers_factories.ProviderFactory()
        offer = educational_factories.CollectiveOfferFactory(provider=provider2)

        response = public_client.post(
            "/v2/collective/offers/archive",
            json={"ids": [offer.id]},
        )

        assert response.status_code == 404
        assert response.json == {"ids": f"Les offres suivantes n'ont pas été trouvées: {{{offer.id}}}"}
        db_session.refresh(offer)
        assert offer.isArchived is False
