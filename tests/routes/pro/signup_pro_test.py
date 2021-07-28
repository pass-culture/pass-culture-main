import pytest

from pcapi.core.offerers.factories import VirtualVenueTypeFactory
from pcapi.core.offerers.models import Offerer
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import UserOffererFactory
from pcapi.core.users.factories import ProFactory
from pcapi.core.users.models import User
from pcapi.models.user_offerer import UserOfferer

from tests.conftest import TestClient


BASE_DATA_PRO = {
    "email": "toto_pro@example.com",
    "publicName": "Toto Pro",
    "firstName": "Toto",
    "lastName": "Pro",
    "password": "__v4l1d_P455sw0rd__",
    "siren": "349974931",
    "address": "12 boulevard de Pesaro",
    "phoneNumber": "0102030405",
    "postalCode": "92000",
    "city": "Nanterre",
    "name": "Crédit Coopératif",
}


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def when_user_data_is_valid(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        venue_type = VirtualVenueTypeFactory()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers

        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user is not None
        assert user.isBeneficiary is False
        assert user.departementCode == "92"
        assert user.email == "toto_pro@example.com"
        assert user.firstName == "Toto"
        assert user.isAdmin is False
        assert user.lastName == "Pro"
        assert user.phoneNumber == "0102030405"
        assert user.postalCode == "92000"
        assert user.publicName == "Toto Pro"
        assert user.dateOfBirth is None
        assert user.dateCreated is not None
        assert user.notificationSubscriptions == {"marketing_push": True, "marketing_email": False}
        offerer = Offerer.query.filter_by(siren="349974931").first()
        assert offerer is not None
        assert offerer.validationToken is not None
        assert len(offerer.managedVenues) == 1
        assert offerer.managedVenues[0].isVirtual
        assert offerer.managedVenues[0].venueTypeId == venue_type.id
        user_offerer = UserOfferer.query.filter_by(user=user, offerer=offerer).first()
        assert user_offerer is not None
        assert user_offerer.validationToken is None

    def test_creates_user_offerer_digital_venue_and_userOfferer_and_does_not_log_user_in(self, app):
        # Given
        data_pro = BASE_DATA_PRO.copy()
        data_pro["contactOk"] = "true"
        venue_type = VirtualVenueTypeFactory()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data_pro)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers
        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user is not None
        assert user.notificationSubscriptions == {"marketing_push": True, "marketing_email": True}
        offerer = Offerer.query.filter_by(siren="349974931").first()
        assert offerer is not None
        assert offerer.validationToken is not None
        assert len(offerer.managedVenues) == 1
        assert offerer.managedVenues[0].isVirtual
        assert offerer.managedVenues[0].venueTypeId == venue_type.id
        user_offerer = UserOfferer.query.filter_by(user=user, offerer=offerer).first()
        assert user_offerer is not None
        assert user_offerer.validationToken is None

    def when_successful_and_existing_offerer_creates_editor_user_offerer_and_does_not_log_in(self, app):
        # Given
        VirtualVenueTypeFactory()
        offerer = OffererFactory(siren="349974931", validationToken="not_validated")
        pro = ProFactory(email="bobby@test.com", publicName="bobby")
        UserOffererFactory(user=pro, offerer=offerer)

        data = BASE_DATA_PRO.copy()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers
        pro = User.query.filter_by(email="toto_pro@example.com").first()
        assert pro is not None
        offerer = Offerer.query.filter_by(siren="349974931").first()
        assert offerer is not None
        user_offerer = UserOfferer.query.filter_by(user=pro, offerer=offerer).first()
        assert user_offerer is not None
        assert user_offerer.validationToken is not None

    def when_successful_and_existing_offerer_but_no_user_offerer_does_not_signin(self, app):
        # Given
        OffererFactory(siren="349974931")

        data = BASE_DATA_PRO.copy()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers
        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user is not None
        offerer = Offerer.query.filter_by(siren="349974931").first()
        assert offerer is not None
        user_offerer = UserOfferer.query.filter_by(user=user, offerer=offerer).first()
        assert user_offerer is not None
        assert user_offerer.validationToken is not None

    def when_successful_and_mark_pro_user_as_no_cultural_survey_needed(self, app):
        # Given
        OffererFactory(siren="349974931")

        data = BASE_DATA_PRO.copy()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user.needsToFillCulturalSurvey == False


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_email_is_missing(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["email"]

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def when_email_is_invalid(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        data["email"] = "toto"
        VirtualVenueTypeFactory()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def when_email_is_already_used(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        VirtualVenueTypeFactory()
        TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def when_public_name_is_missing(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["publicName"]
        VirtualVenueTypeFactory()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "publicName" in error

    def when_public_name_is_too_long(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        data["publicName"] = "x" * 300
        VirtualVenueTypeFactory()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "publicName" in error

    def when_password_is_missing(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["password"]

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "password" in error

    def when_password_is_invalid(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        data["password"] = "weakpassword"

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        response = response.json
        assert response["password"] == [
            "Ton mot de passe doit contenir au moins :\n"
            "- 12 caractères\n"
            "- Un chiffre\n"
            "- Une majuscule et une minuscule\n"
            "- Un caractère spécial"
        ]

    def when_offerer_name_is_missing(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["name"]
        VirtualVenueTypeFactory()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "name" in error

    def when_offerer_city_is_missing(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["city"]
        VirtualVenueTypeFactory()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "city" in error

    def when_postal_code_is_missing(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["postalCode"]
        VirtualVenueTypeFactory()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "postalCode" in error

    def when_invalid_postal_code(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        data["postalCode"] = "111"
        VirtualVenueTypeFactory()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "postalCode" in error

    def when_extra_data_is_given(self, app):
        # Given
        user_json = {
            "email": "toto_pro@example.com",
            "publicName": "Toto Pro",
            "firstName": "Toto",
            "lastName": "Pro",
            "password": "__v4l1d_P455sw0rd__",
            "siren": "349974931",
            "address": "12 boulevard de Pesaro",
            "phoneNumber": "0102030405",
            "postalCode": "92000",
            "city": "Nanterre",
            "name": "Crédit Coopératif",
            "isAdmin": True,
            "contactOk": "true",
        }
        VirtualVenueTypeFactory()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=user_json)

        # Then
        assert response.status_code == 400
        created_user = User.query.filter_by(email="toto_pro@example.com").first()
        assert created_user is None

    def when_invalid_phone_number(self, app):
        # Given
        data = BASE_DATA_PRO.copy()
        data["phoneNumber"] = "abc 123"
        VirtualVenueTypeFactory()

        # When
        response = TestClient(app.test_client()).post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "phoneNumber" in error
