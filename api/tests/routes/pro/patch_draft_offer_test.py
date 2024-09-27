from datetime import datetime

import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.routes.native.v1.serialization.offerers import VenueTypeCode
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_patch_draft_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            name="Name",
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venue=venue,
            description="description",
            url="http://example.com/offer",
        )

        data = {
            "name": "New name",
            "description": "New description",
            "subcategoryId": subcategories.ABO_PLATEFORME_VIDEO.id,
            "extraData": {"gtl_id": "07000000"},
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/draft/{offer.id}", json=data)
        assert response.status_code == 200
        assert response.json["id"] == offer.id
        assert response.json["venue"]["id"] == offer.venue.id
        assert response.json["productId"] == None

        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.subcategoryId == subcategories.ABO_PLATEFORME_VIDEO.id
        assert updated_offer.description == "New description"
        assert not updated_offer.product

    @override_features(WIP_EAN_CREATION=True)
    def test_patch_draft_offer_without_product_with_new_ean_should_succeed(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            name="Name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            description="description",
            extraData={"ean": "1111111111111"},
        )

        data = {"extraData": {"ean": "2222222222222"}}
        response = client.with_session_auth("user@example.com").patch(f"offers/draft/{offer.id}", json=data)

        assert response.status_code == 200
        assert response.json["id"] == offer.id

        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.extraData["ean"] == "2222222222222"

    @override_features(WIP_EAN_CREATION=True)
    def test_patch_draft_offer_without_product(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            name="Name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            description="description",
            url="http://example.com/offer",
        )

        data = {
            "name": "New name",
            "description": "New description",
            "extraData": {"author": "Nicolas Gogol"},
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/draft/{offer.id}", json=data)
        assert response.status_code == 200
        assert response.json["id"] == offer.id
        assert response.json["venue"]["id"] == offer.venue.id
        assert response.json["productId"] == None

        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert updated_offer.description == "New description"
        assert not updated_offer.product

    def test_patch_draft_with_extra_data(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.EventOfferFactory(
            name="Film",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            isDuo=False,
            description="description",
            extraData=None,
        )

        data = {
            "name": "Film",
            "description": "description",
            "subcategoryId": subcategories.SEANCE_CINE.id,
            "extraData": {"stageDirector": "Greta Gerwig"},
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/draft/{offer.id}", json=data)
        assert response.status_code == 200
        assert response.json["id"] == offer.id

        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.extraData == {"stageDirector": "Greta Gerwig"}

    def test_patch_draft_offer_with_empty_extra_data(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider, venue=venue)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
        offer = offers_factories.EventOfferFactory(
            name="Film",
            venue=venue_provider.venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProviderId=cinema_provider_pivot.provider.id,
            isDuo=False,
            description="description",
            extraData=None,
        )

        data = {
            "name": "Film",
            "description": "description",
            "subcategoryId": subcategories.SEANCE_CINE.id,
            "extraData": {
                "author": "",
                "gtl_id": "",
                "performer": "",
                "showType": "",
                "showSubType": "",
                "speaker": "",
                "stageDirector": "",
                "visa": "",
            },
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/draft/{offer.id}", json=data)
        assert response.status_code == 200
        assert response.json["id"] == offer.id

        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.extraData == {
            "author": "",
            "gtl_id": "",
            "performer": "",
            "showType": "",
            "showSubType": "",
            "speaker": "",
            "stageDirector": "",
            "visa": "",
        }

    @override_features(WIP_EAN_CREATION=False)
    def test_patch_draft_offer_linked_to_product_with_same_extra_data(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        product = offers_factories.ProductFactory(
            name="Name",
            description="description",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"gtl_id": "07000000", "ean": "1111111111111"},
        )
        offer = offers_factories.OfferFactory(
            venue=venue,
            url="http://example.com/offer",
            product=product,
        )

        data = {
            "extraData": {"gtl_id": "07000000", "ean": "1111111111111"},
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/draft/{offer.id}", json=data)
        assert response.status_code == 200
        assert response.json["id"] == offer.id

        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.extraData == {"gtl_id": "07000000", "ean": "1111111111111"}

    def test_patch_draft_offer_with_existing_extra_data_with_new_extra_data(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.EventOfferFactory(
            name="Film",
            venue=venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            isDuo=False,
            description="description",
            extraData={
                "cast": ["Joan Baez", "Joe Cocker", "David Crosby"],
                "eidr": "10.5240/ADBD-3CAA-43A0-7BF0-86E2-K",
                "type": "FEATURE_FILM",
                "visa": "37205",
                "title": "Woodstock",
                "genres": ["DOCUMENTARY", "HISTORICAL", "MUSIC"],
                "credits": [
                    {"person": {"lastName": "Wadleigh", "firstName": "Michael"}, "position": {"name": "DIRECTOR"}}
                ],
                "runtime": 185,
                "theater": {"allocine_room_id": "W0135", "allocine_movie_id": 2634},
                "backlink": "https://www.allocine.fr/film/fichefilm_gen_cfilm=2634.html",
                "synopsis": "Le plus important rassemblement de la musique pop de ces vingt derni\u00e8res ann\u00e9es. Des groupes qui ont marqu\u00e9 leur \u00e9poque et une jeunesse qui a marqu\u00e9 la sienne.",
                "companies": [{"name": "Wadleigh-Maurice", "activity": "Production"}],
                "countries": ["USA"],
                "posterUrl": "https://fr.web.img2.acsta.net/pictures/14/06/20/12/25/387023.jpg",
                "allocineId": 2634,
                "originalTitle": "Woodstock",
                "stageDirector": "Michael Wadleigh",
                "productionYear": 1970,
            },
        )

        data = {
            "name": "Film",
            "description": "description",
            "subcategoryId": subcategories.SEANCE_CINE.id,
            "extraData": {
                "author": "",
                "gtl_id": "",
                "performer": "",
                "showType": "",
                "showSubType": "",
                "speaker": "",
                "stageDirector": "Greta Gerwig",
                "visa": "",
                "cast": ["Joan Baez", "Joe Cocker", "David Crosby"],
                "eidr": "10.5240/ADBD-3CAA-43A0-7BF0-86E2-K",
                "type": "FEATURE_FILM",
                "title": "Woodstock",
                "genres": ["DOCUMENTARY", "HISTORICAL", "MUSIC"],
                "credits": [
                    {"person": {"lastName": "Wadleigh", "firstName": "Michael"}, "position": {"name": "DIRECTOR"}}
                ],
                "runtime": 185,
                "theater": {"allocine_room_id": "W0135", "allocine_movie_id": 2634},
                "backlink": "https://www.allocine.fr/film/fichefilm_gen_cfilm=2634.html",
                "synopsis": "Le plus important rassemblement de la musique pop de ces vingt derni\u00e8res ann\u00e9es. Des groupes qui ont marqu\u00e9 leur \u00e9poque et une jeunesse qui a marqu\u00e9 la sienne.",
                "companies": [{"name": "Wadleigh-Maurice", "activity": "Production"}],
                "countries": ["USA"],
                "posterUrl": "https://fr.web.img2.acsta.net/pictures/14/06/20/12/25/387023.jpg",
                "allocineId": 2634,
                "originalTitle": "Woodstock",
                "productionYear": 1970,
            },
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/draft/{offer.id}", json=data)
        assert response.status_code == 200
        assert response.json["id"] == offer.id

        updated_offer = Offer.query.get(offer.id)
        assert updated_offer.extraData == {
            "cast": ["Joan Baez", "Joe Cocker", "David Crosby"],
            "eidr": "10.5240/ADBD-3CAA-43A0-7BF0-86E2-K",
            "type": "FEATURE_FILM",
            "visa": "",
            "title": "Woodstock",
            "genres": ["DOCUMENTARY", "HISTORICAL", "MUSIC"],
            "credits": [{"person": {"lastName": "Wadleigh", "firstName": "Michael"}, "position": {"name": "DIRECTOR"}}],
            "runtime": 185,
            "theater": {"allocine_room_id": "W0135", "allocine_movie_id": 2634},
            "backlink": "https://www.allocine.fr/film/fichefilm_gen_cfilm=2634.html",
            "synopsis": "Le plus important rassemblement de la musique pop de ces vingt derni\u00e8res ann\u00e9es. Des groupes qui ont marqu\u00e9 leur \u00e9poque et une jeunesse qui a marqu\u00e9 la sienne.",
            "companies": [{"name": "Wadleigh-Maurice", "activity": "Production"}],
            "countries": ["USA"],
            "posterUrl": "https://fr.web.img2.acsta.net/pictures/14/06/20/12/25/387023.jpg",
            "allocineId": 2634,
            "originalTitle": "Woodstock",
            "stageDirector": "Greta Gerwig",
            "productionYear": 1970,
            "author": "",
            "gtl_id": "",
            "performer": "",
            "showType": "",
            "showSubType": "",
            "speaker": "",
        }


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_trying_to_patch_forbidden_attributes(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CARTE_MUSEE.id,
            name="New name",
            url="http://example.com/offer",
            description="description",
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "dateCreated": format_into_utc_date(datetime(2019, 1, 1)),
            "dateModifiedAtLastProvider": format_into_utc_date(datetime(2019, 1, 1)),
            "id": 1,
            "idAtProviders": 1,
            "lastProviderId": 1,
            "thumbCount": 2,
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
        }
        response = client.with_session_auth("user@example.com").patch(f"offers/draft/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["lastProviderId"] == ["Vous ne pouvez pas changer cette information"]
        forbidden_keys = {
            "dateCreated",
            "dateModifiedAtLastProvider",
            "id",
            "idAtProviders",
            "lastProviderId",
            "thumbCount",
        }
        for key in forbidden_keys:
            assert key in response.json

    @override_features(WIP_EAN_CREATION=True)
    def when_trying_to_patch_offer_with_product_with_new_ean(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, venueTypeCode=VenueTypeCode.RECORD_STORE
        )
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={"ean": "1111111111111"},
            name="Name",
            description="description",
        )
        offer = offers_factories.OfferFactory(
            venue=venue,
            product=product,
        )

        data = {"extraData": {"ean": "2222222222222"}}
        response = client.with_session_auth("user@example.com").patch(f"offers/draft/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Les extraData des offres avec produit ne sont pas modifialbles"]

    def when_trying_to_patch_product(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, venueTypeCode=VenueTypeCode.RECORD_STORE
        )
        offer = offers_factories.OfferFactory(
            name="Name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            description="description",
        )
        product = offers_factories.ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)

        data = {"product_id": product.id}
        response = client.with_session_auth("user@example.com").patch(f"offers/draft/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["product_id"] == ["Vous ne pouvez pas changer cette information"]


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, client):
        email = "user@example.com"
        offer = offers_factories.OfferFactory(
            name="Old name",
            subcategoryId=subcategories.CARTE_MUSEE.id,
            url="http://example.com/offer",
            description="description",
        )
        offerers_factories.UserOffererFactory(user__email=email)

        data = {"name": "New name"}
        response = client.with_session_auth(email).patch(f"/offers/draft/{offer.id}", json=data)

        assert response.status_code == 403
        msg = "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        assert response.json["global"] == [msg]
        assert Offer.query.get(offer.id).name == "Old name"


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_returns_404_if_offer_does_not_exist(self, client):
        email = "user@example.com"
        users_factories.UserFactory(email=email)
        response = client.with_session_auth(email).patch("/offers/draft/12345", json={})
        assert response.status_code == 404
