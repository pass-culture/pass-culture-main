import pytest

import pcapi.core.history.models as history_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.users.factories import ProFactory
from pcapi.core.users.models import User
from pcapi.models.validation_status_mixin import ValidationStatus


BASE_DATA_PRO = {
    "email": "toto_pro@example.com",
    "firstName": "Toto",
    "lastName": "Pro",
    "password": "__v4l1d_P455sw0rd__",
    "siren": "349974931",
    "address": "12 boulevard de Pesaro",
    "phoneNumber": "0102030405",
    "postalCode": "92000",
    "city": "Nanterre",
    "name": "Crédit Coopératif",
    "contactOk": False,
}


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def test_when_user_data_is_valid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers

        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user is not None
        assert user.has_beneficiary_role is False
        assert user.departementCode == "92"
        assert user.email == "toto_pro@example.com"
        assert user.firstName == "Toto"
        assert not user.has_admin_role
        assert user.lastName == "Pro"
        assert user.phoneNumber == "+33102030405"
        assert user.postalCode == "92000"
        assert user.dateOfBirth is None
        assert user.dateCreated is not None
        assert user.notificationSubscriptions == {"marketing_push": True, "marketing_email": False}
        offerer = Offerer.query.filter_by(siren="349974931").first()
        assert offerer is not None
        assert offerer.validationStatus == ValidationStatus.NEW
        assert len(offerer.managedVenues) == 1
        assert offerer.managedVenues[0].isVirtual
        assert offerer.managedVenues[0].venueTypeCode == offerers_models.VenueTypeCode.DIGITAL
        user_offerer = UserOfferer.query.filter_by(user=user, offerer=offerer).first()
        assert user_offerer is not None
        assert user_offerer.validationStatus == ValidationStatus.VALIDATED
        assert user_offerer.dateCreated is not None

        actions_list = history_models.ActionHistory.query.order_by(history_models.ActionHistory.actionType).all()
        assert len(actions_list) == 2
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == offerer
        assert actions_list[1].actionType == history_models.ActionType.USER_CREATED
        assert actions_list[1].authorUser == user
        assert actions_list[1].user == user
        assert actions_list[1].offerer == offerer

    def test_creates_user_offerer_digital_venue_and_userOfferer_and_does_not_log_user_in(self, client):
        # Given
        data_pro = BASE_DATA_PRO.copy()
        data_pro["contactOk"] = "true"

        # When
        response = client.post("/users/signup/pro", json=data_pro)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers
        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user is not None
        assert user.notificationSubscriptions == {"marketing_push": True, "marketing_email": True}
        offerer = Offerer.query.filter_by(siren="349974931").first()
        assert offerer is not None
        assert offerer.validationStatus == ValidationStatus.NEW
        assert len(offerer.managedVenues) == 1
        assert offerer.managedVenues[0].isVirtual
        assert offerer.managedVenues[0].venueTypeCode == offerers_models.VenueTypeCode.DIGITAL
        user_offerer = UserOfferer.query.filter_by(user=user, offerer=offerer).first()
        assert user_offerer is not None
        assert user_offerer.validationStatus == ValidationStatus.VALIDATED

    def when_successful_and_existing_offerer_creates_editor_user_offerer_and_does_not_log_in(self, client):
        # Given
        offerer = offerers_factories.NotValidatedOffererFactory(siren="349974931")
        pro = ProFactory(email="bobby@test.com")
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        data = BASE_DATA_PRO.copy()

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers
        pro = User.query.filter_by(email="toto_pro@example.com").first()
        assert pro is not None
        offerer = Offerer.query.filter_by(siren="349974931").first()
        assert offerer is not None
        user_offerer = UserOfferer.query.filter_by(user=pro, offerer=offerer).first()
        assert user_offerer is not None
        assert user_offerer.validationStatus == ValidationStatus.NEW

        actions_list = history_models.ActionHistory.query.order_by(history_models.ActionHistory.actionType).all()
        assert len(actions_list) == 2
        assert actions_list[0].actionType == history_models.ActionType.USER_CREATED
        assert actions_list[0].authorUser == pro
        assert actions_list[0].user == pro
        assert actions_list[0].offerer == offerer
        assert actions_list[1].actionType == history_models.ActionType.USER_OFFERER_NEW
        assert actions_list[1].authorUser == pro
        assert actions_list[1].user == pro
        assert actions_list[1].offerer == offerer

    def when_successful_and_existing_offerer_but_no_user_offerer_does_not_signin(self, client):
        # Given
        offerers_factories.OffererFactory(siren="349974931")

        data = BASE_DATA_PRO.copy()

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers
        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user is not None
        offerer = Offerer.query.filter_by(siren="349974931").first()
        assert offerer is not None
        user_offerer = UserOfferer.query.filter_by(user=user, offerer=offerer).first()
        assert user_offerer is not None
        assert user_offerer.validationStatus == ValidationStatus.NEW

    def when_successful_and_mark_pro_user_as_no_cultural_survey_needed(self, client):
        # Given
        offerers_factories.OffererFactory(siren="349974931")

        data = BASE_DATA_PRO.copy()

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user.needsToFillCulturalSurvey == False

    def test_when_offerer_was_previously_rejected(self, client):
        # Given
        offerer = offerers_factories.RejectedOffererFactory(
            name="Rejected Offerer",
            siren=BASE_DATA_PRO["siren"],
        )

        first_creation_date = offerer.dateCreated

        data = BASE_DATA_PRO.copy()

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers

        user = User.query.filter_by(email="toto_pro@example.com").first()
        offerer = Offerer.query.filter_by(siren="349974931").one()
        assert offerer.name == BASE_DATA_PRO["name"]
        assert offerer.validationStatus == ValidationStatus.NEW
        assert offerer.isActive
        assert offerer.dateCreated > first_creation_date
        user_offerer = UserOfferer.query.filter_by(user=user, offerer=offerer).one()
        assert user_offerer.validationStatus == ValidationStatus.VALIDATED
        assert user_offerer.dateCreated is not None

        actions_list = history_models.ActionHistory.query.order_by(history_models.ActionHistory.actionType).all()
        assert len(actions_list) == 2
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == offerer
        assert actions_list[0].comment == "Nouvelle demande sur un SIREN précédemment rejeté"
        assert actions_list[1].actionType == history_models.ActionType.USER_CREATED
        assert actions_list[1].authorUser == user
        assert actions_list[1].user == user
        assert actions_list[1].offerer == offerer


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_when_email_is_missing(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["email"]

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_email_is_invalid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["email"] = "toto"

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_email_is_already_used(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        client.post("/users/signup/pro", json=data)

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_password_is_missing(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["password"]

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "password" in error

    def test_when_password_is_invalid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["password"] = "weakpassword"

        # When
        response = client.post("/users/signup/pro", json=data)

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

    def test_when_offerer_name_is_missing(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["name"]

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "name" in error

    def test_when_offerer_city_is_missing(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["city"]

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "city" in error

    def test_when_postal_code_is_missing(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["postalCode"]

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "postalCode" in error

    def test_when_invalid_postal_code(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["postalCode"] = "111"

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "postalCode" in error

    def test_when_extra_data_is_given(self, client):
        # Given
        user_json = {
            "email": "toto_pro@example.com",
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

        # When
        response = client.post("/users/signup/pro", json=user_json)

        # Then
        assert response.status_code == 400
        created_user = User.query.filter_by(email="toto_pro@example.com").first()
        assert created_user is None

    def test_when_bad_format_phone_number(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["phoneNumber"] = "abc 123"

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "phoneNumber" in error
        assert "Le numéro de téléphone est invalide" in error["phoneNumber"]

    def test_when_invalid_phone_number(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["phoneNumber"] = "0873492896"

        # When
        response = client.post("/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "phoneNumber" in error
        assert "Le numéro de téléphone est invalide" in error["phoneNumber"]
