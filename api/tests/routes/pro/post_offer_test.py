import contextlib
from decimal import Decimal

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus


pytestmark = pytest.mark.usefixtures("db_session")


def offer_minimal_shared_data(subcategory_id, venue):
    return {
        "name": f"some {subcategory_id} offer",
        "subcategoryId": subcategory_id,
        "venueId": venue.id,
        "audioDisabilityCompliant": False,
        "mentalDisabilityCompliant": False,
        "motorDisabilityCompliant": False,
        "visualDisabilityCompliant": False,
    }


def offer_optional_shared_data(**kwargs):
    return {
        "bookingContact": "booking.contact@test.fr",
        "bookingEmail": "booking.email@test.fr",
        "description": "some description",
        **kwargs,
    }


@pytest.fixture(name="venue")
def venue_fixture():
    return offerers_factories.VenueFactory()


@pytest.fixture(name="user")
def user_fixture(venue):
    return offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com").user


@pytest.fixture(name="auth_client")
def auth_client_fixture(client, user):
    return client.with_session_auth(user.email)


THINGS_WITH_EAN = {
    subcategories.LIVRE_PAPIER.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
}


THINGS_RANDOM = {
    subcategories.ABO_BIBLIOTHEQUE.id,
    subcategories.ABO_CONCERT.id,
    subcategories.ABO_MEDIATHEQUE.id,
    subcategories.ABO_PRATIQUE_ART.id,
    subcategories.ACHAT_INSTRUMENT.id,
    subcategories.CARTE_CINE_ILLIMITE.id,
    subcategories.CARTE_CINE_MULTISEANCES.id,
    subcategories.CARTE_JEUNES.id,
    subcategories.CARTE_MUSEE.id,
    subcategories.ESCAPE_GAME.id,
    subcategories.LIVRE_AUDIO_PHYSIQUE.id,
    subcategories.LOCATION_INSTRUMENT.id,
    subcategories.MATERIEL_ART_CREATIF.id,
    subcategories.PARTITION.id,
    subcategories.SUPPORT_PHYSIQUE_FILM.id,
}


THINGS = THINGS_WITH_EAN | THINGS_RANDOM


DIGITAL = {
    subcategories.TELECHARGEMENT_MUSIQUE.id,
    subcategories.LIVRE_NUMERIQUE.id,
    subcategories.PLATEFORME_PRATIQUE_ARTISTIQUE.id,
    subcategories.AUTRE_SUPPORT_NUMERIQUE.id,
    subcategories.MUSEE_VENTE_DISTANCE.id,
    subcategories.VISITE_VIRTUELLE.id,
    subcategories.PRATIQUE_ART_VENTE_DISTANCE.id,
    subcategories.ABO_PLATEFORME_VIDEO.id,
    subcategories.ABO_PRESSE_EN_LIGNE.id,
    subcategories.APP_CULTURELLE.id,
    subcategories.JEU_EN_LIGNE.id,
    subcategories.CINE_VENTE_DISTANCE.id,
    subcategories.ABO_LIVRE_NUMERIQUE.id,
    subcategories.ABO_JEU_VIDEO.id,
    subcategories.PODCAST.id,
    subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
    subcategories.ABO_PLATEFORME_MUSIQUE.id,
    subcategories.VOD.id,
}


DIGITAL_EVENT = {
    subcategories.SPECTACLE_ENREGISTRE.id,
    subcategories.SPECTACLE_VENTE_DISTANCE.id,
}


CANNOT_BE_CREATED = {
    subcategories.ACTIVATION_EVENT.id,
    subcategories.CAPTATION_MUSIQUE.id,
    subcategories.OEUVRE_ART.id,
    subcategories.BON_ACHAT_INSTRUMENT.id,
    subcategories.ACTIVATION_THING.id,
    subcategories.ABO_LUDOTHEQUE.id,
    subcategories.JEU_SUPPORT_PHYSIQUE.id,
    subcategories.DECOUVERTE_METIERS.id,
}


