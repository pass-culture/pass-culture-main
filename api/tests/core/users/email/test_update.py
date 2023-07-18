import dataclasses
import datetime
from unittest.mock import patch

from freezegun import freeze_time
import pytest
from sqlalchemy.exc import IntegrityError

from pcapi.core import token as token_utils
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users import factories as users_factories
import pcapi.core.users.constants as users_constants
import pcapi.core.users.email.update as email_update
import pcapi.core.users.exceptions as users_exceptions
from pcapi.core.users.models import EmailHistoryEventTypeEnum
from pcapi.core.users.models import User
from pcapi.core.users.utils import decode_jwt_token
from pcapi.core.users.utils import encode_jwt_payload


pytestmark = pytest.mark.usefixtures("db_session")


def _initialize_token_old(user, new_email, app):  # delete after migration
    expiration_date = datetime.datetime.utcnow() + users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME
    token = encode_jwt_payload({"current_email": user.email, "new_email": new_email}, expiration_date)
    app.redis_client.set(
        email_update.get_token_key(user, email_update.TokenType.CONFIRMATION),
        token,
        ex=users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
    )
    return token


def _initialize_token(user, new_email, app=None):
    return token_utils.Token.create(
        type_=token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION,
        ttl=users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
        user_id=user.id,
        data={"new_email": new_email},
    ).encoded_token


class RequestEmailUpdateTest:
    def test_request_email_update_history(self):
        old_email = "py@test.com"
        password = "p@ssword"
        user = users_factories.UserFactory(email=old_email, password=password)
        new_email = "pypy@test.com"

        email_update.request_email_update(user, new_email, password)

        reloaded_user = User.query.get(user.id)
        assert len(reloaded_user.email_history) == 1

        history = reloaded_user.email_history[0]
        assert history.oldEmail == old_email
        assert history.newEmail == new_email
        assert history.eventType == EmailHistoryEventTypeEnum.UPDATE_REQUEST
        assert history.id is not None


class EmailUpdateConfirmationTest:
    @pytest.mark.parametrize(
        "token_init",
        [(_initialize_token), (_initialize_token_old)],
    )
    def test_email_update_confirmation(self, app, token_init):
        # Given
        user = users_factories.UserFactory()
        email_update_request = users_factories.EmailUpdateEntryFactory(user=user)
        token = token_init(user, email_update_request.newEmail, app)

        # When
        email_update.confirm_email_update_request(token)

        # Then
        # Email history is updated
        email_history = user.email_history
        assert len(email_history) == 2
        assert email_history[0].eventType == EmailHistoryEventTypeEnum.UPDATE_REQUEST
        assert email_history[1].eventType == EmailHistoryEventTypeEnum.CONFIRMATION

        # Confirmation email is sent
        assert len(mails_testing.outbox) == 1
        email_sent = mails_testing.outbox[0]
        assert email_sent.sent_data["To"] == email_update_request.newEmail
        assert email_sent.sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.EMAIL_CHANGE_CONFIRMATION.value
        )

        # Token is deleted
        assert app.redis_client.get(email_update.get_token_key(user, email_update.TokenType.CONFIRMATION)) is None

    @pytest.mark.parametrize(
        "token_init",
        [(_initialize_token), (_initialize_token_old)],
    )
    def test_update_email_confirmation_with_invalid_token(self, app, token_init):
        # Given
        user = users_factories.UserFactory()
        email_update_request = users_factories.EmailUpdateEntryFactory(user=user)  # existing confirmation token
        token_init(user, email_update_request.newEmail, app)
        invalid_token = encode_jwt_payload({"current_email": user.email, "new_email": "new@e.mail"})

        # When
        with pytest.raises(users_exceptions.InvalidToken):
            email_update.confirm_email_update_request(invalid_token)

        # Then
        # Email history is not updated
        email_history = user.email_history
        assert len(email_history) == 1
        assert email_history[0].eventType == EmailHistoryEventTypeEnum.UPDATE_REQUEST

        # Confirmation email is not sent
        assert len(mails_testing.outbox) == 0

        # Token is not deleted
        assert app.redis_client.get(
            email_update.get_token_key(user, email_update.TokenType.CONFIRMATION)
        ) is not None or token_utils.Token.token_exists(token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION, user.id)

    @pytest.mark.parametrize(
        "token_init",
        [(_initialize_token), (_initialize_token_old)],
    )
    def test_update_email_confirmation_email_already_exists(self, app, token_init):
        # Given
        user = users_factories.UserFactory()
        email_update_request = users_factories.EmailUpdateEntryFactory(user=user)
        token = token_init(user, email_update_request.newEmail, app)
        users_factories.UserFactory(email=email_update_request.newEmail)

        # When
        with pytest.raises(users_exceptions.EmailExistsError):
            email_update.confirm_email_update_request(token)

        # Then
        # Email history is not updated
        email_history = user.email_history
        assert len(email_history) == 1
        assert email_history[0].eventType == EmailHistoryEventTypeEnum.UPDATE_REQUEST

        # Confirmation email is not sent
        assert len(mails_testing.outbox) == 0

        # Token is not deleted
        assert app.redis_client.get(
            email_update.get_token_key(user, email_update.TokenType.CONFIRMATION)
        ) is not None or token_utils.Token.token_exists(token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION, user.id)

    @pytest.mark.parametrize(
        "token_init",
        [(_initialize_token), (_initialize_token_old)],
    )
    def test_update_email_confirmation_update_history_failed(self, app, token_init):
        # Given
        user = users_factories.UserFactory()
        email_update_request = users_factories.EmailUpdateEntryFactory(user=user)
        token = token_init(user, email_update_request.newEmail, app)

        with pytest.raises(Exception):
            with patch(
                "pcapi.core.users.models.UserEmailHistory.build_confirmation",
                side_effect=IntegrityError(statement="", params=(), orig=None),
            ):
                email_update.confirm_email_update_request(token)

        # Then
        # Email history is not updated
        email_history = user.email_history
        assert len(email_history) == 1

        # Confirmation email is already sent
        assert len(mails_testing.outbox) == 1

        # Token is not deleted
        assert app.redis_client.get(
            email_update.get_token_key(user, email_update.TokenType.CONFIRMATION)
        ) is not None or token_utils.Token.token_exists(token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION, user.id)


