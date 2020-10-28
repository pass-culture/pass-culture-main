from datetime import datetime
from unittest.mock import patch
from freezegun import freeze_time

from pcapi.models import OfferSQLEntity, Product, Provider
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_provider_by_local_class
from pcapi.routes.serialization import serialize
from tests.conftest import TestClient
from pcapi.model_creators.generic_creators import (
    create_user,
    create_offerer,
    create_venue,
    create_user_offerer,
    API_URL,
    create_provider,
)
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.model_creators.specific_creators import (
    create_product_with_thing_type,
    create_product_with_event_type,
    create_offer_with_thing_product,
    create_offer_with_event_product,
)
from pcapi.utils.human_ids import humanize


class Returns200:
    def when_updating_offer_booking_email(self, app, db_session):
        # Given
        mocked_date = datetime(2020, 10, 15)

        user = create_user()
        offerer = create_offerer(
            date_created=mocked_date,
            date_modified_at_last_provider=mocked_date,
        )
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(
            offerer,
            date_created=mocked_date,
            date_modified_at_last_provider=mocked_date,
        )
        offer = create_offer_with_thing_product(
            venue,
            booking_email="old@example.com",
            date_created=mocked_date,
            date_modified_at_last_provider=mocked_date,
        )
        offer.product.dateCreated = mocked_date
        offer.product.dateModifiedAtLastProvider = mocked_date

        repository.save(offer, user, user_offerer)

        json = {
            "bookingEmail": "offer@example.com",
        }

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # Then
        assert response.status_code == 200
        assert response.json == {
            "id": humanize(offer.id),
        }
        assert OfferSQLEntity.query.get(offer.id).bookingEmail == "offer@example.com"

    @patch("pcapi.use_cases.update_an_offer.redis.add_offer_id")
    def when_updating_an_offer_expect_offer_id_to_be_added_to_redis(
        self, mock_add_offer_id_to_redis, app, db_session
    ):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, booking_email="old@example.com")

        repository.save(offer, user, user_offerer)

        json = {
            "bookingEmail": "offer@example.com",
        }

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # Then
        assert response.status_code == 200
        mock_add_offer_id_to_redis.assert_called_once_with(
            client=app.redis_client, offer_id=offer.id
        )

    def when_user_updating_thing_offer_is_linked_to_same_owning_offerer(
        self, app, db_session
    ):
        # Given
        user = create_user(email="editor@example.com")
        owning_offerer = create_offerer()
        user_offerer = create_user_offerer(user, owning_offerer)
        venue = create_venue(owning_offerer)
        product = create_product_with_thing_type(
            thing_name="Old Name", owning_offerer=owning_offerer
        )
        offer = create_offer_with_thing_product(venue=venue, product=product)
        repository.save(offer, user_offerer)
        offer_id = offer.id
        product_id = product.id

        json = {"name": "New Name"}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer_id)}", json=json)
        )

        # Then
        assert response.status_code == 200
        assert OfferSQLEntity.query.get(offer_id).name == "New Name"
        assert Product.query.get(product_id).name == "New Name"

    def when_user_updating_thing_offer_is_not_linked_to_owning_offerer(
        self, app, db_session
    ):
        # Given
        user = create_user(email="editor@example.com")
        owning_offerer = create_offerer(siren="123456789")
        editor_offerer = create_offerer(siren="123456780")
        editor_user_offerer = create_user_offerer(user, editor_offerer)
        venue = create_venue(editor_offerer)
        product = create_product_with_thing_type(
            thing_name="Old Name", owning_offerer=owning_offerer
        )
        offer = create_offer_with_thing_product(venue=venue, product=product)
        repository.save(offer, editor_user_offerer, owning_offerer)
        offer_id = offer.id
        product_id = product.id

        json = {"name": "New Name"}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # Then
        assert response.status_code == 200
        assert OfferSQLEntity.query.get(offer_id).name == "New Name"
        assert Product.query.get(product_id).name == "Old Name"

    def when_user_updating_thing_offer_has_rights_on_offer_but_no_owningOfferer_for_thing(
        self, app, db_session
    ):
        # Given
        user = create_user(email="editor@example.com")
        offerer = create_offerer(siren="123456780")
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        product = create_product_with_thing_type(
            thing_name="Old Name", owning_offerer=None
        )
        offer = create_offer_with_thing_product(venue=venue, product=product)
        repository.save(offer, user_offerer)

        json = {"name": "New Name"}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # Then
        assert response.status_code == 200
        assert OfferSQLEntity.query.one().name == "New Name"
        assert Product.query.one().name == "Old Name"

    def when_deactivate_offer_from_provider(self, app, db_session):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        provider = activate_provider("TiteLiveStocks")
        offer = create_offer_with_thing_product(
            venue, id_at_providers="id_provider", last_provider_id=provider.id
        )
        repository.save(offer, user_offerer)
        offer_id = offer.id

        json = {"isActive": False}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # Then
        assert response.status_code == 200
        assert not OfferSQLEntity.query.get(offer_id).isActive

    def when_activate_offer_from_provider(self, app, db_session):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        provider = activate_provider("TiteLiveStocks")
        offer = create_offer_with_thing_product(
            venue,
            is_active=False,
            id_at_providers="id_provider",
            last_provider_id=provider.id,
        )
        repository.save(offer, user_offerer)
        offer_id = offer.id

        json = {"isActive": True}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # Then
        assert response.status_code == 200
        assert OfferSQLEntity.query.get(offer_id).isActive

    def when_patch_an_offer_that_is_imported_from_titelive(self, app, db_session):
        # given
        tite_live_provider = Provider.query.filter(
            Provider.localClass == "TiteLiveThings"
        ).first()

        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(
            venue,
            booking_email="old@example.com",
            last_provider_id=tite_live_provider.id,
        )

        repository.save(offer, user, user_offerer)
        json = {
            "bookingEmail": "offer@example.com",
        }

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # then
        assert response.status_code == 200

    def when_patch_an_offer_that_is_imported_from_allocine(self, app, db_session):
        # given
        allocine_provider = Provider.query.filter(
            Provider.localClass == "AllocineStocks"
        ).first()

        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(
            venue,
            booking_email="old@example.com",
            last_provider_id=allocine_provider.id,
        )

        repository.save(offer, user, user_offerer)
        json = {
            "isDuo": "true",
        }

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # then
        assert response.status_code == 200