ACTIVITY_SUBSCRIPTION = {
    subcategories.ABO_SPECTACLE.id,
}


ACTIVITY_ONLINE = {
    subcategories.LIVESTREAM_EVENEMENT.id,
    subcategories.LIVESTREAM_MUSIQUE.id,
    subcategories.RENCONTRE_EN_LIGNE.id,
    subcategories.LIVESTREAM_PRATIQUE_ARTISTIQUE.id,
}


ACTIVITY_WITHDRAWABLE = {
    subcategories.SPECTACLE_REPRESENTATION.id,
    subcategories.FESTIVAL_ART_VISUEL.id,
    subcategories.FESTIVAL_SPECTACLE.id,
    subcategories.FESTIVAL_MUSIQUE.id,
    subcategories.EVENEMENT_MUSIQUE.id,
    subcategories.CONCERT.id,
}


ACTIVITY_RANDOM = {
    subcategories.ATELIER_PRATIQUE_ART.id,
    subcategories.CINE_PLEIN_AIR.id,
    subcategories.CONCOURS.id,
    subcategories.CONFERENCE.id,
    subcategories.EVENEMENT_CINE.id,
    subcategories.EVENEMENT_JEU.id,
    subcategories.EVENEMENT_PATRIMOINE.id,
    subcategories.FESTIVAL_CINE.id,
    subcategories.FESTIVAL_LIVRE.id,
    subcategories.RENCONTRE.id,
    subcategories.RENCONTRE_JEU.id,
    subcategories.SALON.id,
    subcategories.SEANCE_CINE.id,
    subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
    subcategories.VISITE.id,
    subcategories.VISITE_GUIDEE.id,
}


def shared_response_json_checks(offer, response_json):
    assert response_json["id"] == offer.id
    assert response_json["name"] == offer.name
    assert not response_json["publicationDate"]
    assert not response_json["publicationDatetime"]
    assert not response_json["bookingAllowedDatetime"]


def shared_offer_checks(offer, payload):
    assert offer.name == payload["name"]
    assert offer.venueId == payload["venueId"]
    assert offer.subcategoryId == payload["subcategoryId"]
    assert not offer.publicationDate
    assert not offer.publicationDatetime
    assert not offer.bookingAllowedDatetime
    assert not offer.isActive


# shared
# booking_email: EmailStr | None
# description: str | None
# extra_data: dict[str, typing.Any] | None
# is_national: bool | None
# product_id: int | None
# video_url: HttpUrl | None = None
#
# -----
#
# things
#
# -----
#
# digital
#
# -----
#
# activity
# booking_contact: EmailStr | None
# address: offerers_schemas.AddressBodyModel | None
# duration_minutes: int | None
# external_ticket_office_url: HttpUrl | None
# is_duo: bool | None
# withdrawal_delay: int | None
# withdrawal_details: str | None
# withdrawal_type: offers_models.WithdrawalTypeEnum | None
#
# -----
#
# digital & activity
# url: HttpUrl | None
#
# -----
#


@contextlib.contextmanager
def assert_delta(model, delta):
    before_count = db.session.query(model).count()

    yield

    after_count = db.session.query(model).count()
    assert after_count == before_count + delta


@contextlib.contextmanager
def assert_no_object_created(model):
    before_count = db.session.query(model).count()

    yield

    after_count = db.session.query(model).count()
    assert after_count == before_count


def default_address_payload():
    return {"city": "Paris", "latitude": 2.0, "longitude": 48.0, "postalCode": 75002, "street": "1 rue des rues"}