class EmailUpdateCancellationTest:
    @pytest.mark.parametrize(
        "token_init",
        [(_initialize_token), (_initialize_token_old)],
    )
    def test_email_update_cancellation(self, app, token_init):
        # Given
        user = users_factories.UserFactory()
        email_update_request = users_factories.EmailUpdateEntryFactory(user=user)
        token = token_init(user, email_update_request.newEmail, app)

        # When
        email_update.cancel_email_update_request(token)

        # Then
        # Email history is updated
        email_history = user.email_history
        assert len(email_history) == 2
        assert email_history[0].eventType == EmailHistoryEventTypeEnum.UPDATE_REQUEST
        assert email_history[1].eventType == EmailHistoryEventTypeEnum.CANCELLATION

        # Account is suspended
        assert user.is_active is False

        # Token is deleted
        assert app.redis_client.get(email_update.get_token_key(user, email_update.TokenType.CONFIRMATION)) is None

    @pytest.mark.parametrize(
        "token_init",
        [(_initialize_token), (_initialize_token_old)],
    )
    def test_email_update_cancellation_with_invalid_token(self, app, token_init):
        # Given
        user = users_factories.UserFactory()
        email_update_request = users_factories.EmailUpdateEntryFactory(user=user)

        token_init(user, email_update_request.newEmail, app)

        invalid_token = encode_jwt_payload({"current_email": user.email, "new_email": "new@e.mail"})

        # When
        with pytest.raises(users_exceptions.InvalidToken):
            email_update.cancel_email_update_request(invalid_token)

        # Then
        # Email history is not updated
        email_history = user.email_history
        assert len(email_history) == 1
        assert email_history[0].eventType == EmailHistoryEventTypeEnum.UPDATE_REQUEST

        # Account is not suspended
        assert user.is_active is True

        # Token is not deleted
        assert app.redis_client.get(
            email_update.get_token_key(user, email_update.TokenType.CONFIRMATION)
        ) is not None or token_utils.Token.token_exists(token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION, user.id)

    @pytest.mark.parametrize(
        "token_init",
        [(_initialize_token), (_initialize_token_old)],
    )
    def test_email_update_cancellation_suspend_account_failed(self, app, token_init):
        # Given
        user = users_factories.UserFactory()
        email_update_request = users_factories.EmailUpdateEntryFactory(user=user)
        token = token_init(user, email_update_request.newEmail, app)

        with pytest.raises(Exception):
            with patch(
                "pcapi.core.users.api.suspend_account",
                side_effect=Exception("Something went wrong"),
            ):
                email_update.cancel_email_update_request(token)

        # Then
        # Email history is not updated
        email_history = user.email_history
        assert len(email_history) == 1

        # Account is not suspended
        assert user.is_active is True

        # Token is not deleted
        assert app.redis_client.get(
            email_update.get_token_key(user, email_update.TokenType.CONFIRMATION)
        ) is not None or token_utils.Token.token_exists(token_utils.TokenType.EMAIL_CHANGE_CONFIRMATION, user.id)


