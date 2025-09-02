import datetime
import json

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
from pcapi.core.videos import api as videos_api
from pcapi.models import db
from pcapi.utils.date import format_into_utc_date


def default_accessibility_fields():
    return {
        "audioDisabilityCompliant": True,
        "mentalDisabilityCompliant": True,
        "motorDisabilityCompliant": True,
        "visualDisabilityCompliant": True,
    }


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    # get user_session
    # get user
    # get pending bookings
    # check user_offerer exists
    # stocks
    # insert
    num_queries = 6

    endpoint = "/offers/draft/{offer_id}"

    def test_patch_draft_offer(self, app, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.DigitalOfferFactory(
            name="Name",
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venue=venue,
            description="description",
            url="http://example.com/offer",
        )

        video_id = "WtM4OW2qVjY"
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        data = {
            "name": "New name",
            "description": "New description",
            "subcategoryId": subcategories.ABO_PLATEFORME_VIDEO.id,
            "extraData": {"gtl_id": "07000000"},
            "videoUrl": video_url,
        }
        app.redis_client.set(
            f"{videos_api.YOUTUBE_INFO_CACHE_PREFIX}{video_id}",
            json.dumps(
                {
                    "title": "Title",
                    "thumbnail_url": "thumbnail url",
                    "duration": 100,
                }
            ),
        )
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )
        assert response.status_code == 200
        assert response.json["id"] == offer.id
        assert response.json["venue"]["id"] == offer.venue.id
        assert response.json["venue"]["street"]
        assert response.json["productId"] == None

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.subcategoryId == subcategories.ABO_PLATEFORME_VIDEO.id
        assert updated_offer.description == "New description"
        assert updated_offer.metaData.videoUrl == "https://www.youtube.com/watch?v=WtM4OW2qVjY"

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
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offerer_address = offerers_factories.OffererAddressFactory(offerer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            name="Name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            description="description",
            offererAddress=offerer_address,
        )

        data = {
            "name": "New name",
            "description": "New description",
            "extraData": {"author": "Nicolas Gogol"},
        }
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )
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
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )
        assert response.status_code == 200
        assert response.json["id"] == offer.id

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.extraData == {"stageDirector": "Greta Gerwig"}

    def test_patch_draft_offer_with_empty_extra_data(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
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
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )
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
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )
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
            **default_accessibility_fields(),
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
        assert not response.json.get("location")
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
            "location": {
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
        assert response.json["location"]["id"] == created_address.id
        assert response.json["location"]["label"] == venue.common_name if is_venue_address else "Librairie des mangas"

    def test_update_offer_accepts_accessibility_fields(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offerer_address = offerers_factories.OffererAddressFactory(offerer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            name="Name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            venue=venue,
            audioDisabilityCompliant=False,
            mentalDisabilityCompliant=False,
            motorDisabilityCompliant=False,
            visualDisabilityCompliant=False,
            offererAddress=offerer_address,
        )

        data = {
            "name": "New name",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "audioDisabilityCompliant": True,
        }
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert updated_offer.audioDisabilityCompliant is True
        assert updated_offer.mentalDisabilityCompliant is False
        assert updated_offer.motorDisabilityCompliant is False
        assert updated_offer.visualDisabilityCompliant is False

        assert not updated_offer.product

    def test_update_offer_accepts_video_url_for_product_offer(self, app, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(venue=venue, product=product)

        video_id = "l73rmrLTHQc"
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        app.redis_client.set(
            f"{videos_api.YOUTUBE_INFO_CACHE_PREFIX}{video_id}",
            json.dumps(
                {
                    "title": "Title",
                    "thumbnail_url": "thumbnail url",
                    "duration": 100,
                }
            ),
        )

        data = {"videoUrl": video_url}
        auth_client = client.with_session_auth("user@example.com")
        offer_id = offer.id

        response = auth_client.patch(self.endpoint.format(offer_id=offer_id), json=data)
        assert response.status_code == 200

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.metaData.videoUrl == "https://www.youtube.com/watch?v=l73rmrLTHQc"
        assert response.json["location"]["street"]

    def test_update_offer_accepts_video_url_for_synchronized_offer(self, app, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        provider = providers_factories.PublicApiProviderFactory()
        offer = offers_factories.OfferFactory(
            venue=venue,
            lastProviderId=provider.id,
            idAtProvider="id_at_provider",
        )

        video_id = "l73rmrLTHQc"
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        app.redis_client.set(
            f"{videos_api.YOUTUBE_INFO_CACHE_PREFIX}{video_id}",
            json.dumps(
                {
                    "title": "Title",
                    "thumbnail_url": "thumbnail url",
                    "duration": 100,
                }
            ),
        )

        data = {"videoUrl": video_url}
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 200

        updated_offer = db.session.get(Offer, offer.id)
        assert updated_offer.metaData.videoUrl == "https://www.youtube.com/watch?v=l73rmrLTHQc"

    def test_no_video_url_in_payload_should_not_remove_offer_video(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer_with_video = offers_factories.OfferFactory(venue=venue)

        offers_factories.OfferMetaDataFactory(
            offer=offer_with_video, videoUrl="https://www.youtube.com/watch?v=fXBIHHOXwAM"
        )

        data = {
            "name": "Aucun rapport avec la vidéo",
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/draft/{offer_with_video.id}", json=data)

        assert response.status_code == 200, response.json

        updated_offer = db.session.get(Offer, offer_with_video.id)
        assert updated_offer.metaData.videoUrl == "https://www.youtube.com/watch?v=fXBIHHOXwAM"

    def test_empty_video_url_in_payload_should_remove_offer_video(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer_with_video = offers_factories.OfferFactory(venue=venue)

        offers_factories.OfferMetaDataFactory(
            offer=offer_with_video,
            videoDuration=208,
            videoExternalId="fXBIHHOXwAM",
            videoThumbnailUrl="/mocked/thumbnail/fXBIHHOXwAM.jpg",
            videoTitle="Planète Boum Boum",
            videoUrl="https://www.youtube.com/watch?v=fXBIHHOXwAM",
        )

        data = {
            "videoUrl": "",
        }
        response = client.with_session_auth("user@example.com").patch(f"/offers/draft/{offer_with_video.id}", json=data)

        assert response.status_code == 200, response.json
        updated_offer = db.session.get(Offer, offer_with_video.id)
        assert not updated_offer.metaData.videoDuration
        assert not updated_offer.metaData.videoExternalId
        assert not updated_offer.metaData.videoThumbnailUrl
        assert not updated_offer.metaData.videoTitle
        assert not updated_offer.metaData.videoUrl


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    endpoint = "/offers/draft/{offer_id}"

    @pytest.mark.parametrize(
        "patch_body,expected_response_json",
        [
            (
                {
                    "dateCreated": format_into_utc_date(datetime.datetime(2019, 1, 1)),
                    "dateModifiedAtLastProvider": format_into_utc_date(datetime.datetime(2019, 1, 1)),
                    "id": 1,
                    "idAtProviders": 1,
                    "lastProviderId": 1,
                    "thumbCount": 2,
                    "subcategoryId": subcategories.LIVRE_PAPIER.id,
                    "product_id": 42,
                },
                {
                    "dateCreated": ["Vous ne pouvez pas changer cette information"],
                    "dateModifiedAtLastProvider": ["Vous ne pouvez pas changer cette information"],
                    "id": ["Vous ne pouvez pas changer cette information"],
                    "idAtProviders": ["Vous ne pouvez pas changer cette information"],
                    "lastProviderId": ["Vous ne pouvez pas changer cette information"],
                    "thumbCount": ["Vous ne pouvez pas changer cette information"],
                    "product_id": ["Vous ne pouvez pas changer cette information"],
                },
            ),
            (
                {"description": "d" * 10_001},
                {"description": ["ensure this value has at most 10000 characters"]},
            ),
            (
                {"name": "Le Visible et l'invisible - Suivi de notes de travail - 9782070286256"},
                {"name": ["Le titre d'une offre ne peut contenir l'EAN"]},
            ),
            (
                {"videoUrl": "coucou.com"},
                {"videoUrl": ['L\'URL doit commencer par "http://" ou "https://"']},
            ),
            (
                {"videoUrl": "http://coucou.com"},
                {
                    "videoUrl": [
                        "Veuillez renseigner une URL provenant de la plateforme Youtube. Les shorts et les chaînes ne sont pas acceptées."
                    ]
                },
            ),
            (
                {"durationMinutes": 1440},
                {
                    "durationMinutes": [
                        "La durée doit être inférieure à 24 heures. Pour les événements durant 24 heures ou plus (par exemple, un pass festival de 3 jours), veuillez laisser ce champ vide."
                    ]
                },
            ),
        ],
    )
    def when_sending_incorrect_patch_body(self, patch_body, expected_response_json, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.CARTE_MUSEE.id, name="New name", url="http://example.com/offer"
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").patch(f"offers/draft/{offer.id}", json=patch_body)

        assert response.status_code == 400
        assert response.json == expected_response_json

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

    def test_fail_when_body_has_null_accessibility_fields(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(
            venue=venue,
        )

        data = {
            "audioDisabilityCompliant": None,
        }
        response = client.with_session_auth("user@example.com").patch(
            self.endpoint.format(offer_id=offer.id), json=data
        )

        assert response.status_code == 400
        assert response.json["global"][0] == "L’accessibilité de l’offre doit être définie"

    @pytest.mark.settings(YOUTUBE_API_BACKEND="pcapi.connectors.youtube.YoutubeNotFoundBackend")
    def test_fetch_metadata_not_found_should_fail(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)

        data = {"videoUrl": "https://www.youtube.com/watch?v=l73rmrLTHQc"}
        auth_client = client.with_session_auth("user@example.com")
        response = auth_client.patch(f"/offers/draft/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["videoUrl"] == ["URL Youtube non trouvée, vérifiez si votre vidéo n’est pas en privé."]


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    endpoint = "/offers/draft/{offer_id}"

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
        response = client.with_session_auth(email).patch(self.endpoint.format(offer_id=offer.id), json=data)

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