class CreateOfferBase:
    endpoint = "/v2/offers"

    success_num_queries = 1  # fetch user session
    success_num_queries += 1  # fetch user
    success_num_queries += 1  # fetch venue
    success_num_queries += 1  # user offerer check
    success_num_queries += 1  # fetch product
    success_num_queries += 1  # fetch FF
    success_num_queries += 1  # create offer
    success_num_queries += 1  # fetch mediation
    success_num_queries += 1  # fetch stocks
    success_num_queries += 1  # fetch price categories
    success_num_queries += 1  # fetch offerer address
    success_num_queries += 1  # fetch offer meta data
    success_num_queries += 1  # fetch user
    success_num_queries += 1  # fetch offerer
    success_num_queries += 1  # check national program (?)
    success_num_queries += 1  # check venue has collective offers (?)
    success_num_queries += 1  # check offer regarding offer status (?)
    success_num_queries += 1  # check offer's venue has at least one cancelled booking (?)

    def send_request(self, client, payload):
        with assert_delta(Offer, 1):
            with assert_num_queries(self.success_num_queries):
                response = client.post(self.endpoint, json=payload)
                assert response.status_code == 201, response.json
                return response


class CreateThingTest(CreateOfferBase):
    @pytest.mark.parametrize("subcategory_id", THINGS)
    def test_create_offer_with_minimal_payload_is_succesful(self, auth_client, venue, subcategory_id):
        payload = offer_minimal_shared_data(subcategory_id, venue)
        response = self.send_request(auth_client, payload)

        offer = db.session.query(Offer).one()
        shared_response_json_checks(offer, response.json)
        shared_offer_checks(offer, payload)

        assert not offer.isDigital
        assert not offer.isEvent

    # TODO(jbaudet): most of `THINGS` subcategories should not accept any EAN
    # but for now... it is valid.
    @pytest.mark.parametrize("subcategory_id", THINGS)
    def test_create_offer_with_ean_and_no_product_is_ok(self, auth_client, venue, subcategory_id):
        payload = {
            **offer_minimal_shared_data(subcategory_id, venue),
            "bookingEmail": "booking.email@test.com",
            "description": "some description",
            "extraData": {"ean": "0000000000001"},
        }
        response = auth_client.post(self.endpoint, json=payload)
        assert response.status_code == 201

        offer = db.session.query(Offer).one()

        shared_response_json_checks(offer, response.json)
        shared_offer_checks(offer, payload)

        assert not offer.isDigital
        assert not offer.isEvent
        assert offer.ean == "0000000000001"
        assert offer.description == payload["description"]
        assert not offer.productId

    @pytest.mark.parametrize("subcategory_id", THINGS_WITH_EAN)
    def test_create_offer_with_product_is_ok(self, auth_client, venue, subcategory_id):
        product = offers_factories.ProductFactory(subcategoryId=subcategory_id)
        payload = {
            **offer_minimal_shared_data(subcategory_id, venue),
            "bookingEmail": "booking.email@test.com",
            "description": "some description",
            "extraData": {"ean": product.ean},
            "productId": product.id,
        }
        response = auth_client.post(self.endpoint, json=payload)
        assert response.status_code == 201

        offer = db.session.query(Offer).one()

        shared_response_json_checks(offer, response.json)
        shared_offer_checks(offer, payload)

        assert not offer.isDigital
        assert not offer.isEvent
        assert offer.ean == product.ean
        assert offer.description == product.description
        assert offer.productId == product.id

    @pytest.mark.parametrize(
        "extra",
        [
            # TODO(jbaudet): fill this list after offer creation has been
            # cleaned up. For example an `ABO_BIBLIOTHEQUE` should not accept
            # any duration
            {"url": "https://example.thing@test.com"},
            {"withdrawalType": "in_app"},
        ],
    )
    def test_create_offer_with_non_thing_field_is_not_ok(self, auth_client, venue, extra):
        subcategory_id = sorted(THINGS)[0]
        payload = {**offer_minimal_shared_data(subcategory_id, venue), **extra}
        response = auth_client.post(self.endpoint, json=payload)

        with assert_no_object_created(Offer):
            assert response.status_code == 400