class EmailUpdateTokenTest:
    @pytest.mark.parametrize(
        "token_type",
        [
            (email_update.TokenType.CONFIRMATION),
            (email_update.TokenType.VALIDATION),
        ],
    )
    def test_generate_email_change_token(self, app, token_type):
        # Given
        user = users_factories.UserFactory()
        new_email = "Updated_" + user.email
        expiration_date = email_update.generate_email_change_token_expiration_date()

        # When
        token = email_update.generate_email_change_token(
            user, new_email, expiration_date=expiration_date, token_type=token_type
        )

        # Then
        decoded_token = decode_jwt_token(token)
        assert app.redis_client.get(email_update.get_token_key(user, token_type)) == token
        assert decoded_token["current_email"] == user.email
        assert decoded_token["new_email"] == new_email
        assert decoded_token["exp"] == int(expiration_date.timestamp())

    @pytest.mark.parametrize(
        "token_type",
        [
            (email_update.TokenType.CONFIRMATION),
            (email_update.TokenType.VALIDATION),
        ],
    )
    def test_check_token_nominal(self, app, token_type):
        # Given
        user = users_factories.UserFactory()
        new_email = "Updated_" + user.email
        expiration_date = email_update.generate_email_change_token_expiration_date()
        token = email_update.generate_email_change_token(
            user, new_email, expiration_date=expiration_date, token_type=token_type
        )

        # should not raise
        email_update._check_token(user, token, token_type)

    @pytest.mark.parametrize(
        "token_type",
        [
            (email_update.TokenType.CONFIRMATION),
            (email_update.TokenType.VALIDATION),
        ],
    )
    def test_check_token_wrong_type(self, app, token_type):
        # Given
        user = users_factories.UserFactory()
        new_email = "Updated_" + user.email
        expiration_date = email_update.generate_email_change_token_expiration_date()
        token = email_update.generate_email_change_token(
            user, new_email, expiration_date=expiration_date, token_type=token_type
        )

        # When
        with pytest.raises(users_exceptions.InvalidToken):
            email_update._check_token(
                user,
                token,
                email_update.TokenType.CONFIRMATION
                if token_type == email_update.TokenType.VALIDATION
                else email_update.TokenType.VALIDATION,
            )

    @pytest.mark.parametrize(
        "token_type",
        [
            (email_update.TokenType.CONFIRMATION),
            (email_update.TokenType.VALIDATION),
        ],
    )
    def test_expire_token(self, app, token_type):
        # Given
        user = users_factories.UserFactory()
        new_email = "Updated_" + user.email
        expiration_date = email_update.generate_email_change_token_expiration_date()
        token = email_update.generate_email_change_token(
            user, new_email, expiration_date=expiration_date, token_type=token_type
        )

        # When
        email_update._expire_token(user, token_type)

        # Then
        assert app.redis_client.get(email_update.get_token_key(user, token_type)) is None

        with pytest.raises(users_exceptions.InvalidToken):
            email_update._check_token(user, token, token_type)

    @pytest.mark.parametrize(
        "token_type",
        [
            (email_update.TokenType.CONFIRMATION),
            (email_update.TokenType.VALIDATION),
        ],
    )
    @freeze_time("2021-01-01 00:00:00")
    def test_get_active_token_expiration(self, app, token_type):
        # Given
        user = users_factories.UserFactory()
        new_email = "Updated_" + user.email
        expiration_date = email_update.generate_email_change_token_expiration_date()
        email_update.generate_email_change_token(
            user, new_email, expiration_date=expiration_date, token_type=token_type
        )

        # When
        expiration = email_update.get_active_token_expiration(user)

        # Then
        assert expiration == expiration_date

    def test_get_active_token_expiration_no_token(self, app):
        # Given
        user = users_factories.UserFactory()

        # When
        expiration = email_update.get_active_token_expiration(user)

        # Then
        assert expiration is None
