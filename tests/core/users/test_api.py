from datetime import date
from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import jwt
import pytest

from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users.api import _set_offerer_departement_code
from pcapi.core.users.api import create_id_check_token
from pcapi.core.users.api import fulfill_user_data
from pcapi.core.users.api import generate_and_save_token
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.core.users.repository import get_user_with_valid_token
from pcapi.core.users.utils import decode_jwt_token
from pcapi.core.users.utils import encode_jwt_payload
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.models.user_session import UserSession
from pcapi.repository import repository

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class GenerateAndSaveTokenTest:
    def test_generate_and_save_token(self, app):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = TokenType.RESET_PASSWORD
        life_time = timedelta(hours=24)

        generated_token = generate_and_save_token(user, token_type, life_time)

        saved_token = Token.query.filter_by(user=user).first()

        assert generated_token.id == saved_token.id
        assert saved_token.type == token_type
        decoded = decode_jwt_token(saved_token.value)
        assert decoded["userId"] == user.id
        assert decoded["type"] == token_type.value
        assert decoded["exp"] is not None

        with freeze_time(datetime.now() + timedelta(hours=48)):
            with pytest.raises(jwt.exceptions.ExpiredSignatureError):
                decode_jwt_token(saved_token.value)

        # ensure token is not valid for authentication
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {saved_token.value}"}
        response = test_client.get("/native/v1/me")
        assert response.status_code == 422

    def test_generate_and_save_token_without_expiration_date(self):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = TokenType.RESET_PASSWORD

        generate_and_save_token(user, token_type)

        generated_token = Token.query.filter_by(user=user).first()

        assert generated_token.type == token_type
        assert generated_token.expirationDate is None

        decoded = decode_jwt_token(generated_token.value)

        assert decoded["userId"] == user.id
        assert decoded["type"] == token_type.value
        assert "exp" not in decoded

    def test_generate_and_save_token_with_wrong_type(self):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = "not-enum-type"

        with pytest.raises(AttributeError):
            generate_and_save_token(user, token_type)


