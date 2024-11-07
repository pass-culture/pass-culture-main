from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors import api_adresse
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.geography import models as geography_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferStatus
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

    @override_features(WIP_SPLIT_OFFER=True)
    @override_features(WIP_ENABLE_OFFER_ADDRESS=False)
    @override_features(WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE=False)
    @pytest.mark.parametrize(
        "is_venue_address,address_payload,return_value,expected_data",
        [
            (
                False,
                {
                    "city": "LA ROCHE-SUR-YON",
                    "latitude": 46.66979,
                    "longitude": -1.42979,
                    "postalCode": "85000",
                    "street": "11 RUE GEORGES CLEMENCEAU",
                    "label": "Librairie des mangas",
                    "isManualEdition": False,
                    "isVenueAddress": False,
                },
                api_adresse.AddressInfo(
                    score=1,
                    city="LA ROCHE-SUR-YON",
                    latitude=46.66979,
                    longitude=-1.42979,
                    postcode="85000",
                    label="11 Rue Georges Clémenceau 85000 La Roche-sur-Yon",
                    street="11 Rue Georges Clémenceau",
                    citycode="85191",
                    id="85191_0940_00011",
                ),
                {
                    "city": "LA ROCHE-SUR-YON",
                    "departmentCode": "85",
                    "latitude": 46.66979,
                    "longitude": -1.42979,
                    "postalCode": "85000",
                    "street": "11 Rue Georges Clémenceau",
                    "label": "Librairie des mangas",
                    "inseeCode": "85191",
                    "banId": "85191_0940_00011",
                    "isLinkedToVenue": False,
                    "isManualEdition": False,
                },
            ),
            (
                True,
                {
                    "city": "Paris",
                    "latitude": 48.87004,
                    "longitude": 2.37850,
                    "postalCode": "75002",
                    "street": "1 boulevard Poissonnière",
                    "isManualEdition": False,
                    "isVenueAddress": True,
                },
                api_adresse.AddressInfo(
                    score=1,
                    city="Paris",
                    latitude=48.87004,
                    longitude=2.37850,
                    postcode="75002",
                    label="1 boulevard Poissonnière 75002 Paris",
                    street="1 boulevard Poissonnière",
                    citycode="75002",
                    id="75102_7560_00001",
                ),
                {
                    "city": "Paris",
                    "departmentCode": "75",
                    "latitude": 48.87004,
                    "longitude": 2.37850,
                    "postalCode": "75002",
                    "street": "1 boulevard Poissonnière",
                    "inseeCode": "75102",
                    "banId": "75102_7560_00001",
                    "isLinkedToVenue": True,
                    "isManualEdition": False,
                },
            ),
        ],
    )
    def test_first_step_funnel_creation_shouldnt_create_offer_offerer_address_ff_off(
        self, client, is_venue_address, address_payload, return_value, expected_data
    ):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        data = {
            "name": "New draft offer",
            "description": "This is a new draft offer",
            "subcategoryId": subcategories.FESTIVAL_SPECTACLE.id,
            "venueId": venue.id,
            "extraData": {
                "author": "",
                "ean": "",
                "gtl_id": "",
                "performer": "",
                "showSubType": 1202,
                "showType": 1200,
                "speaker": "",
                "stageDirector": "",
                "visa": "",
            },
        }
        user_email = user_offerer.user.email
        response = client.with_session_auth(user_email).post(f"/offers/draft", json=data)
        assert response.status_code == 201

        draft_offer = Offer.query.one()
        offer_id = draft_offer.id
        response = client.with_session_auth(user_email).get(f"/offers/{offer_id}")
        assert response.status_code == 200
        assert response.json["status"] == OfferStatus.DRAFT.value
        assert response.json["id"] == draft_offer.id
        assert not response.json.get("address")
        assert draft_offer.offererAddressId is None
        assert draft_offer.status is OfferStatus.DRAFT

        data = {
            "audioDisabilityCompliant": True,
            "isNational": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "withdrawalDelay": 172800,
            "withdrawalDetails": "",
            "visualDisabilityCompliant": False,
            "withdrawalType": "by_email",
            "bookingEmail": None,
            "shouldSendMail": True,
            "bookingContact": "test@mail.com",
            "address": {
                **address_payload,
                "label": venue.common_name if address_payload["isVenueAddress"] else "Librairie des mangas",
            },
        }

        with patch("pcapi.connectors.api_adresse.get_address", return_value=return_value):
            response = client.with_session_auth(user_email).patch(f"/offers/{offer_id}", json=data)

        updated_draft_offer = Offer.query.one()
        created_address = geography_models.Address.query.order_by(geography_models.Address.id.desc()).first()
        assert response.status_code == 200
        assert response.json["status"] == OfferStatus.DRAFT.value

        response = client.with_session_auth(user_email).get(f"/offers/{offer_id}")
        assert response.status_code == 200
        assert response.json["address"] == {
            **expected_data,
            "id": created_address.id,
            "id_oa": updated_draft_offer.offererAddressId,
            "label": venue.common_name if is_venue_address else "Librairie des mangas",
        }

    @override_features(WIP_SPLIT_OFFER=True)
    @override_features(WIP_ENABLE_OFFER_ADDRESS=True)
    @override_features(WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE=True)
    @pytest.mark.parametrize(
        "is_venue_address,address_payload,return_value,expected_data",
        [
            (
                False,
                {
                    "city": "LA ROCHE-SUR-YON",
                    "latitude": 46.66979,
                    "longitude": -1.42979,
                    "postalCode": "85000",
                    "street": "11 RUE GEORGES CLEMENCEAU",
                    "label": "Librairie des mangas",
                    "isManualEdition": False,
                    "isVenueAddress": False,
                },
                api_adresse.AddressInfo(
                    score=1,
                    city="LA ROCHE-SUR-YON",
                    latitude=46.66979,
                    longitude=-1.42979,
                    postcode="85000",
                    label="11 Rue Georges Clémenceau 85000 La Roche-sur-Yon",
                    street="11 Rue Georges Clémenceau",
                    citycode="85191",
                    id="85191_0940_00011",
                ),
                {
                    "city": "LA ROCHE-SUR-YON",
                    "departmentCode": "85",
                    "latitude": 46.66979,
                    "longitude": -1.42979,
                    "postalCode": "85000",
                    "street": "11 Rue Georges Clémenceau",
                    "label": "Librairie des mangas",
                    "inseeCode": "85191",
                    "banId": "85191_0940_00011",
                    "isLinkedToVenue": False,
                    "isManualEdition": False,
                },
            ),
            (
                True,
                {
                    "city": "Paris",
                    "latitude": 48.87004,
                    "longitude": 2.37850,
                    "postalCode": "75002",
                    "street": "1 boulevard Poissonnière",
                    "isManualEdition": False,
                    "isVenueAddress": True,
                },
                api_adresse.AddressInfo(
                    score=1,
                    city="Paris",
                    latitude=48.87004,
                    longitude=2.37850,
                    postcode="75002",
                    label="1 boulevard Poissonnière 75002 Paris",
                    street="1 boulevard Poissonnière",
                    citycode="75002",
                    id="75102_7560_00001",
                ),
                {
                    "city": "Paris",
                    "departmentCode": "75",
                    "latitude": 48.87004,
                    "longitude": 2.37850,
                    "postalCode": "75002",
                    "street": "1 boulevard Poissonnière",
                    "inseeCode": "75102",
                    "banId": "75102_7560_00001",
                    "isLinkedToVenue": True,
                    "isManualEdition": False,
                },
            ),
        ],
    )
    def test_first_step_funnel_creation_shouldnt_create_offer_offerer_address_ff_on(
        self, client, is_venue_address, address_payload, return_value, expected_data
    ):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        data = {
            "name": "New draft offer",
            "description": "This is a new draft offer",
            "subcategoryId": subcategories.FESTIVAL_SPECTACLE.id,
            "venueId": venue.id,
            "extraData": {
                "author": "",
                "ean": "",
                "gtl_id": "",
                "performer": "",
                "showSubType": 1202,
                "showType": 1200,
                "speaker": "",
                "stageDirector": "",
                "visa": "",
            },
        }
        user_email = user_offerer.user.email
        response = client.with_session_auth(user_email).post(f"/offers/draft", json=data)
        assert response.status_code == 201

        draft_offer = Offer.query.one()
        offer_id = draft_offer.id
        response = client.with_session_auth(user_email).get(f"/offers/{offer_id}")
        assert response.status_code == 200
        assert response.json["status"] == OfferStatus.DRAFT.value
        assert response.json["id"] == draft_offer.id
        assert not response.json.get("address")
        assert draft_offer.offererAddressId is None
        assert draft_offer.status is OfferStatus.DRAFT

        data = {
            "audioDisabilityCompliant": True,
            "isNational": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "withdrawalDelay": 172800,
            "withdrawalDetails": "",
            "visualDisabilityCompliant": False,
            "withdrawalType": "by_email",
            "bookingEmail": None,
            "shouldSendMail": True,
            "bookingContact": "test@mail.com",
            "address": {
                **address_payload,
                "label": venue.common_name if address_payload["isVenueAddress"] else "Librairie des mangas",
            },
        }
        with patch("pcapi.connectors.api_adresse.get_address", return_value=return_value):
            response = client.with_session_auth(user_email).patch(f"/offers/{offer_id}", json=data)
        updated_draft_offer = Offer.query.one()
        created_address = geography_models.Address.query.order_by(geography_models.Address.id.desc()).first()
        assert response.status_code == 200
        assert response.json["status"] == OfferStatus.DRAFT.value
        assert response.json["id"] == updated_draft_offer.id

        response = client.with_session_auth(user_email).get(f"/offers/{offer_id}")
        assert response.status_code == 200
        assert response.json["address"] == {
            **expected_data,
            "id": created_address.id,
            "id_oa": updated_draft_offer.offererAddressId,
            "label": venue.common_name if is_venue_address else "Librairie des mangas",
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
