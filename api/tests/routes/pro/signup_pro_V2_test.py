from dataclasses import asdict
from datetime import datetime

import pytest
from sqlalchemy.orm import joinedload

import pcapi.core.history.models as history_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers.factories import OffererInvitationFactory
from pcapi.core.users.factories import ProFactory
from pcapi.core.users.factories import UserProNewNavStateFactory
from pcapi.core.users.models import User


BASE_DATA_PRO = {
    "email": "toto_pro@example.com",
    "firstName": "Toto",
    "lastName": "Pro",
    "password": "__v4l1d_P455sw0rd__",
    "phoneNumber": "0102030405",
    "contactOk": False,
    "token": "token",
}


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def test_when_user_data_is_valid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers

        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user is not None
        assert user.has_beneficiary_role is False
        assert user.has_non_attached_pro_role is True
        assert user.email == "toto_pro@example.com"
        assert user.firstName == "Toto"
        assert not user.has_admin_role
        assert user.lastName == "Pro"
        assert user.phoneNumber == "+33102030405"
        assert user.dateOfBirth is None
        assert user.dateCreated is not None
        assert user.notificationSubscriptions == {
            "marketing_push": True,
            "marketing_email": False,
            "subscribed_themes": [],
        }

        actions_list = history_models.ActionHistory.query.order_by(history_models.ActionHistory.actionType).all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.USER_CREATED
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user

        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.EMAIL_VALIDATION_TO_PRO.value)

    def test_new_user_should_always_have_NPP(self, client):
        data = BASE_DATA_PRO.copy()
        emails = ["user1@example.com", "user2@example.com"]
        for email in emails:
            response = client.post("/v2/users/signup/pro", json=data | {"email": email})
            assert response.status_code == 204
        users = User.query.options(joinedload(User.pro_new_nav_state)).filter(User.pro_new_nav_state.has()).all()
        assert len(users) == 2
        for user in users:
            assert user.pro_new_nav_state.eligibilityDate is None
            assert user.pro_new_nav_state.newNavDate is not None

    def test_user_inherit_new_nav_for_inviter(self, client):
        """Test the new navigation activation at creation. Only the newNavDate is set
        The eligibilityDate is used to distinguish between the beta test dans the A/B test so It should only be set manually
        """
        inviter_with_new_nav = UserProNewNavStateFactory(newNavDate=datetime.utcnow()).user
        invitation_with_new_nav = OffererInvitationFactory(user=inviter_with_new_nav)
        inviter_with_old_nav = UserProNewNavStateFactory(newNavDate=None).user
        invitation_with_old_nav = OffererInvitationFactory(user=inviter_with_old_nav)
        inviter_without_nav_state = ProFactory()
        invitation_without_nav_state = OffererInvitationFactory(user=inviter_without_nav_state)
        data = BASE_DATA_PRO.copy()
        response = client.post("/v2/users/signup/pro", json=data | {"email": invitation_with_new_nav.email})
        assert response.status_code == 204
        user_invited = User.query.filter_by(email=invitation_with_new_nav.email).one()
        assert user_invited.pro_new_nav_state.eligibilityDate is None
        assert user_invited.pro_new_nav_state.newNavDate is not None

        response = client.post("/v2/users/signup/pro", json=data | {"email": invitation_with_old_nav.email})
        assert response.status_code == 204
        user_invited = User.query.filter_by(email=invitation_with_old_nav.email).one()
        assert user_invited.pro_new_nav_state is None

        response = client.post("/v2/users/signup/pro", json=data | {"email": invitation_without_nav_state.email})
        assert response.status_code == 204
        user_invited = User.query.filter_by(email=invitation_without_nav_state.email).one()
        assert user_invited.pro_new_nav_state is None

    def when_successful_and_mark_pro_user_as_no_cultural_survey_needed(self, client):
        data = BASE_DATA_PRO.copy()

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user.needsToFillCulturalSurvey is False


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_when_email_is_missing(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["email"]

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_email_is_invalid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["email"] = "toto"

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_email_is_already_used(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        client.post("/v2/users/signup/pro", json=data)

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_password_is_missing(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["password"]

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "password" in error

    def test_when_password_is_invalid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["password"] = "weakpassword"

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        response = response.json
        assert response["password"] == [
            "Le mot de passe doit contenir au moins :\n"
            "- 12 caractères\n"
            "- Un chiffre\n"
            "- Une majuscule et une minuscule\n"
            "- Un caractère spécial"
        ]

    def test_when_extra_data_is_given(self, client):
        # Given
        user_json = {
            "email": "toto_pro@example.com",
            "firstName": "Toto",
            "lastName": "Pro",
            "password": "__v4l1d_P455sw0rd__",
            "phoneNumber": "0102030405",
            "isAdmin": True,
            "contactOk": "true",
        }

        # When
        response = client.post("/v2/users/signup/pro", json=user_json)

        # Then
        assert response.status_code == 400
        created_user = User.query.filter_by(email="toto_pro@example.com").first()
        assert created_user is None

    def test_when_bad_format_phone_number(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["phoneNumber"] = "abc 123"

        # When
        response = client.post("/v2/users/signup/pro", json=data)

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
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "phoneNumber" in error
        assert "Le numéro de téléphone est invalide" in error["phoneNumber"]
