from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.categories import subcategories
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferStatus
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.models import db
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

        publication_dt = datetime.now(tz=timezone.utc) + timedelta(days=10)
        booking_allowed_dt = datetime.now(tz=timezone.utc) + timedelta(days=30)

        data = {
            "name": "New name",
            "description": "New description",
            "subcategoryId": subcategories.ABO_PLATEFORME_VIDEO.id,
            "extraData": {"gtl_id": "07000000"},
            "publicationDatetime": publication_dt.isoformat(),
            "bookingAllowedDatetime": booking_allowed_dt.isoformat(),
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/draft/{offer.id}", json=data)
        assert response.status_code == 200
        assert response.json["id"] == offer.id
        assert response.json["venue"]["id"] == offer.venue.id
        assert response.json["productId"] == None

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.subcategoryId == subcategories.ABO_PLATEFORME_VIDEO.id
        assert updated_offer.description == "New description"
        assert updated_offer.publicationDatetime == publication_dt.replace(tzinfo=None)
        assert updated_offer.bookingAllowedDatetime == booking_allowed_dt.replace(tzinfo=None)
        assert not updated_offer.product

    def test_patch_draft_offer_without_product_with_new_ean_should_succeed(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.DraftOfferFactory(
            name="Name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            description="description",
            ean="1111111111111",
        )

        data = {"extraData": {"ean": "2222222222222"}}
        response = client.with_session_auth("user@example.com").patch(f"offers/draft/{offer.id}", json=data)

        assert response.status_code == 200
        assert response.json["id"] == offer.id

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.ean == "2222222222222"
        assert updated_offer.extraData == {}

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

        updated_offer = db.session.get(Offer, offer.id)
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

        updated_offer = db.session.get(Offer, offer.id)
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

        updated_offer = db.session.get(Offer, offer.id)
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

        updated_offer = db.session.get(Offer, offer.id)
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

    @pytest.mark.parametrize(
        "is_venue_address,address_payload,",
        [
            (
                False,
                {
                    "banId": "85191_0940_00011",
                    "city": "LA ROCHE-SUR-YON",
                    "cityCode": "85191",
                    "latitude": 46.66979,
                    "longitude": -1.42979,
                    "postalCode": "85000",
                    "street": "11 RUE GEORGES CLEMENCEAU",
                    "label": "Librairie des mangas",
                    "isManualEdition": False,
                    "isVenueAddress": False,
                },
            ),
            (
                True,
                {
                    "banId": "75102_7560_00001",
                    "city": "Paris",
                    "cityCode": "75002",
                    "latitude": 48.87004,
                    "longitude": 2.37850,
                    "postalCode": "75002",
                    "street": "1 boulevard Poissonnière",
                    "isManualEdition": False,
                    "isVenueAddress": True,
                },
            ),
        ],
    )
    def test_first_step_funnel_creation_shouldnt_create_offer_offerer_address(
        self,
        client,
        is_venue_address,
        address_payload,
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
        response = client.with_session_auth(user_email).post("/offers/draft", json=data)
        assert response.status_code == 201

        draft_offer = db.session.query(Offer).one()
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

        response = client.with_session_auth(user_email).patch(f"/offers/{offer_id}", json=data)

        updated_draft_offer = db.session.query(Offer).one()
        created_address = (
            db.session.query(geography_models.Address).order_by(geography_models.Address.id.desc()).first()
        )
        assert response.status_code == 200
        assert response.json["status"] == OfferStatus.DRAFT.value
        assert response.json["id"] == updated_draft_offer.id

        response = client.with_session_auth(user_email).get(f"/offers/{offer_id}")
        assert response.status_code == 200
        assert response.json["address"]["id"] == created_address.id
        assert response.json["address"]["id_oa"] == updated_draft_offer.offererAddressId
        assert response.json["address"]["label"] == venue.common_name if is_venue_address else "Librairie des mangas"


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

    def when_trying_to_set_a_description_way_to_long(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CARTE_MUSEE.id, name="New name", url="http://example.com/offer"
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"description": "d" * 10_001}
        response = client.with_session_auth("user@example.com").patch(f"offers/draft/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["description"] == ["ensure this value has at most 10000 characters"]

    def when_trying_to_set_offer_name_with_ean(self, client):
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
            "name": "Le Visible et l'invisible - Suivi de notes de travail - 9782070286256",
        }
        response = client.with_session_auth("user@example.com").patch(f"offers/draft/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["name"] == ["Le titre d'une offre ne peut contenir l'EAN"]

    def when_trying_to_patch_offer_with_product_with_new_ean(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(
            managingOfferer=user_offerer.offerer, venueTypeCode=VenueTypeCode.RECORD_STORE
        )
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean="1111111111111",
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
        assert response.json["global"] == ["Les extraData des offres avec produit ne sont pas modifiables"]

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
        assert db.session.get(Offer, offer.id).name == "Old name"


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_returns_404_if_offer_does_not_exist(self, client):
        email = "user@example.com"
        users_factories.UserFactory(email=email)

        response = client.with_session_auth(email).patch("/offers/draft/12345", json={})
        assert response.status_code == 404


USER_EMAIL = "user@example.com"


@pytest.fixture(name="offer")
def offer_fixture():
    user_offerer = offerers_factories.UserOffererFactory(user__email=USER_EMAIL)
    venue = offerers_factories.VirtualVenueFactory(managingOfferer=user_offerer.offerer)
    return offers_factories.OfferFactory(venue=venue)


@pytest.fixture(name="offer")
def auth_client_fixture(client, offer):
    # offer fixture is needed because it sets the user and its offerer which
    # are needed before authentication.
    return client.with_session_auth(USER_EMAIL)


def dt_with_delta(days, tz=timezone.utc):
    return datetime.now(tz=tz) + timedelta(days=days)


@pytest.mark.usefixtures("db_session")
class PatchDraftOfferFuturePublicationErrorsTest:
    def test_booking_allowed_dt_before_publication_dt_is_not_allowed(self, auth_client, offer):
        publication_dt = dt_with_delta(days=10)
        booking_allowed_dt = dt_with_delta(days=5)

        response = self.send_request(auth_client, offer.id, publication_dt, booking_allowed_dt)
        assert response.status_code == 400
        assert response.json == {"bookingAllowedDatetime": ["must be after `publicationDatetime`"]}

    def test_publication_dt_must_be_timezone_aware(self, auth_client, offer):
        publication_dt = dt_with_delta(days=10, tz=None)
        booking_allowed_dt = dt_with_delta(days=30)

        response = self.send_request(auth_client, offer.id, publication_dt, booking_allowed_dt)
        assert response.status_code == 400
        assert response.json == {"publicationDatetime": ["The datetime must be timezone-aware."]}

    def test_booking_allowed_dt_must_be_timezone_aware(self, auth_client, offer):
        publication_dt = dt_with_delta(days=10)
        booking_allowed_dt = dt_with_delta(days=30, tz=None)

        response = self.send_request(auth_client, offer.id, publication_dt, booking_allowed_dt)
        assert response.status_code == 400
        assert response.json == {"bookingAllowedDatetime": ["The datetime must be timezone-aware."]}

    def test_publication_dt_cannot_be_in_the_past(self, auth_client, offer):
        publication_dt = dt_with_delta(days=-100)
        booking_allowed_dt = dt_with_delta(days=30)

        response = self.send_request(auth_client, offer.id, publication_dt, booking_allowed_dt)
        assert response.status_code == 400
        assert response.json == {"publicationDatetime": ["The datetime must be in the future."]}

    def test_booking_allowed_dt_cannot_be_in_the_past(self, auth_client, offer):
        publication_dt = dt_with_delta(days=10)
        booking_allowed_dt = dt_with_delta(days=-30)

        response = self.send_request(auth_client, offer.id, publication_dt, booking_allowed_dt)
        assert response.status_code == 400
        assert response.json == {"bookingAllowedDatetime": ["The datetime must be in the future."]}

    def test_either_both_are_set_or_both_are_null(self, auth_client, offer):
        publication_dt = dt_with_delta(days=10)
        booking_allowed_dt = dt_with_delta(days=30)

        response = self.send_request(auth_client, offer.id, publication_dt, booking_allowed_dt)
        assert response.status_code == 200

        response = self.send_request(auth_client, offer.id, None, None)
        assert response.status_code == 200

        response = self.send_request(auth_client, offer.id, publication_dt, None)
        assert response.status_code == 400
        assert response.json == {
            "__root__": [
                "either both `publicationDatetime` and `bookingAllowedDatetime` are set or both are null",
            ]
        }

        response = self.send_request(auth_client, offer.id, None, booking_allowed_dt)
        assert response.status_code == 400
        assert response.json == {
            "__root__": [
                "either both `publicationDatetime` and `bookingAllowedDatetime` are set or both are null",
            ]
        }

    def send_request(self, client, offer_id, publication_dt, booking_allowed_dt):
        data = {
            "publicationDatetime": publication_dt.isoformat() if publication_dt else None,
            "bookingAllowedDatetime": booking_allowed_dt.isoformat() if booking_allowed_dt else None,
        }

        return client.patch(f"offers/draft/{offer_id}", json=data)