@pytest.mark.parametrize("subcategory_id", DIGITAL)
class CreateDigitalOfferTest(CreateOfferBase):
    endpoint = "/v2/offers"

    def test_create_offer_with_minimal_payload_is_succesful(self, auth_client, venue, subcategory_id):
        default_url = "https://default.url@test.com"
        payload = {**offer_minimal_shared_data(subcategory_id, venue), "url": default_url}

        response = self.send_request(auth_client, payload)
        assert response.status_code == 201

        offer = db.session.query(Offer).one()

        shared_response_json_checks(offer, response.json)
        shared_offer_checks(offer, payload)

        assert offer.isDigital
        assert not offer.isEvent


@pytest.mark.parametrize("subcategory_id", DIGITAL_EVENT)
class CreateDigitalEventTest(CreateOfferBase):
    endpoint = "/v2/offers"

    def test_create_offer_with_minimal_payload_is_succesful(self, auth_client, venue, subcategory_id):
        activity_url = "https://activity.online@test.com"
        payload = {
            **offer_minimal_shared_data(subcategory_id, venue),
            "extraData": {"showType": 100, "showSubType": 101},
            "url": activity_url,
        }

        response = self.send_request(auth_client, payload)
        assert response.status_code == 201

        offer = db.session.query(Offer).one()

        shared_response_json_checks(offer, response.json)
        shared_offer_checks(offer, payload)

        assert offer.isDigital
        assert not offer.isEvent


@pytest.mark.parametrize("subcategory_id", ACTIVITY_SUBSCRIPTION)
class CreateActivitySubscriptionTest(CreateOfferBase):
    endpoint = "/v2/offers"

    def test_create_offer_with_minimal_payload_is_succesful(self, auth_client, venue, subcategory_id):
        payload = {
            **offer_minimal_shared_data(subcategory_id, venue),
            "extraData": {"showType": 100, "showSubType": 101},
        }

        response = self.send_request(auth_client, payload)
        assert response.status_code == 201

        offer = db.session.query(Offer).one()

        shared_response_json_checks(offer, response.json)
        shared_offer_checks(offer, payload)

        assert not offer.isDigital
        assert not offer.isEvent


@pytest.mark.parametrize("subcategory_id", ACTIVITY_ONLINE)
class CreateActivityOnlineTest(CreateOfferBase):
    endpoint = "/v2/offers"

    def test_create_offer_with_minimal_payload_is_succesful(self, auth_client, venue, subcategory_id):
        activity_url = "https://activity.online@test.com"
        payload = {
            **offer_minimal_shared_data(subcategory_id, venue),
            "extraData": {"showType": 100, "showSubType": 101},
            "url": activity_url,
        }

        response = self.send_request(auth_client, payload)
        assert response.status_code == 201

        offer = db.session.query(Offer).one()

        shared_response_json_checks(offer, response.json)
        shared_offer_checks(offer, payload)

        assert offer.isDigital
        assert offer.isEvent


@pytest.mark.parametrize("subcategory_id", ACTIVITY_WITHDRAWABLE)
class CreateActivityWithdrawableTest(CreateOfferBase):
    endpoint = "/v2/offers"

    @pytest.mark.parametrize("withdrawal_type", ["by_email", "on_site", "no_ticket"])
    def test_create_offer_with_minimal_payload_is_succesful(self, auth_client, venue, subcategory_id, withdrawal_type):
        payload = {
            **offer_minimal_shared_data(subcategory_id, venue),
            "extraData": {"showType": 100, "showSubType": 101},
            "bookingContact": "booking.contact@test.com",
            "withdrawalType": withdrawal_type,
            "withdrawalDelay": 10 if withdrawal_type != "no_ticket" else None,
        }

        response = self.send_request(auth_client, payload)
        assert response.status_code == 201

        offer = db.session.query(Offer).one()

        shared_response_json_checks(offer, response.json)
        shared_offer_checks(offer, payload)

        assert not offer.isDigital
        assert offer.isEvent

    def test_cannot_manually_create_offer_with_in_app_withdrawal(self, auth_client, venue, subcategory_id):
        payload = {
            **offer_minimal_shared_data(subcategory_id, venue),
            "extraData": {"showType": 100, "showSubType": 101},
            "bookingContact": "booking.contact@test.com",
            "withdrawalType": "in_app",
        }

        response = auth_client.post(self.endpoint, json=payload)
        assert response.status_code == 400
        assert response.json == {"withdrawalType": ["Withdrawal type cannot be in_app for manually created offers"]}