class Returns400:
    def when_trying_to_patch_forbidden_attributes(self, app, db_session):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        thing_product = create_product_with_thing_type(
            thing_name="Old Name", owning_offerer=None
        )
        offer = create_offer_with_thing_product(venue=venue, product=thing_product)

        repository.save(offer, user, user_offerer)

        forbidden_keys = [
            "idAtProviders",
            "dateModifiedAtLastProvider",
            "thumbCount",
            "owningOffererId",
            "id",
            "lastProviderId",
            "dateCreated",
        ]

        json = {
            "id": 1,
            "dateCreated": serialize(datetime(2019, 1, 1)),
            "lastProviderId": 1,
            "owningOffererId": "AA",
            "idAtProviders": 1,
            "dateModifiedAtLastProvider": serialize(datetime(2019, 1, 1)),
            "thumbCount": 2,
        }

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # Then
        assert response.status_code == 400
        assert response.json["owningOffererId"] == [
            "Vous ne pouvez pas changer cette information"
        ]
        for key in forbidden_keys:
            assert key in response.json

    def when_offer_name_is_too_long(self, app, db_session):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        thing_product = create_product_with_thing_type(
            thing_name="Old Name", owning_offerer=None
        )
        offer = create_offer_with_thing_product(venue, product=thing_product)

        repository.save(offer, user, user_offerer)

        json = {
            "name": "Nom vraiment très long excédant la taille maximale (nom de plus de quatre-vingt-dix caractères)",
        }

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # Then
        assert response.status_code == 400
        assert response.json["name"] == [
            "Le titre de l’offre doit faire au maximum 90 caractères."
        ]

    def when_trying_to_patch_an_imported_offer(self, app, db_session):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        thing_product = create_product_with_thing_type(
            thing_name="Old Name", owning_offerer=None
        )
        provider = create_provider(
            idx=1, local_class="OpenAgenda", is_active=True, is_enable_for_pro=True
        )
        offer = create_offer_with_event_product(
            booking_email="wrong-email@example.net",
            venue=venue,
            product=thing_product,
            id_at_providers="24561461",
            last_provider=provider,
        )

        repository.save(offer, user, user_offerer)

        json = {"isDuo": False, "isActive": True, "bookingEmail": "offer@example.com"}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # Then
        assert response.status_code == 400
        assert response.json["global"] == [
            "Les offres importées ne sont pas modifiables"
        ]

    def when_trying_to_patch_any_allocine_offer_field_except_is_duo(
        self, app, db_session
    ):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        provider = get_provider_by_local_class("AllocineStocks")
        offer = create_offer_with_event_product(
            venue, id_at_providers="24561461", last_provider=provider
        )

        repository.save(offer, user, user_offerer)

        json = {
            "isNational": True,
            "bookingEmail": "new-email@example.com",
            "name": "Autre nom pour mon offre",
        }

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # Then
        assert response.status_code == 400
        assert response.json["isNational"] == ["Vous ne pouvez pas modifier ce champ"]
        assert response.json["bookingEmail"] == ["Vous ne pouvez pas modifier ce champ"]
        assert response.json["name"] == ["Vous ne pouvez pas modifier ce champ"]


class Returns403:
    def when_user_is_not_attached_to_offerer(self, app, db_session):
        # Given
        user = create_user()
        offerer = create_offerer()
        event_product = create_product_with_event_type(event_name="Old name")
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue=venue, product=event_product)

        repository.save(event_product, offer, user, venue)

        json = {"name": "New name", "venueId": humanize(venue.id)}

        # When
        response = (
            TestClient(app.test_client())
            .with_auth(user.email)
            .patch(f"{API_URL}/offers/{humanize(offer.id)}", json=json)
        )

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]


class Returns404:
    def test_returns_404_if_offer_does_not_exist(self, app, db_session):
        # given
        user = create_user()
        repository.save(user)
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

        # when
        response = auth_request.patch("/offers/ADFGA", json={})

        # then
        assert response.status_code == 404