class ValidateJwtTokenTest:
    token_value = encode_jwt_payload({"pay": "load"})

    def test_get_user_with_valid_token(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD
        expiration_date = datetime.now() + timedelta(hours=24)

        saved_token = Token(
            from_dict={
                "userId": user.id,
                "value": self.token_value,
                "type": token_type,
                "expirationDate": expiration_date,
            }
        )
        repository.save(saved_token)

        associated_user = get_user_with_valid_token(self.token_value, [token_type, "other-allowed-type"])

        assert associated_user.id == user.id

    def test_get_user_with_valid_token_without_expiration_date(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        saved_token = Token(from_dict={"userId": user.id, "value": self.token_value, "type": token_type})
        repository.save(saved_token)

        associated_user = get_user_with_valid_token(self.token_value, [token_type])

        assert associated_user.id == user.id

    def test_get_user_with_valid_token_wrong_token(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        saved_token = Token(from_dict={"userId": user.id, "value": self.token_value, "type": token_type})
        repository.save(saved_token)

        associated_user = get_user_with_valid_token("wrong-token-value", [token_type])

        assert associated_user is None

    def test_get_user_with_valid_token_wrong_type(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        saved_token = Token(from_dict={"userId": user.id, "value": self.token_value, "type": token_type})
        repository.save(saved_token)

        assert Token.query.filter_by(value=self.token_value).first() is not None

        associated_user = get_user_with_valid_token(self.token_value, ["other_type"])

        assert associated_user is None

    def test_get_user_with_valid_token_with_expired_date(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        saved_token = Token(
            from_dict={
                "userId": user.id,
                "value": self.token_value,
                "type": token_type,
                "expirationDate": datetime.now() - timedelta(hours=24),
            }
        )
        repository.save(saved_token)

        assert Token.query.filter_by(value=self.token_value).first() is not None

        associated_user = get_user_with_valid_token(self.token_value, [token_type])

        assert associated_user is None


class GenerateIdCheckTokenIfEligibleTest:
    @freeze_time("2018-06-01")
    def test_when_elible(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1))
        token = create_id_check_token(user)
        assert token

    @freeze_time("2018-06-01")
    def test_when_not_elible_under_age(self):
        # user is 17 years old
        user = users_factories.UserFactory(dateOfBirth=datetime(2000, 8, 1))
        token = create_id_check_token(user)
        assert not token

    @freeze_time("2018-06-01")
    def test_when_not_elible_above_age(self):
        # user is 19 years old
        user = users_factories.UserFactory(dateOfBirth=datetime(1999, 5, 1))
        token = create_id_check_token(user)
        assert not token


class SuspendAccountTest:
    def test_suspend_account(self):
        user = users_factories.UserFactory(isAdmin=True)
        users_factories.UserSessionFactory(user=user)
        reason = users_constants.SuspensionReason.FRAUD
        actor = users_factories.UserFactory(isAdmin=True)

        users_api.suspend_account(user, reason, actor)

        assert user.suspensionReason == str(reason)
        assert not user.isActive
        assert not user.isAdmin
        assert not UserSession.query.filter_by(userId=user.id).first()
        assert actor.isActive


class UnsuspendAccountTest:
    def test_unsuspend_account(self):
        user = users_factories.UserFactory(isActive=False)
        actor = users_factories.UserFactory(isAdmin=True)

        users_api.unsuspend_account(user, actor)

        assert not user.suspensionReason
        assert user.isActive


@pytest.mark.usefixtures("db_session")
class ChangeUserEmailTest:
    @freeze_time("2020-10-15 09:00:00")
    def test_change_user_email(self):
        # Given
        user = users_factories.UserFactory(email="oldemail@mail.com", firstName="UniqueNameForEmailChangeTest")
        users_factories.UserSessionFactory(user=user)
        expiration_date = datetime.now() + timedelta(hours=1)
        token_payload = dict(current_email="oldemail@mail.com", new_email="newemail@mail.com")
        token = encode_jwt_payload(token_payload, expiration_date)

        # When
        users_api.change_user_email(token)

        # Then
        assert user.email == "newemail@mail.com"
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is not None
        assert new_user.firstName == "UniqueNameForEmailChangeTest"
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is None
        assert UserSession.query.filter_by(userId=user.id).first() is None

    def test_change_user_email_undecodable_token(self):
        # Given
        users_factories.UserFactory(email="oldemail@mail.com", firstName="UniqueNameForEmailChangeTest")
        token = "wtftokenwhatareyoutryingtodo"

        # When
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            users_api.change_user_email(token)

        # Then
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is not None
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is None

    @freeze_time("2020-10-15 09:00:00")
    def test_change_user_email_expired_token(self):
        # Given
        users_factories.UserFactory(email="oldemail@mail.com", firstName="UniqueNameForEmailChangeTest")
        expiration_date = datetime.now() - timedelta(hours=1)
        token_payload = dict(current_email="oldemail@mail.com", new_email="newemail@mail.com")
        token = encode_jwt_payload(token_payload, expiration_date)

        # When
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            users_api.change_user_email(token)

        # Then
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is not None
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is None

    @freeze_time("2020-10-15 09:00:00")
    def test_change_user_email_missing_argument_in_token(self):
        # Given
        users_factories.UserFactory(email="oldemail@mail.com", firstName="UniqueNameForEmailChangeTest")
        expiration_date = datetime.now() + timedelta(hours=1)
        missing_current_email_token_payload = dict(new_email="newemail@mail.com")
        missing_current_email_token = encode_jwt_payload(missing_current_email_token_payload, expiration_date)

        missing_new_email_token_payload = dict(current_email="oldemail@mail.com")
        missing_new_email_token = encode_jwt_payload(missing_new_email_token_payload, expiration_date)

        missing_exp_token_payload = dict(new_email="newemail@mail.com")
        missing_exp_token = encode_jwt_payload(missing_exp_token_payload)

        # When
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            users_api.change_user_email(missing_current_email_token)
            users_api.change_user_email(missing_new_email_token)
            users_api.change_user_email(missing_exp_token)

        # Then
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is not None
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is None

    @freeze_time("2020-10-15 09:00:00")
    def test_change_user_email_new_email_already_existing(self):
        # Given
        users_factories.UserFactory(email="newemail@mail.com", firstName="UniqueNameForEmailChangeTest")
        expiration_date = datetime.now() + timedelta(hours=1)
        token_payload = dict(current_email="oldemail@mail.com", new_email="newemail@mail.com")
        token = encode_jwt_payload(token_payload, expiration_date)

        # When
        users_api.change_user_email(token)

        # Then
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is None
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is not None

    @freeze_time("2020-10-15 09:00:00")
    def test_change_user_email_current_email_not_existing_anymore(self):
        # Given
        expiration_date = datetime.now() + timedelta(hours=1)
        token_payload = dict(current_email="oldemail@mail.com", new_email="newemail@mail.com")
        token = encode_jwt_payload(token_payload, expiration_date)

        # When
        users_api.change_user_email(token)

        # Then
        old_user = User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is None
        new_user = User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is None


class CreateBeneficiaryTest:
    def test_with_eligible_user(self):
        eligible_date = date.today() - relativedelta(years=18, days=30)
        user = users_factories.UserFactory(isBeneficiary=False, dateOfBirth=eligible_date)
        user = users_api.activate_beneficiary(user, "test")
        assert user.isBeneficiary
        assert len(user.deposits) == 1


class FulfillUserDataTest:
    def test_fill_user_with_password_token_and_deposit(self):
        # given
        user = User()

        # when
        user = fulfill_user_data(user, "deposit_source", None)

        # then
        assert isinstance(user, User)
        assert user.password is not None
        assert user.resetPasswordToken is not None
        assert len(user.deposits) == 1

    def test_fill_user_with_specific_deposit_version(self):
        # given
        user = User()

        # when
        user = fulfill_user_data(user, "deposit_source", 2)

        # then
        assert isinstance(user, User)
        assert user.password is not None
        assert user.resetPasswordToken is not None
        assert len(user.deposits) == 1
        assert user.deposit_version == 2


class SetOffererDepartementCodeTest:
    @patch("pcapi.settings.IS_INTEGRATION", True)
    def should_set_user_department_to_all_departments_in_integration(self):
        # Given
        new_user = create_user()
        offerer = create_offerer(postal_code="75019")

        # When
        updated_user = _set_offerer_departement_code(new_user, offerer)

        # Then
        assert updated_user.departementCode == "00"

    def should_set_user_department_to_undefined_department_code_when_offerer_has_none(self):
        # Given
        new_user = create_user()
        offerer = create_offerer(postal_code=None)

        # When
        updated_user = _set_offerer_departement_code(new_user, offerer)

        # Then
        assert updated_user.departementCode == "XX"

    def should_set_user_department_code_based_on_offerer(self):
        # Given
        new_user = create_user()
        offerer = create_offerer(postal_code="75019")

        # When
        updated_user = _set_offerer_departement_code(new_user, offerer)

        # Then
        assert updated_user.departementCode == "75"