@pytest.mark.parametrize("subcategory_id", ACTIVITY_RANDOM)
class CreateActivityRandomTest(CreateOfferBase):
    endpoint = "/v2/offers"

    def test_create_offer_with_minimal_payload_is_succesful(self, auth_client, venue, subcategory_id):
        payload = {
            **offer_minimal_shared_data(subcategory_id, venue),
            "extraData": {"showType": 100, "showSubType": 101},
        }

        response = self.send_request(auth_client, payload)
        assert response.status_code == 201

        offer = db.session.query(Offer).one()

        shared_response_json_checks(offer, response.json)
        shared_offer_checks(offer, payload)

        assert not offer.isDigital
        assert offer.isEvent


@pytest.mark.parametrize("subcategory_id", CANNOT_BE_CREATED)
class CannotCreateOfferTest:
    endpoint = "/v2/offers"

    def test_create_offer_with_minimal_payload_is_not_autorized(self, auth_client, venue, subcategory_id):
        payload = {**offer_minimal_shared_data(subcategory_id, venue)}
        response = auth_client.post(self.endpoint, json=payload)

        assert response.status_code == 400
        assert response.json == {
            "subcategory": ["Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"]
        }


class Returns200Test:
    def test_created_offer_should_be_inactive(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "Celeste",
            "subcategoryId": subcategories.ABO_BIBLIOTHEQUE.id,
            "mentalDisabilityCompliant": True,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)
        offer_id = response.json["id"]
        offer = db.session.get(Offer, offer_id)
        response_dict = response.json
        assert offer.isActive is False
        assert response_dict["venue"]["id"] == offer.venue.id
        assert response.json["venue"]["street"] == offer.venue.offererAddress.address.street
        assert response_dict["name"] == "Celeste"
        assert response_dict["id"] == offer.id
        assert not offer.product

    def test_create_event_offer(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "bookingContact": "offer@example.com",
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
            "extraData": {"toto": "text", "showType": 200, "showSubType": 201},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = response.json["id"]
        offer = db.session.get(Offer, offer_id)
        assert offer.bookingContact == "offer@example.com"
        assert offer.bookingEmail == "offer@example.com"
        assert offer.publicationDate is None
        assert offer.subcategoryId == subcategories.SPECTACLE_REPRESENTATION.id
        assert offer.extraData == {"showType": 200, "showSubType": 201}
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.venue == venue
        assert offer.motorDisabilityCompliant is False
        assert offer.visualDisabilityCompliant is False
        assert offer.audioDisabilityCompliant is False
        assert offer.mentalDisabilityCompliant is True
        assert offer.validation == OfferValidationStatus.DRAFT
        assert offer.isActive is False
        assert offer.offererAddress.id == venue.offererAddressId
        assert offer.offererAddress == venue.offererAddress

    @pytest.mark.parametrize("oa_label", [None, "some place"])
    def test_create_event_offer_with_existing_offerer_address(self, oa_label, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        # Match the BAN API response
        offerer_address = offerers_factories.OffererAddressFactory(
            offerer=offerer,
            address__banId="75101_9575_00003",
            address__city="Paris",
            address__departmentCode="75",
            address__inseeCode="75056",
            address__isManualEdition=False,
            address__latitude=Decimal("48.87171"),
            address__longitude=Decimal("2.308289"),
            address__postalCode="75001",
            address__street="3 Rue de Valois",
            address__timezone="Europe/Paris",
        )
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "bookingContact": "offer@example.com",
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
            "extraData": {"toto": "text", "showType": 200, "showSubType": 201},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "address": {
                "city": offerer_address.address.city,
                "inseeCode": offerer_address.address.inseeCode,
                "label": oa_label,
                "latitude": offerer_address.address.latitude,
                "longitude": offerer_address.address.longitude,
                "postalCode": offerer_address.address.postalCode,
                "street": offerer_address.address.street,
                "banId": offerer_address.address.banId,
            },
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = response.json["id"]
        offer = db.session.get(Offer, offer_id)
        assert offer.offererAddress.address == offerer_address.address
        assert offer.offererAddress.label == oa_label
        assert not offer.offererAddress.address.isManualEdition

    @pytest.mark.parametrize("oa_label", [None, "some place"])
    def test_create_event_offer_with_non_existing_offerer_address(self, oa_label, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerer_address = offerers_factories.OffererAddressFactory(offerer=offerer)
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "bookingContact": "offer@example.com",
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
            "extraData": {"toto": "text", "showType": 200, "showSubType": 201},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "address": {
                "city": "Paris",
                "label": oa_label,
                "latitude": "48.87171",
                "longitude": "2.308289",
                "postalCode": "75001",
                "street": "3 Rue de Valois",
            },
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = response.json["id"]
        offer = db.session.get(Offer, offer_id)
        assert offer.offererAddress.address != offerer_address.address
        assert offer.offererAddress.label == oa_label
        assert not offer.offererAddress.address.isManualEdition

    @pytest.mark.parametrize("oa_label", [None, "some place"])
    def test_create_event_offer_with_manual_offerer_address(self, oa_label, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "bookingContact": "offer@example.com",
            "bookingEmail": "offer@example.com",
            "durationMinutes": 60,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.SPECTACLE_REPRESENTATION.id,
            "withdrawalType": "no_ticket",
            "extraData": {"toto": "text", "showType": 200, "showSubType": 201},
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "address": {
                "city": "Paris",
                "label": oa_label,
                "latitude": "48.87171",
                "longitude": "2.308289",
                "postalCode": "75001",
                "street": "3 Rue de Valois",
                "isManualEdition": True,
            },
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = response.json["id"]
        offer = db.session.get(Offer, offer_id)
        assert offer.offererAddress.address.isManualEdition
        assert offer.offererAddress.label == oa_label
        assert not offer.offererAddress.address.banId
        assert offer.offererAddress.address.isManualEdition is True

    def when_creating_new_thing_offer(self, client):
        # Given
        venue = offerers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "bookingEmail": "offer@example.com",
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "url": "http://example.com/offer",
            "externalTicketOfficeUrl": "http://example.net",
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 201
        offer_id = response.json["id"]
        offer = db.session.get(Offer, offer_id)
        assert offer.bookingEmail == "offer@example.com"
        assert offer.subcategoryId == subcategories.JEU_EN_LIGNE.id
        assert offer.venue == venue
        assert offer.externalTicketOfficeUrl == "http://example.net"
        assert offer.url == "http://example.com/offer"
        assert offer.isDigital
        assert offer.isNational
        assert offer.motorDisabilityCompliant is False
        assert offer.visualDisabilityCompliant is False
        assert offer.audioDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is False
        assert offer.offererAddress is None

    def test_create_offer_with_ean(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        ean = "1234567890112"
        data = {
            "venueId": venue.id,
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.LIVRE_PAPIER.id,
            "extraData": {
                "ean": ean,
            },
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        assert response.status_code == 201
        assert response.json["extraData"]["ean"] == ean
        assert "ean" not in response.json

        offer_id = response.json["id"]
        offer = db.session.get(Offer, offer_id)
        assert offer.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert offer.venue == venue
        assert offer.ean == "1234567890112"
        assert "ean" not in offer.extraData

    def test_withdrawable_event_offer_can_have_no_ticket_to_withdraw(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {
            "venueId": venue.id,
            "name": "La pièce de théâtre",
            "subcategoryId": subcategories.CONCERT.id,
            "bookingContact": "booking@conta.ct",
            "withdrawalDetails": "Veuillez récuperer vos billets à l'accueil :)",
            "withdrawalType": "no_ticket",
            "extraData": {"gtl_id": "07000000"},
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        offer_id = response.json["id"]
        offer = db.session.get(Offer, offer_id)
        assert offer.withdrawalDetails == "Veuillez récuperer vos billets à l'accueil :)"
        assert offer.withdrawalType == WithdrawalTypeEnum.NO_TICKET


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    @staticmethod
    def _get_default_json(venue_id: int, subcategory_id: str) -> dict:
        return {
            "venueId": venue_id,
            "name": "Mon offre",
            "subcategoryId": subcategory_id,
            "mentalDisabilityCompliant": False,
            "audioDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
        }

    def test_fail_if_venue_is_not_found(self, client):
        # Given
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {
            "venueId": 1,
            "bookingEmail": "offer@example.com",
            "name": "Les lièvres pas malins",
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "url": "http://example.com/offer",
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "input_json,expected_json",
        [
            ({"name": "too long" * 30}, {"name": ["Le titre de l’offre doit faire au maximum 90 caractères."]}),
            (
                {
                    "name": "Le Visible et l'invisible - Suivi de notes de travail - 9782070286256",
                    "subcategoryId": subcategories.LIVRE_PAPIER.id,
                },
                {"name": ["Le titre d'une offre ne peut contenir l'EAN"]},
            ),
            (
                {"subcategoryId": subcategories.ACHAT_INSTRUMENT.id, "url": "http://legrandj.eu"},
                {"url": ['Une offre de sous-catégorie "Achat instrument" ne peut contenir un champ `url`']},
            ),
            ({"url": "missing.something"}, {"url": ['L\'URL doit commencer par "http://" ou "https://"']}),
            ({"url": "https://missing"}, {"url": ['L\'URL doit terminer par une extension (ex. ".fr")']}),
            (
                {"externalTicketOfficeUrl": "missing.something"},
                {"externalTicketOfficeUrl": ['L\'URL doit commencer par "http://" ou "https://"']},
            ),
            (
                {"externalTicketOfficeUrl": "https://missing"},
                {"externalTicketOfficeUrl": ['L\'URL doit terminer par une extension (ex. ".fr")']},
            ),
            ({"subcategoryId": "ART_PRIMITIF"}, {"subcategory": ["La sous-catégorie de cette offre est inconnue"]}),
            (
                {"subcategoryId": "OEUVRE_ART"},
                {"subcategory": ["Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"]},
            ),
            (
                {"subcategoryId": subcategories.FESTIVAL_ART_VISUEL.id},
                {"offer": ["Une offre qui a un ticket retirable doit avoir un type de retrait renseigné"]},
            ),
            (
                {"subcategoryId": subcategories.FESTIVAL_ART_VISUEL.id, "withdrawalType": "no_ticket"},
                {"offer": ["Une offre qui a un ticket retirable doit avoir l'email du contact de réservation"]},
            ),
            (
                {"subcategoryId": subcategories.FESTIVAL_ART_VISUEL.id, "withdrawalType": "in_app"},
                {"withdrawalType": ["Withdrawal type cannot be in_app for manually created offers"]},
            ),
        ],
    )
    def test_fail_if_json_incorrect(self, client, input_json, expected_json):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = self._get_default_json(venue.id, subcategories.SPECTACLE_REPRESENTATION.id)
        data.update(input_json)

        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        assert response.status_code == 400
        assert response.json == expected_json


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_when_user_is_not_attached_to_offerer(self, client):
        # Given
        users_factories.ProFactory(email="user@example.com")
        venue = offerers_factories.VirtualVenueFactory()

        # When
        data = {
            "venueId": venue.id,
            "subcategoryId": subcategories.JEU_EN_LIGNE.id,
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "name": "Les orphelins",
        }
        response = client.with_session_auth("user@example.com").post("/offers", json=data)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        ]
