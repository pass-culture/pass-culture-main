import datetime
from decimal import Decimal
import logging
import pathlib
from unittest import mock

from dateutil.relativedelta import relativedelta
import fakeredis
from flask_jwt_extended.utils import decode_token
from freezegun import freeze_time
import pytest
import requests_mock

from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories_v2
import pcapi.core.finance.conf as finance_conf
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.geography import api as geography_api
from pcapi.core.geography import models as geography_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.subscription import api as subscription_api
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.email import update as email_update
from pcapi.core.users.repository import get_user_with_valid_token
from pcapi.core.users.utils import encode_jwt_payload
from pcapi.models import db
from pcapi.notifications.push import testing as batch_testing
from pcapi.routes.native.v1.serialization import account as account_serialization
from pcapi.routes.serialization.users import ImportUserFromCsvModel

import tests
from tests.test_utils import gen_offerer_tags


DATA_DIR = pathlib.Path(tests.__path__[0]) / "files"
pytestmark = pytest.mark.usefixtures("db_session")


class GenerateAndSaveTokenTest:
    def test_generate_and_save_token(self, app):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = users_models.TokenType.RESET_PASSWORD
        life_time = datetime.timedelta(hours=24)

        generated_token = users_api.generate_and_save_token(
            user, token_type, expiration=datetime.datetime.utcnow() + life_time
        )

        saved_token = users_models.Token.query.filter_by(user=user).first()

        assert generated_token.id == saved_token.id
        assert saved_token.type == token_type

    def test_generate_and_save_token_without_expiration_date(self):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = users_models.TokenType.RESET_PASSWORD

        users_api.generate_and_save_token(user, token_type)

        generated_token = users_models.Token.query.filter_by(user=user).first()

        assert generated_token.type == token_type
        assert generated_token.expirationDate is None

    def test_generate_and_save_token_with_wrong_type(self):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = "not-enum-type"

        with pytest.raises(AttributeError):
            users_api.generate_and_save_token(user, token_type)


class ValidateJwtTokenTest:
    token_value = encode_jwt_payload({"pay": "load"})

    def test_get_user_with_valid_token(self):
        user = users_factories.UserFactory()
        token_type = users_models.TokenType.RESET_PASSWORD
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(hours=24)

        saved_token = users_factories.TokenFactory(
            user=user, value=self.token_value, type=token_type, expirationDate=expiration_date
        )

        associated_user = get_user_with_valid_token(self.token_value, [token_type, "other-allowed-type"])

        assert associated_user.id == user.id
        assert users_models.Token.query.get(saved_token.id)

    def test_get_user_and_mark_token_as_used(self):
        user = users_factories.UserFactory()
        token_type = users_models.TokenType.RESET_PASSWORD
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(hours=24)

        saved_token = users_factories.TokenFactory(
            user=user, value=self.token_value, type=token_type, expirationDate=expiration_date
        )

        associated_user = get_user_with_valid_token(self.token_value, [token_type])

        assert associated_user.id == user.id

        token = users_models.Token.query.get(saved_token.id)
        assert token.isUsed

    def test_get_user_with_valid_token_without_expiration_date(self):
        user = users_factories.UserFactory()
        token_type = users_models.TokenType.RESET_PASSWORD

        users_factories.TokenFactory(user=user, value=self.token_value, type=token_type)

        associated_user = get_user_with_valid_token(self.token_value, [token_type])

        assert associated_user.id == user.id

    def test_get_user_with_valid_token_wrong_token(self):
        user = users_factories.UserFactory()
        token_type = users_models.TokenType.RESET_PASSWORD

        users_factories.TokenFactory(user=user, value=self.token_value, type=token_type)

        with pytest.raises(users_exceptions.InvalidToken):
            get_user_with_valid_token("wrong-token-value", [token_type])

    def test_get_user_with_valid_token_wrong_type(self):
        user = users_factories.UserFactory()
        token_type = users_models.TokenType.RESET_PASSWORD

        users_factories.TokenFactory(user=user, value=self.token_value, type=token_type)

        assert users_models.Token.query.filter_by(value=self.token_value).first() is not None

        with pytest.raises(users_exceptions.InvalidToken):
            get_user_with_valid_token(self.token_value, ["other_type"])

    def test_get_user_with_valid_token_with_expired_date(self):
        user = users_factories.UserFactory()
        token_type = users_models.TokenType.RESET_PASSWORD

        expiration_date = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        users_factories.TokenFactory(user=user, value=self.token_value, type=token_type, expirationDate=expiration_date)

        assert users_models.Token.query.filter_by(value=self.token_value).first() is not None

        with pytest.raises(users_exceptions.InvalidToken):
            get_user_with_valid_token(self.token_value, [token_type])


class DeleteExpiredTokensTest:
    def test_deletion(self):
        never_expire_token = users_factories.TokenFactory(expirationDate=None)
        not_expired_token = users_factories.TokenFactory(
            expirationDate=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        )
        expiration_after_delay = users_factories.TokenFactory(
            expirationDate=datetime.datetime.utcnow() - datetime.timedelta(days=6)
        )
        users_factories.TokenFactory(  # to delete
            expirationDate=datetime.datetime.utcnow() - users_constants.TOKEN_DELETION_AFTER_EXPIRATION_DELAY
        )

        users_api.delete_expired_tokens()

        assert set(users_models.Token.query.all()) == {never_expire_token, not_expired_token, expiration_after_delay}


class DeleteUserTokenTest:
    def test_delete_user_token(self):
        user = users_factories.UserFactory()
        token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD,
            users_constants.RESET_PASSWORD_TOKEN_LIFE_TIME,
            user.id,
        )
        token_utils.Token.create(
            token_utils.TokenType.EMAIL_VALIDATION, users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME, user.id
        )

        other_user = users_factories.BeneficiaryGrant18Factory()
        token_utils.Token.create(
            token_utils.TokenType.EMAIL_VALIDATION, users_constants.EMAIL_VALIDATION_TOKEN_LIFE_TIME, other_user.id
        )

        users_api.delete_all_users_tokens(user)

        assert not token_utils.Token.token_exists(token_utils.TokenType.EMAIL_VALIDATION, user.id)
        assert token_utils.Token.token_exists(token_utils.TokenType.EMAIL_VALIDATION, other_user.id)
        assert not token_utils.Token.token_exists(token_utils.TokenType.RESET_PASSWORD, user.id)


def _datetime_within_last_5sec(when: datetime.datetime) -> bool:
    return datetime.datetime.utcnow() - relativedelta(seconds=5) < when < datetime.datetime.utcnow()


def _assert_user_action_history_as_expected(
    action: history_models.ActionHistory,
    user: users_models.User,
    author: users_models.User,
    actionType: history_models.ActionType,
    reason: users_constants.SuspensionReason,
    comment: str | None = None,
):
    assert action.user == user
    assert action.authorUser == author
    assert action.actionType == actionType
    if reason:
        assert action.extraData["reason"] == reason.value
    else:
        assert action.extraData == {}
    assert action.comment == comment


@pytest.mark.usefixtures("db_session")
class CancelBeneficiaryBookingsOnSuspendAccountTest:
    def should_cancel_booking_when_the_offer_is_a_thing(self):
        booking_thing = bookings_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories_v2.CARTE_CINE_ILLIMITE.id,
            status=BookingStatus.CONFIRMED,
        )

        author = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION

        users_api.suspend_account(booking_thing.user, reason, author)

        assert booking_thing.status is BookingStatus.CANCELLED

    def should_cancel_booking_when_event_is_still_cancellable(self):
        """
        ---[        cancellable       ][         not cancellable        ]-->
        ---|---------------------------|--------------------------------|-->
        booking date         date cancellation limit                event date

        -----------------|------------------------------------------------->
                        now
        """
        in_the_past = datetime.datetime.utcnow() - relativedelta(days=1)
        in_the_future = datetime.datetime.utcnow() + relativedelta(days=1)
        booking_event = bookings_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories_v2.SEANCE_CINE.id,
            status=BookingStatus.CONFIRMED,
            dateCreated=in_the_past,
            cancellationLimitDate=in_the_future,
        )

        author = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION

        users_api.suspend_account(booking_event.user, reason, author)

        assert booking_event.status is BookingStatus.CANCELLED

    def should_not_cancel_event_when_cancellation_limit_date_is_past(self):
        """
        ---[        cancellable       ][         not cancellable        ]-->
        ---|---------------------------|--------------------------------|-->
        booking date         date cancellation limit                event date

        -------------------------------------------------|----------------->
                                                        now
        """
        in_the_past = datetime.datetime.utcnow() - relativedelta(seconds=1)
        further_in_the_past = datetime.datetime.utcnow() - relativedelta(days=3)
        booking_event = bookings_factories.BookingFactory(
            stock__offer__subcategoryId=subcategories_v2.SEANCE_CINE.id,
            status=BookingStatus.CONFIRMED,
            dateCreated=further_in_the_past,
            cancellationLimitDate=in_the_past,
        )

        author = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION

        users_api.suspend_account(booking_event.user, reason, author)

        assert booking_event.status is BookingStatus.CONFIRMED


@pytest.mark.usefixtures("db_session")
class SuspendAccountTest:
    def test_suspend_admin(self):
        user = users_factories.AdminFactory()
        users_factories.UserSessionFactory(user=user)
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION
        author = users_factories.AdminFactory()

        users_api.suspend_account(user, reason, author)

        assert user.suspension_reason == reason
        assert _datetime_within_last_5sec(user.suspension_date)
        assert not user.isActive
        assert not user.has_admin_role
        assert not users_models.UserSession.query.filter_by(userId=user.id).first()
        assert author.isActive

        history = history_models.ActionHistory.query.filter_by(userId=user.id).all()
        assert len(history) == 1
        _assert_user_action_history_as_expected(
            history[0], user, author, history_models.ActionType.USER_SUSPENDED, reason
        )

    def test_suspend_beneficiary(self):
        user = users_factories.BeneficiaryGrant18Factory()
        cancellable_booking = bookings_factories.BookingFactory(user=user)
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        confirmed_booking = bookings_factories.BookingFactory(
            user=user, cancellation_limit_date=yesterday, status=BookingStatus.CONFIRMED
        )
        used_booking = bookings_factories.UsedBookingFactory(user=user)
        author = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION
        comment = "Dossier n°12345"
        old_password_hash = user.password

        users_api.suspend_account(user, reason, author, comment=comment)

        db.session.refresh(user)

        assert not user.isActive
        assert user.password == old_password_hash
        assert user.suspension_reason == reason
        assert _datetime_within_last_5sec(user.suspension_date)

        assert cancellable_booking.status is BookingStatus.CANCELLED
        assert confirmed_booking.status is BookingStatus.CONFIRMED
        assert used_booking.status is BookingStatus.USED

        history = history_models.ActionHistory.query.filter_by(userId=user.id).all()
        assert len(history) == 1
        _assert_user_action_history_as_expected(
            history[0], user, author, history_models.ActionType.USER_SUSPENDED, reason, comment
        )

    def test_suspend_pro(self):
        booking = bookings_factories.BookingFactory()
        pro = offerers_factories.UserOffererFactory(offerer=booking.offerer).user
        author = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION

        users_api.suspend_account(pro, reason, author)

        assert not pro.isActive
        assert booking.status is BookingStatus.CANCELLED

        history = history_models.ActionHistory.query.filter_by(userId=pro.id).all()
        assert len(history) == 1
        _assert_user_action_history_as_expected(
            history[0], pro, author, history_models.ActionType.USER_SUSPENDED, reason
        )

    def test_suspend_pro_with_other_offerer_users(self):
        booking = bookings_factories.BookingFactory()
        pro = offerers_factories.UserOffererFactory(offerer=booking.offerer).user
        offerers_factories.UserOffererFactory(offerer=booking.offerer)
        author = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION

        users_api.suspend_account(pro, reason, author)

        assert not pro.isActive
        assert booking.status is not BookingStatus.CANCELLED

        history = history_models.ActionHistory.query.filter_by(userId=pro.id).all()
        assert len(history) == 1
        _assert_user_action_history_as_expected(
            history[0], pro, author, history_models.ActionType.USER_SUSPENDED, reason
        )

    def should_change_password_when_user_is_suspended_for_suspicious_login(self):
        user = users_factories.UserFactory()
        old_password_hash = user.password

        users_api.suspend_account(user, users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER, user)

        assert user.password != old_password_hash

    @pytest.mark.parametrize(
        "reason",
        [
            users_constants.SuspensionReason.FRAUD_SUSPICION,
            users_constants.SuspensionReason.UPON_USER_REQUEST,
            users_constants.SuspensionReason.SUSPENSION_FOR_INVESTIGATION_TEMP,
            users_constants.SuspensionReason.FRAUD_USURPATION,
        ],
    )
    def should_not_change_password_when_user_is_suspended_for_reason_other_than_suspicious_login(self, reason):
        user = users_factories.UserFactory()
        old_password_hash = user.password

        users_api.suspend_account(user, reason, user)

        assert user.password == old_password_hash


class UnsuspendAccountTest:
    def test_unsuspend_account(self):
        user = users_factories.UserFactory(isActive=False)
        author = users_factories.AdminFactory()

        comment = "Confusion avec un homonyme"
        users_api.unsuspend_account(user, author, comment=comment)

        assert not user.suspension_reason
        assert not user.suspension_date
        assert user.isActive

        history = history_models.ActionHistory.query.filter_by(userId=user.id).all()
        assert len(history) == 1
        _assert_user_action_history_as_expected(
            history[0], user, author, history_models.ActionType.USER_UNSUSPENDED, reason=None, comment=comment
        )

    def should_send_reset_password_email_when_user_is_suspended_for_suspicious_login(self):
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER
        )
        author = users_factories.AdminFactory()

        users_api.unsuspend_account(user, author)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["params"]["RESET_PASSWORD_LINK"]

    @pytest.mark.parametrize(
        "reason",
        [
            users_constants.SuspensionReason.FRAUD_SUSPICION,
            users_constants.SuspensionReason.UPON_USER_REQUEST,
            users_constants.SuspensionReason.SUSPENSION_FOR_INVESTIGATION_TEMP,
            users_constants.SuspensionReason.FRAUD_FAKE_DOCUMENT,
        ],
    )
    def should_not_send_reset_password_email_when_user_is_suspended_for_reason_other_than_suspicious_login(
        self, reason
    ):
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=reason)
        author = users_factories.AdminFactory()

        users_api.unsuspend_account(user, author)

        assert len(mails_testing.outbox) == 0


@pytest.mark.usefixtures("db_session")
class ChangeUserEmailTest:
    old_email = "oldemail@mail.com"
    new_email = "newemail@mail.com"
    mock_redis_client = fakeredis.FakeStrictRedis()

    def _init_token(self, user):
        return token_utils.Token.create(
            token_utils.TokenType.EMAIL_CHANGE_VALIDATION,
            users_constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user.id,
            {"new_email": self.new_email},
        ).encoded_token

    def test_change_user_email(self):
        # Given
        user = users_factories.UserFactory(email=self.old_email, firstName="UniqueNameForEmailChangeTest")
        users_factories.UserSessionFactory(user=user)

        token = self._init_token(user)
        # When
        returned_user = email_update.validate_email_update_request(token)

        # Then
        reloaded_user = users_models.User.query.get(user.id)
        assert returned_user == reloaded_user
        assert reloaded_user.email == self.new_email
        assert users_models.User.query.filter_by(email=self.old_email).first() is None
        assert users_models.UserSession.query.filter_by(userId=reloaded_user.id).first() is None

        assert len(reloaded_user.email_history) == 1

        history = reloaded_user.email_history[0]
        assert history.oldEmail == self.old_email
        assert history.newEmail == self.new_email
        assert history.eventType == users_models.EmailHistoryEventTypeEnum.VALIDATION
        assert history.id is not None

    def test_change_user_email_new_email_already_existing(self):
        # Given
        user = users_factories.UserFactory(email=self.old_email, firstName="UniqueNameForEmailChangeTest")
        other_user = users_factories.UserFactory(email=self.new_email)
        token = self._init_token(user)

        # When
        with pytest.raises(users_exceptions.EmailExistsError):
            email_update.validate_email_update_request(token)

        # Then
        user = users_models.User.query.get(user.id)
        assert user.email == "oldemail@mail.com"

        other_user = users_models.User.query.get(other_user.id)
        assert other_user.email == self.new_email

    def test_change_user_email_expired_token(self, app):
        # Given
        user = users_factories.UserFactory(email=self.old_email, firstName="UniqueNameForEmailChangeTest")
        users_factories.UserSessionFactory(user=user)
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            with freeze_time("2021-01-01"):
                token = self._init_token(user)

            # When
            with freeze_time("2021-01-03"):
                with pytest.raises(users_exceptions.InvalidToken):
                    email_update.validate_email_update_request(token)

                # Then
                user = users_models.User.query.get(user.id)
                assert user.email == self.old_email

    def test_change_user_email_twice(self):
        """
        Test that when the function is called twice:
            1. no error is raised
            2. no email updated is performed (email history stays the
               same)
        Update has been done, no need to panic.
        """

        user = users_factories.UserFactory(email=self.old_email)
        users_factories.UserSessionFactory(user=user)
        token = self._init_token(user)

        # first call, email is updated as expected
        returned_user = email_update.validate_email_update_request(token)

        reloaded_user = users_models.User.query.get(user.id)
        assert returned_user == reloaded_user
        assert reloaded_user.email == self.new_email

        # second call, no error, no update
        returned_user = email_update.validate_email_update_request(token)
        reloaded_user = users_models.User.query.get(user.id)
        assert returned_user == reloaded_user
        assert reloaded_user.email == self.new_email

    def test_validating_email_updates_external_contact(self):
        # Given
        user = users_factories.UserFactory(email=self.old_email, firstName="UniqueNameForEmailChangeTest")
        users_factories.UserSessionFactory(user=user)

        token = self._init_token(user)
        # When
        email_update.validate_email_update_request(token)

        assert sendinblue_testing.sendinblue_requests == [
            {"email": self.old_email, "attributes": {"EMAIL": self.new_email}, "emailBlacklisted": False}
        ]


class CreateBeneficiaryTest:
    def test_with_eligible_user(self):
        user = users_factories.UserFactory(roles=[])
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        user = subscription_api.activate_beneficiary_for_eligibility(
            user, fraud_check, users_models.EligibilityType.AGE18
        )
        assert user.has_beneficiary_role
        assert len(user.deposits) == 1

    def test_with_eligible_underage_user(self):
        user = users_factories.UserFactory(
            roles=[], validatedBirthDate=datetime.date.today() - relativedelta(years=16, months=4)
        )
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(registration_datetime=datetime.datetime.utcnow()),
        )
        user = subscription_api.activate_beneficiary_for_eligibility(
            user, fraud_check, users_models.EligibilityType.UNDERAGE
        )
        assert user.has_underage_beneficiary_role
        assert len(user.deposits) == 1
        assert user.has_active_deposit
        assert user.deposit.amount == 30

    def test_apps_flyer_called(self):
        apps_flyer_data = {
            "apps_flyer": {"user": "some-user-id", "platform": "ANDROID"},
            "firebase_pseudo_id": "firebase_pseudo_id",
        }
        user = users_factories.UserFactory(externalIds=apps_flyer_data)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        expected = {
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary",
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": "GRANT_18",
            },
        }

        with requests_mock.Mocker() as request_mock:
            posted = request_mock.post("https://api2.appsflyer.com/inappevent/app.passculture.webapp")
            user = subscription_api.activate_beneficiary_for_eligibility(
                user, fraud_check, users_models.EligibilityType.AGE18
            )

            assert posted.last_request.json() == expected

            assert user.has_beneficiary_role
            assert len(user.deposits) == 1

    def test_external_users_updated(self):
        user = users_factories.UserFactory(roles=[])
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        subscription_api.activate_beneficiary_for_eligibility(user, fraud_check, users_models.EligibilityType.AGE18)

        assert len(batch_testing.requests) == 3
        assert len(sendinblue_testing.sendinblue_requests) == 1

        trigger_event_log = batch_testing.requests[2]
        assert trigger_event_log["user_id"] == user.id
        assert trigger_event_log["event_name"] == "user_deposit_activated"
        assert trigger_event_log["event_payload"] == {"deposit_type": "GRANT_18", "deposit_amount": 300}

    @freeze_time("2020-03-01")
    def test_15yo_that_started_at_14_is_activated(self):
        fifteen_years_and_one_week_ago = datetime.datetime(2005, 2, 22)
        one_month_ago = datetime.datetime(2020, 2, 1)

        fifteen_year_old = users_factories.UserFactory(validatedBirthDate=fifteen_years_and_one_week_ago)

        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=fifteen_year_old,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(registration_datetime=one_month_ago),
        )

        subscription_api.activate_beneficiary_for_eligibility(
            fifteen_year_old, fraud_check, users_models.EligibilityType.UNDERAGE
        )

        assert fifteen_year_old.is_beneficiary
        assert fifteen_year_old.deposit.amount == 20


class SetOffererDepartementCodeTest:
    def test_with_empty_postal_code(self):
        # Given
        new_user = users_factories.ProFactory.build()
        offerer = offerers_factories.OffererFactory.build(postalCode=None)

        # When
        updated_user = users_api._set_offerer_departement_code(new_user, offerer)

        # Then
        assert updated_user.departementCode is None

    def test_with_set_postal_code(self):
        # Given
        new_user = users_factories.ProFactory.build()
        offerer = offerers_factories.OffererFactory.build(postalCode="75019")

        # When
        updated_user = users_api._set_offerer_departement_code(new_user, offerer)

        # Then
        assert updated_user.departementCode == "75"


@pytest.mark.usefixtures("db_session")
class SetProTutoAsSeenTest:
    def should_set_has_seen_pro_tutorials_to_true_for_user(self):
        # Given
        user = users_factories.UserFactory(hasSeenProTutorials=False)

        # When
        users_api.set_pro_tuto_as_seen(user)

        # Then
        assert users_models.User.query.one().hasSeenProTutorials is True


@pytest.mark.usefixtures("db_session")
class SetProRgsAsSeenTest:
    def should_set_has_seen_pro_rgs_to_true_for_user(self):
        # Given
        user = users_factories.UserFactory(hasSeenProRgs=False)

        # When
        users_api.set_pro_rgs_as_seen(user)

        # Then
        assert users_models.User.query.one().hasSeenProRgs is True


@pytest.mark.usefixtures("db_session")
class UpdateUserInfoTest:
    def test_update_user_info(self):
        user = users_factories.UserFactory(email="initial@example.com")

        users_api.update_user_info(user, author=user, first_name="New", last_name="Name")
        user = users_models.User.query.one()
        assert user.email == "initial@example.com"
        assert user.full_name == "New Name"

        users_api.update_user_info(user, author=user, email="new@example.com")
        user = users_models.User.query.one()
        assert user.email == "new@example.com"
        assert user.full_name == "New Name"

    def test_update_user_info_sanitizes_email(self):
        user = users_factories.UserFactory(email="initial@example.com")

        users_api.update_user_info(user, author=user, email="  NEW@example.com   ")
        user = users_models.User.query.one()
        assert user.email == "new@example.com"

    def test_update_user_info_returns_modified_info(self):
        user = users_factories.UserFactory(firstName="Noël", lastName="Flantier")

        modified_info = users_api.update_user_info(
            user, author=user, first_name="Hubert", last_name="Bonisseur de la Bath"
        )
        assert modified_info.to_dict() == {
            "firstName": {"new_info": "Hubert", "old_info": "Noël"},
            "lastName": {"new_info": "Bonisseur de la Bath", "old_info": "Flantier"},
        }

    def test_update_user_info_also_updates_underage_deposit_expiration_date(self):
        # Given a user with an underage deposit
        with freeze_time("2020-05-01"):
            user = users_factories.BeneficiaryFactory(age=17)
            users_api.update_user_info(user, author=user, validated_birth_date=datetime.date(2003, 1, 1))

        assert user.deposits[0].expirationDate == datetime.datetime(2021, 1, 1)


@pytest.mark.usefixtures("db_session")
class DomainsCreditTest:
    def test_get_domains_credit_v1(self):
        user = users_factories.BeneficiaryGrant18Factory(deposit__version=1, deposit__amount=500)

        # booking only in all domains
        bookings_factories.BookingFactory(
            user=user,
            amount=50,
            stock__offer__subcategoryId=subcategories_v2.SEANCE_CINE.id,
        )
        bookings_factories.BookingFactory(
            user=user,
            amount=5,
            stock__offer__subcategoryId=subcategories_v2.SEANCE_CINE.id,
        )

        # booking in digital domain
        bookings_factories.BookingFactory(
            user=user,
            amount=80,
            stock__offer__subcategoryId=subcategories_v2.JEU_EN_LIGNE.id,
            stock__offer__url="http://on.line",
        )

        # booking in physical domain
        bookings_factories.BookingFactory(
            user=user,
            amount=150,
            stock__offer__subcategoryId=subcategories_v2.JEU_SUPPORT_PHYSIQUE.id,
        )

        # cancelled booking
        bookings_factories.CancelledBookingFactory(
            user=user,
            amount=150,
            stock__offer__subcategoryId=subcategories_v2.JEU_SUPPORT_PHYSIQUE.id,
        )

        assert users_api.get_domains_credit(user) == users_models.DomainsCredit(
            all=users_models.Credit(initial=Decimal(500), remaining=Decimal(215)),
            digital=users_models.Credit(initial=Decimal(200), remaining=Decimal(120)),
            physical=users_models.Credit(initial=Decimal(200), remaining=Decimal(50)),
        )

    def test_get_domains_credit(self):
        user = users_factories.BeneficiaryGrant18Factory()

        # booking in physical domain
        bookings_factories.BookingFactory(
            user=user,
            amount=250,
            stock__offer__subcategoryId=subcategories_v2.JEU_SUPPORT_PHYSIQUE.id,
        )

        assert users_api.get_domains_credit(user) == users_models.DomainsCredit(
            all=users_models.Credit(initial=Decimal(300), remaining=Decimal(50)),
            digital=users_models.Credit(initial=Decimal(100), remaining=Decimal(50)),
            physical=None,
        )

    def test_get_domains_credit_deposit_expired(self):
        user = users_factories.BeneficiaryGrant18Factory()
        bookings_factories.BookingFactory(
            user=user,
            amount=250,
            stock__offer__subcategoryId=subcategories_v2.JEU_SUPPORT_PHYSIQUE.id,
        )

        with freeze_time(
            datetime.datetime.utcnow() + relativedelta(years=finance_conf.GRANT_18_VALIDITY_IN_YEARS, days=2)
        ):
            assert users_api.get_domains_credit(user) == users_models.DomainsCredit(
                all=users_models.Credit(initial=Decimal(300), remaining=Decimal(0)),
                digital=users_models.Credit(initial=Decimal(100), remaining=Decimal(0)),
                physical=None,
            )

    def test_get_domains_credit_no_deposit(self):
        user = users_factories.UserFactory()

        assert not users_api.get_domains_credit(user)


class CreateProUserTest:
    data = {
        "email": "prouser@example.com",
        "password": "P@ssword12345",
        "firstName": "Jean",
        "lastName": "Test",
        "contactOk": False,
        "phoneNumber": "0666666666",
        "name": "Le Petit Rintintin",
        "siren": "123456789",
        "address": "1 rue du test",
        "postalCode": "44000",
        "city": "Nantes",
    }

    def test_create_pro_user(self):
        pro_user_creation_body = ImportUserFromCsvModel(**self.data)

        pro_user = users_api.create_pro_user(pro_user_creation_body)

        assert pro_user.email == "prouser@example.com"
        assert not pro_user.has_admin_role
        assert not pro_user.needsToFillCulturalSurvey
        assert not pro_user.has_pro_role
        assert not pro_user.has_admin_role
        assert not pro_user.has_beneficiary_role
        assert not pro_user.deposits

    @override_settings(IS_INTEGRATION=True)
    def test_create_pro_user_in_integration(self):
        pro_user_creation_body = ImportUserFromCsvModel(**self.data)

        pro_user = users_api.create_pro_user(pro_user_creation_body)

        assert pro_user.email == "prouser@example.com"
        assert not pro_user.has_admin_role
        assert not pro_user.needsToFillCulturalSurvey
        assert not pro_user.has_pro_role
        assert not pro_user.has_admin_role
        assert pro_user.has_beneficiary_role
        assert pro_user.deposits


class CreateProUserAndOffererTest:
    @override_settings(NATIONAL_PARTNERS_EMAIL_DOMAINS="example.com,partner.com")
    def test_offerer_auto_tagging(self):
        # Given
        gen_offerer_tags()
        user_info = ImportUserFromCsvModel(
            address="1 rue des polissons",
            city="Paris",
            email="user@example.com",
            firstName="Jerry",
            lastName="khan",
            name="The best name",
            password="The p@ssw0rd",
            phoneNumber="0607080910",
            postalCode="75017",
            siren=777084122,
            contactOk=True,
        )

        # When
        user = users_api.import_pro_user_and_offerer_from_csv(user_info)

        # Then
        offerer = user.UserOfferers[0].offerer
        assert offerer.name == user_info.name
        assert "Partenaire national" in (tag.label for tag in offerer.tags)


class BeneficiaryInformationUpdateTest:
    def test_update_user_information_from_dms(self):
        declared_on_signup_date_of_birth = datetime.datetime(2000, 1, 1, 0, 0)
        declared_on_dms_date_of_birth = datetime.date(2000, 5, 1)
        user = users_factories.UserFactory(
            activity=None,
            address=None,
            city=None,
            firstName=None,
            lastName=None,
            postalCode=None,
            dateOfBirth=declared_on_signup_date_of_birth,
        )
        beneficiary_information = fraud_models.DMSContent(
            last_name="Doe",
            first_name="Jane",
            activity="Lycéen",
            civility=users_models.GenderEnum.F,
            birth_date=declared_on_dms_date_of_birth,
            email="jane.doe@test.com",
            phone="0612345678",
            postal_code="67200",
            address="11 Rue du Test",
            application_number=123,
            procedure_number=98012,
            registration_datetime=datetime.datetime(2020, 5, 1),
        )

        # when
        beneficiary = users_api.update_user_information_from_external_source(user, beneficiary_information, commit=True)

        # Then
        assert beneficiary.lastName == "Doe"
        assert beneficiary.firstName == "Jane"
        assert beneficiary.postalCode == "67200"
        assert beneficiary.address == "11 Rue du Test"
        assert beneficiary.validatedBirthDate == declared_on_dms_date_of_birth
        assert beneficiary.dateOfBirth == declared_on_signup_date_of_birth
        assert not beneficiary.has_beneficiary_role
        assert not beneficiary.has_admin_role
        assert beneficiary.password is not None
        assert beneficiary.activity == "Lycéen"
        assert beneficiary.civility == "Mme"
        assert not beneficiary.deposits

    def test_update_user_information_from_educonnect(self):
        user = users_factories.UserFactory(
            firstName=None,
            lastName=None,
        )
        educonnect_data = fraud_factories.EduconnectContentFactory(
            first_name="Raoul",
            last_name="Dufy",
            birth_date=datetime.date(2000, 5, 1),
            ine_hash="identifiantnati0naleleve",
        )
        new_user = users_api.update_user_information_from_external_source(user, educonnect_data)

        assert new_user.firstName == "Raoul"
        assert new_user.lastName == "Dufy"
        assert new_user.validatedBirthDate == datetime.date(2000, 5, 1)
        assert new_user.ineHash == "identifiantnati0naleleve"

    def test_update_user_information_from_ubble(self):
        user = users_factories.UserFactory(civility=None)
        ubble_data = fraud_factories.UbbleContentFactory(
            first_name="Raoul",
            last_name="Dufy",
            birth_date=datetime.date(2000, 5, 1).isoformat(),
            id_document_number="123456789",
            gender=users_models.GenderEnum.M,
        )
        new_user = users_api.update_user_information_from_external_source(user, ubble_data)

        assert new_user.firstName == "Raoul"
        assert new_user.lastName == "Dufy"
        assert new_user.validatedBirthDate == datetime.date(2000, 5, 1)
        assert new_user.idPieceNumber == "123456789"
        assert new_user.civility == "M."

    def test_update_user_information_from_ubble_with_married_name(self):
        user = users_factories.UserFactory(civility=None)
        ubble_data = fraud_factories.UbbleContentFactory(married_name="Flouz")
        new_user = users_api.update_user_information_from_external_source(user, ubble_data)

        assert new_user.married_name == "Flouz"

    def test_update_id_piece_number(self):
        user = users_factories.UserFactory(activity="Etudiant", postalCode="75001", idPieceNumber=None)
        dms_data = fraud_factories.DMSContentFactory(id_piece_number="140 767100 016")

        users_api.update_user_information_from_external_source(user, dms_data)
        assert user.idPieceNumber == "140767100016"

    @override_features(ENABLE_PHONE_VALIDATION=True)
    def test_phone_number_does_not_update(self):
        user = users_factories.UserFactory(phoneNumber="+33611111111")
        dms_data = fraud_factories.DMSContentFactory(phoneNumber="+33622222222")

        users_api.update_user_information_from_external_source(user, dms_data)

        assert user.phoneNumber == "+33611111111"

    @override_features(ENABLE_PHONE_VALIDATION=False)
    def test_phone_number_does_not_update_if_not_empty(self):
        user = users_factories.UserFactory(phoneNumber="+33611111111")
        dms_data = fraud_factories.DMSContentFactory(phone="+33622222222")

        users_api.update_user_information_from_external_source(user, dms_data)

        assert user.phoneNumber == "+33611111111"

    def test_incomplete_data(self):
        user = users_factories.UserFactory(firstName="Julie")
        dms_data = fraud_factories.DMSContentFactory(birth_date=None)

        with pytest.raises(users_exceptions.IncompleteDataException):
            users_api.update_user_information_from_external_source(user, dms_data)

        assert user.firstName == "Julie"

    def should_not_update_date_of_birth_if_already_validated(self):
        # Given
        user = users_factories.UserFactory(
            dateOfBirth=datetime.date(2000, 1, 1),
            validatedBirthDate=datetime.date(2000, 1, 1),
        )

        # When
        users_api.update_user_information_from_external_source(user, fraud_factories.DMSContentFactory())

        # Then
        assert user.birth_date == datetime.date(2000, 1, 1)


class UpdateUserLastConnectionDateTest:
    @freeze_time("2021-9-20 11:11:11")
    def test_first_update(self):
        user = users_factories.UserFactory()

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime.datetime(2021, 9, 20, 11, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 1

    @freeze_time("2021-9-20 01:11:11")
    def test_update_day_after(self):
        user = users_factories.UserFactory(lastConnectionDate=datetime.datetime(2021, 9, 19, 23, 00, 11))

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime.datetime(2021, 9, 20, 1, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 1

    @freeze_time("2021-9-20 11:11:11")
    def test_update_same_day(self):
        user = users_factories.UserFactory(lastConnectionDate=datetime.datetime(2021, 9, 20, 9, 0))

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime.datetime(2021, 9, 20, 11, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 0

    @freeze_time("2021-9-20 11:11:11")
    def test_no_update(self):
        user = users_factories.UserFactory(lastConnectionDate=datetime.datetime(2021, 9, 20, 11, 00, 11))

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime.datetime(2021, 9, 20, 11, 00, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 0


class GetEligibilityTest:
    def test_get_eligibility_at_date_timezones_tolerance(self):
        date_of_birth = datetime.datetime(2000, 2, 1, 0, 0)

        specified_date = datetime.datetime(2019, 2, 1, 8, 0)
        assert users_api.get_eligibility_at_date(date_of_birth, specified_date) == users_models.EligibilityType.AGE18

        specified_date = datetime.datetime(2019, 2, 1, 12, 0)
        assert users_api.get_eligibility_at_date(date_of_birth, specified_date) is None


class UserEmailValidationTest:
    def test_validate_pro_user_email_from_pro_ff_on(self):
        user_offerer = offerers_factories.UserOffererFactory(
            user__validationToken="token", user__isEmailValidated=False
        )

        users_api.validate_pro_user_email(user_offerer.user)

        assert history_models.ActionHistory.query.count() == 0
        assert user_offerer.user.validationToken is None
        assert user_offerer.user.isEmailValidated is True
        assert len(mails_testing.outbox) == 0

    def test_validate_pro_user_email_from_backoffice_ff_on(self):
        backoffice_user = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserOffererFactory(
            user__validationToken="token", user__isEmailValidated=False
        )

        users_api.validate_pro_user_email(user_offerer.user, backoffice_user)

        assert history_models.ActionHistory.query.count() == 1
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_EMAIL_VALIDATED
        assert action.user == user_offerer.user
        assert action.authorUser == backoffice_user

        assert user_offerer.user.validationToken is None
        assert user_offerer.user.isEmailValidated is True
        assert len(mails_testing.outbox) == 0


class SaveFlagsTest:
    def test_new_firebase_flags(self):
        user = users_factories.UserFactory()

        users_api.save_flags(user, {"firebase": {"BETTER_OFFER_CREATION": "true"}})

        assert user.pro_flags.firebase == {"BETTER_OFFER_CREATION": "true"}

    def test_same_pre_existing_firebase_flags(self, caplog):
        flags = users_factories.UserProFlagsFactory()
        user = flags.user

        users_api.save_flags(user, {"firebase": {"BETTER_OFFER_CREATION": "true"}})
        assert user.pro_flags.firebase == {"BETTER_OFFER_CREATION": "true"}
        assert not caplog.messages

    def test_different_pre_existing_firebase_flags(self, caplog):
        flags = users_factories.UserProFlagsFactory()
        user = flags.user

        users_api.save_flags(user, {"firebase": {"BETTER_OFFER_CREATION": "false"}})

        assert user.pro_flags.firebase == {"BETTER_OFFER_CREATION": "false"}
        assert caplog.messages == [f"{user} now has different Firebase flags than before"]

    def test_unknown_flags(self):
        flags = users_factories.UserProFlagsFactory()
        user = flags.user

        with pytest.raises(ValueError):
            users_api.save_flags(user, {"uknown": {"toto": 10}})


class SearchPublicAccountTest:
    def test_current_email(self):
        user = users_factories.BeneficiaryGrant18Factory(email="current@email.com")
        users_factories.EmailValidationEntryFactory(user=user)

        query = users_api.search_public_account("current@email.com")
        users = query.all()

        assert len(users) == 1
        assert users[0].id == user.id

    def test_current_domain(self):
        user = users_factories.BeneficiaryGrant18Factory(email="current@domain.com")
        users_factories.EmailValidationEntryFactory(user=user)

        query = users_api.search_public_account("@domain.com")
        users = query.all()

        assert len(users) == 1
        assert users[0].id == user.id

    def test_email_not_in_known_users(self):
        users_factories.BeneficiaryGrant18Factory(email="current@domain.com")

        query = users_api.search_public_account("another@email.com")

        assert not query.all()

    def test_domain_not_in_known_users(self):
        users_factories.BeneficiaryGrant18Factory(email="current@domain.com")

        query = users_api.search_public_account("@email.com")

        assert not query.all()

    def test_old_email(self):
        event = users_factories.EmailValidationEntryFactory()
        event.user.email = event.newEmail

        query = users_api.search_public_account_in_history_email(event.oldEmail)
        users = query.all()

        assert len(users) == 1
        assert users[0].id == event.user.id

    def test_old_domain(self):
        user = users_factories.BeneficiaryGrant18Factory(email="current@domain.com")
        event = users_factories.EmailValidationEntryFactory(user=user)

        query = users_api.search_public_account_in_history_email(f"@{event.oldDomainEmail}")
        users = query.all()

        assert len(users) == 1
        assert users[0].id == user.id

    def test_old_email_but_not_validated(self):
        user = users_factories.BeneficiaryGrant18Factory(email="current@domain.com")
        event = users_factories.EmailUpdateEntryFactory(user=user)
        # ensure that the current email is different from the event's
        # old one
        event.user.email = event.newEmail

        query = users_api.search_public_account_in_history_email(event.oldEmail)
        assert not query.all()

    def test_unknown_email(self):
        query = users_api.search_public_account("no@user.com")
        assert not query.all()

    def test_unknown_email_in_history_email(self):
        query = users_api.search_public_account_in_history_email("no@user.com")
        assert not query.all()


class SaveTrustedDeviceTest:
    def should_not_save_trusted_device_when_no_device_id_provided(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="",
            source="iPhone 13",
            os="iOS",
        )

        users_api.save_trusted_device(device_info=device_info, user=user)

        assert users_models.TrustedDevice.query.count() == 0

    def test_can_save_trusted_device(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
            source="iPhone 13",
            os="iOS",
        )

        users_api.save_trusted_device(device_info=device_info, user=user)

        trusted_device = users_models.TrustedDevice.query.one()

        assert trusted_device.deviceId == device_info.device_id
        assert trusted_device.source == "iPhone 13"
        assert trusted_device.os == "iOS"

    def test_can_access_trusted_devices_from_user(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
            source="iPhone 13",
            os="iOS",
        )

        users_api.save_trusted_device(device_info=device_info, user=user)

        trusted_device = users_models.TrustedDevice.query.one()

        assert user.trusted_devices == [trusted_device]

    def should_log_when_no_device_id(self, caplog):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="",
            source="iPhone 13",
            os="iOS",
        )

        with caplog.at_level(logging.INFO):
            users_api.save_trusted_device(device_info=device_info, user=user)

        assert caplog.messages == ["Invalid deviceId was provided for trusted device"]
        assert caplog.records[0].extra == {
            "deviceId": "",
            "os": "iOS",
            "source": "iPhone 13",
        }


class UpdateLoginDeviceHistoryTest:
    def should_not_save_login_device_when_no_device_id_provided(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="",
            source="iPhone 13",
            os="iOS",
        )

        users_api.update_login_device_history(device_info=device_info, user=user)

        assert users_models.LoginDeviceHistory.query.count() == 0

    def test_can_save_login_device(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
            source="iPhone 13",
            os="iOS",
        )

        users_api.update_login_device_history(device_info=device_info, user=user)

        login_device = users_models.LoginDeviceHistory.query.one()

        assert login_device.deviceId == device_info.device_id
        assert login_device.source == "iPhone 13"
        assert login_device.os == "iOS"
        assert login_device.location is None

    def should_return_login_history(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
            source="iPhone 13",
            os="iOS",
        )

        login_history = users_api.update_login_device_history(device_info=device_info, user=user)

        login_device = users_models.LoginDeviceHistory.query.one()

        assert login_history == login_device

    def test_can_access_login_device_history_from_user(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
            source="iPhone 13",
            os="iOS",
        )

        users_api.update_login_device_history(device_info=device_info, user=user)

        login_device = users_models.LoginDeviceHistory.query.one()

        assert user.login_device_history == [login_device]

    def should_log_when_no_device_id(self, caplog):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="",
            source="iPhone 13",
            os="iOS",
        )

        with caplog.at_level(logging.INFO):
            users_api.update_login_device_history(device_info=device_info, user=user)

        assert caplog.messages == ["Invalid deviceId was provided for login device"]
        assert caplog.records[0].extra == {
            "deviceId": "",
            "os": "iOS",
            "source": "iPhone 13",
        }


class ShouldSaveLoginDeviceAsTrustedDeviceTest:
    device_info = account_serialization.TrustedDevice(
        deviceId="2E429592-2446-425F-9A62-D6983F375B3B", os="iOS", source="iPhone 13"
    )

    def should_be_false_when_no_device_id(self):
        user = users_factories.UserFactory()
        device_without_id = account_serialization.TrustedDevice(deviceId="", os="iOS", source="iPhone 13")

        assert users_api.should_save_login_device_as_trusted_device(device_info=device_without_id, user=user) is False

    def should_be_false_when_no_device_history_for_user(self):
        user = users_factories.UserFactory()

        assert users_api.should_save_login_device_as_trusted_device(device_info=self.device_info, user=user) is False

    def should_be_true_when_user_has_device_history_matching_device_id(self):
        user = users_factories.UserFactory()
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=user)

        assert users_api.should_save_login_device_as_trusted_device(device_info=self.device_info, user=user) is True

    def should_be_false_when_user_has_device_history_for_different_device(self):
        user = users_factories.UserFactory()
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=user)

        other_device_info = account_serialization.TrustedDevice(deviceId="other_id", os="iOS", source="iPhone 13")
        assert users_api.should_save_login_device_as_trusted_device(device_info=other_device_info, user=user) is False

    def should_be_false_when_device_id_matches_different_user(self):
        user = users_factories.UserFactory()
        second_user = users_factories.UserFactory(email="py2@test.com")
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=second_user)

        assert users_api.should_save_login_device_as_trusted_device(device_info=self.device_info, user=user) is False

    def should_be_true_when_device_id_matches_multiple_users_including_current_user(self):
        user = users_factories.UserFactory()
        second_user = users_factories.UserFactory(email="py2@test.com")
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=second_user)
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=user)

        assert users_api.should_save_login_device_as_trusted_device(device_info=self.device_info, user=user) is True

    def should_be_false_when_login_device_is_already_trusted_device(self):
        user = users_factories.UserFactory()
        users_factories.TrustedDeviceFactory(deviceId=self.device_info.device_id, user=user)
        users_factories.LoginDeviceHistoryFactory(deviceId=self.device_info.device_id, user=user)

        assert users_api.should_save_login_device_as_trusted_device(device_info=self.device_info, user=user) is False


class IsLoginDeviceTrustedDeviceTest:
    def should_not_be_trusted_when_user_has_no_trusted_device(self):
        user = users_factories.UserFactory()
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B", os="iOS", source="iPhone 13"
        )

        assert user.trusted_devices == []
        assert users_api.is_login_device_a_trusted_device(device_info=device_info, user=user) is False

    def should_not_be_trusted_when_no_device_info(self):
        user = users_factories.UserFactory()

        assert users_api.is_login_device_a_trusted_device(device_info=None, user=user) is False

    def should_not_be_trusted_when_no_device_id(self):
        user = users_factories.UserFactory()
        device_without_id = account_serialization.TrustedDevice(deviceId="", os="iOS", source="iPhone 13")

        assert users_api.is_login_device_a_trusted_device(device_info=device_without_id, user=user) is False

    def should_be_trusted_when_device_is_a_trusted_device(self):
        user = users_factories.UserFactory()
        trusted_device = users_factories.TrustedDeviceFactory(user=user)
        users_factories.TrustedDeviceFactory(deviceId="3A44812-5776-235D-8E31-G4361H987A1A", user=user)
        device_info = account_serialization.TrustedDevice(
            deviceId=trusted_device.deviceId, os="iOS", source="iPhone 13"
        )

        assert users_api.is_login_device_a_trusted_device(device_info=device_info, user=user) is True

    def should_not_be_trusted_when_device_is_not_a_trusted_device(self):
        user = users_factories.UserFactory()
        users_factories.TrustedDeviceFactory(user=user)
        device_info = account_serialization.TrustedDevice(deviceId="other-device-id", os="iOS", source="iPhone 13")

        assert users_api.is_login_device_a_trusted_device(device_info=device_info, user=user) is False


class RecentSuspiciousLoginsTest:
    def should_ignore_trusted_device_logins(self):
        user = users_factories.UserFactory()
        trusted_device = users_factories.TrustedDeviceFactory(user=user)
        _trusted_login = users_factories.LoginDeviceHistoryFactory(user=user, deviceId=trusted_device.deviceId)

        assert not users_api.get_recent_suspicious_logins(user)

    def should_ignore_old_suspicious_device_logins(self):
        user = users_factories.UserFactory()
        _untrusted_login = users_factories.LoginDeviceHistoryFactory(
            user=user, dateCreated=datetime.datetime.utcnow() - relativedelta(hours=25)
        )

        assert not users_api.get_recent_suspicious_logins(user)

    def should_detect_suspicious_login(self):
        user = users_factories.UserFactory()
        untrusted_login = users_factories.LoginDeviceHistoryFactory(user=user)

        assert users_api.get_recent_suspicious_logins(user) == [untrusted_login]

    def should_detect_suspicious_login_before_trusted_device_addition(self):
        user = users_factories.UserFactory()
        untrusted_login = users_factories.LoginDeviceHistoryFactory(user=user)
        _trusted_device = users_factories.TrustedDeviceFactory(user=user, deviceId=untrusted_login.deviceId)

        assert users_api.get_recent_suspicious_logins(user) == [untrusted_login]


class CreateSuspiciousLoginEmailTokenTest:
    @freeze_time("2023-06-19 10:30:00")
    def should_encode_login_info_in_token(self):
        with mock.patch("flask.current_app.redis_client", fakeredis.FakeStrictRedis()):
            user = users_factories.UserFactory()
            login_info = users_models.LoginDeviceHistory(
                deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
                source="iPhone 13",
                os="iOS",
                location="Paris",
                dateCreated=datetime.datetime(2023, 6, 19, 10, 30),
            )

            token = users_api.create_suspicious_login_email_token(login_info, user.id)

            assert token.data == {
                "dateCreated": "2023-06-19T10:30:00.000000Z",
                "location": "Paris",
                "source": "iPhone 13",
                "os": "iOS",
            }
            assert token.get_expiration_date_from_token() == datetime.datetime(2023, 6, 26, 10, 30)

            assert token.user_id == user.id

    @freeze_time("2023-06-02 16:10:00")
    def should_encode_date_and_user_id_in_token_when_no_login_info(self):
        user = users_factories.UserFactory()

        token = users_api.create_suspicious_login_email_token(None, user.id)

        assert token.data == {
            "dateCreated": "2023-06-02T16:10:00.000000Z",
        }
        assert token.user_id == user.id


class DeleteOldTrustedDevicesTest:
    def should_delete_trusted_devices_older_than_five_years_ago(self):
        five_years_ago = datetime.datetime.utcnow() - relativedelta(years=5)
        six_years_ago = datetime.datetime.utcnow() - relativedelta(years=6)
        users_factories.TrustedDeviceFactory(dateCreated=five_years_ago)
        users_factories.TrustedDeviceFactory(dateCreated=six_years_ago)

        users_api.delete_old_trusted_devices()

        assert users_models.TrustedDevice.query.count() == 0

    def should_not_delete_trusted_devices_created_less_than_five_years_ago(self):
        less_than_five_years_ago = datetime.datetime.utcnow() - relativedelta(years=5) + datetime.timedelta(days=1)
        users_factories.TrustedDeviceFactory(dateCreated=less_than_five_years_ago)

        users_api.delete_old_trusted_devices()

        assert users_models.TrustedDevice.query.count() == 1


class DeleteOldLoginDeviceHistoryTest:
    def should_delete_device_history_older_than_thirteen_months_ago(self):
        thirteen_months_ago = datetime.datetime.utcnow() - relativedelta(months=13)
        fourteen_months_ago = datetime.datetime.utcnow() - relativedelta(months=14)
        users_factories.LoginDeviceHistoryFactory(dateCreated=thirteen_months_ago)
        users_factories.LoginDeviceHistoryFactory(dateCreated=fourteen_months_ago)

        users_api.delete_old_login_device_history()

        assert users_models.LoginDeviceHistory.query.count() == 0

    def should_not_delete_device_history_created_less_than_thirteen_months_ago(self):
        less_than_thirteen_months_ago = (
            datetime.datetime.utcnow() - relativedelta(months=13) + datetime.timedelta(days=1)
        )
        users_factories.LoginDeviceHistoryFactory(dateCreated=less_than_thirteen_months_ago)

        users_api.delete_old_login_device_history()

        assert users_models.LoginDeviceHistory.query.count() == 1


class RefreshAccessTokenTest:
    @override_features(WIP_ENABLE_TRUSTED_DEVICE=True, WIP_ENABLE_SUSPICIOUS_EMAIL_SEND=True)
    def should_create_access_token_with_default_lifetime_when_no_device_info(self):
        user = users_factories.UserFactory()

        refresh_token = users_api.create_user_refresh_token(user=user, device_info=None)
        decoded_refresh_token = decode_token(refresh_token)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=True, WIP_ENABLE_SUSPICIOUS_EMAIL_SEND=True)
    def should_create_access_token_with_default_lifetime_when_device_is_not_a_trusted_device(self):
        user = users_factories.UserFactory()
        users_factories.TrustedDeviceFactory(user=user)
        other_device = account_serialization.TrustedDevice(deviceId="other-device-id", os="iOS", source="iPhone 13")

        refresh_token = users_api.create_user_refresh_token(user=user, device_info=other_device)
        decoded_refresh_token = decode_token(refresh_token)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=True, WIP_ENABLE_SUSPICIOUS_EMAIL_SEND=True)
    def should_create_access_token_with_extended_lifetime_when_device_is_a_trusted_device(self):
        user = users_factories.UserFactory()
        trusted_device = users_factories.TrustedDeviceFactory(user=user)
        device_info = account_serialization.TrustedDevice(
            deviceId=trusted_device.deviceId, os="iOS", source="iPhone 13"
        )

        refresh_token = users_api.create_user_refresh_token(user=user, device_info=device_info)
        decoded_refresh_token = decode_token(refresh_token)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXTENDED_EXPIRES

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=True)
    def should_create_access_token_with_default_lifetime_when_device_is_a_trusted_device_and_suspicious_email_feature_flag_is_disabled(
        self,
    ):
        user = users_factories.UserFactory()
        trusted_device = users_factories.TrustedDeviceFactory(user=user)

        refresh_token = users_api.create_user_refresh_token(user=user, device_info=trusted_device)
        decoded_refresh_token = decode_token(refresh_token)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES

    @override_features(WIP_ENABLE_SUSPICIOUS_EMAIL_SEND=True)
    def should_create_access_token_with_default_lifetime_when_device_is_a_trusted_device_and_trusted_device_feature_flag_is_disabled(
        self,
    ):
        user = users_factories.UserFactory()
        trusted_device = users_factories.TrustedDeviceFactory(user=user)

        refresh_token = users_api.create_user_refresh_token(user=user, device_info=trusted_device)
        decoded_refresh_token = decode_token(refresh_token)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES


class NotifyUserBeforeDeletionUponSuspensionTest:
    def test_get_users_with_suspended_account_to_notify(self):
        delta_time = 5
        exact_time = datetime.datetime.utcnow() - datetime.timedelta(days=delta_time)
        suspension_to_be_detected = history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        # not suspended upon user request: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        # suspended one day after: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time + datetime.timedelta(days=1),
            reason=users_constants.SuspensionReason.UPON_USER_REQUEST,
        )

        # suspended one day before: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time - datetime.timedelta(days=1),
            reason=users_constants.SuspensionReason.UPON_USER_REQUEST,
        )

        # should not be notified because unsuspended
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )
        history_factories.UnsuspendedUserActionHistoryFactory(user=user, actionDate=datetime.datetime.utcnow())

        expected_user_ids = {suspension_to_be_detected.userId}

        with assert_num_queries(1):
            query = users_api._get_users_with_suspended_account_to_notify(delta_time)
            user_ids = {user.id for user in query}
            assert user_ids == expected_user_ids

    def test_notify_user_before_deletion_upon_suspension(self, app):
        # given
        exact_time = datetime.datetime.utcnow() - datetime.timedelta(
            days=settings.DELETE_SUSPENDED_ACCOUNTS_SINCE - settings.NOTIFY_X_DAYS_BEFORE_DELETION
        )
        suspension_to_be_detected = history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        # not suspended upon user request: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        # suspended one day after: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time + datetime.timedelta(days=1),
            reason=users_constants.SuspensionReason.UPON_USER_REQUEST,
        )

        # suspended one day before: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=exact_time - datetime.timedelta(days=1),
            reason=users_constants.SuspensionReason.UPON_USER_REQUEST,
        )

        # should not be notified because unsuspended
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )
        history_factories.UnsuspendedUserActionHistoryFactory(user=user, actionDate=datetime.datetime.utcnow())

        # when
        users_api.notify_users_before_deletion_of_suspended_account()

        # then
        user = users_models.User.query.get(suspension_to_be_detected.userId)
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["params"]["FIRSTNAME"] == user.firstName
        assert mails_testing.outbox[0].sent_data["To"] == user.email

    def test_multiple_suspensions_different_reason(self):
        exact_time = datetime.datetime.utcnow() - datetime.timedelta(
            days=settings.DELETE_SUSPENDED_ACCOUNTS_SINCE - settings.NOTIFY_X_DAYS_BEFORE_DELETION
        )
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )
        history_factories.UnsuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time + datetime.timedelta(minutes=1)
        )
        history_factories.SuspendedUserActionHistoryFactory(
            user=user,
            actionDate=exact_time + datetime.timedelta(minutes=2),
            reason=users_constants.SuspensionReason.FRAUD_SUSPICION,
        )

        # when
        users_api.notify_users_before_deletion_of_suspended_account()

        # then
        assert len(mails_testing.outbox) == 0

    def test_multiple_suspensions_different_date(self):
        exact_time = datetime.datetime.utcnow() - datetime.timedelta(
            days=settings.DELETE_SUSPENDED_ACCOUNTS_SINCE - settings.NOTIFY_X_DAYS_BEFORE_DELETION
        )
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )
        history_factories.UnsuspendedUserActionHistoryFactory(
            user=user, actionDate=exact_time + datetime.timedelta(minutes=1)
        )
        history_factories.SuspendedUserActionHistoryFactory(
            user=user,
            actionDate=exact_time + datetime.timedelta(days=1),
            reason=users_constants.SuspensionReason.UPON_USER_REQUEST,
        )

        # when
        users_api.notify_users_before_deletion_of_suspended_account()

        # then
        assert len(mails_testing.outbox) == 0


@pytest.mark.usefixtures("db_session")
class GetSuspendedAccountsUponUserRequestSinceTest:
    def test_get_suspended_upon_user_request_accounts_since(self) -> None:
        one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        something = history_factories.SuspendedUserActionHistoryFactory(
            actionDate=one_week_ago, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        # not suspended upon user request: should be ignored
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=one_week_ago, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        # suspended less than 5 days ago (see below): should be ignored
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        history_factories.SuspendedUserActionHistoryFactory(
            actionDate=yesterday, reason=users_constants.SuspensionReason.UPON_USER_REQUEST
        )

        expected_user_ids = {something.userId}

        with assert_num_queries(1):
            query = users_api.get_suspended_upon_user_request_accounts_since(5)
            user_ids = {user.id for user in query}
            assert user_ids == expected_user_ids

    def test_unsuspended_account(self) -> None:
        """
        Test that an unsuspended account is ignored, even if the
        suspension event occurred more than N days ago.
        """
        one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, actionDate=one_week_ago, reason=users_constants.SuspensionReason.FRAUD_SUSPICION
        )

        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        history_factories.UnsuspendedUserActionHistoryFactory(user=user, actionDate=yesterday)

        with assert_num_queries(1):
            assert not list(users_api.get_suspended_upon_user_request_accounts_since(5))


class AnonymizeNonProNonBeneficiaryUsersTest:
    def import_iris(self):
        path = DATA_DIR / "iris_min.7z"
        geography_api.import_iris_from_7z(str(path))

    def test_anonymize_non_pro_non_beneficiary_users(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=((3 * 365) + 1)),
            validatedBirthDate=datetime.date.today(),
        )
        user_too_new = users_factories.UserFactory(
            firstName="user_too_new",
            lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=((3 * 365) - 1)),
        )
        user_never_connected = users_factories.UserFactory(firstName="user_never_connected", lastConnectionDate=None)
        user_beneficiary = users_factories.BeneficiaryGrant18Factory(
            firstName="user_beneficiary",
        )
        user_underage_beneficiary = users_factories.UnderageBeneficiaryFactory(
            firstName="user_underage_beneficiary",
        )
        user_pro = users_factories.ProFactory(
            firstName="user_pro",
        )
        user_pass_culture = users_factories.ProFactory(
            firstName="user_pass_culture", email="user_pass_culture@passculture.app"
        )
        user_anonymized = users_factories.ProFactory(
            firstName="user_anonymized", email="user_anonymized@anonymized.passculture"
        )

        self.import_iris()
        iris = geography_models.IrisFrance.query.first()

        with mock.patch("pcapi.core.users.api.get_iris_from_address", return_value=iris):
            users_api.anonymize_non_pro_non_beneficiary_users(force=False)

        db.session.refresh(user_to_anonymize)
        db.session.refresh(user_too_new)
        db.session.refresh(user_never_connected)
        db.session.refresh(user_beneficiary)
        db.session.refresh(user_underage_beneficiary)
        db.session.refresh(user_pro)
        db.session.refresh(user_pass_culture)
        db.session.refresh(user_anonymized)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert len(batch_testing.requests) == 1
        assert batch_testing.requests[0]["user_id"] == user_to_anonymize.id

        # these profiles should not have been anonymized
        assert user_too_new.firstName == "user_too_new"
        assert user_never_connected.firstName == "user_never_connected"
        assert user_beneficiary.firstName == "user_beneficiary"
        assert user_underage_beneficiary.firstName == "user_underage_beneficiary"
        assert user_pro.firstName == "user_pro"
        assert user_pass_culture.firstName == "user_pass_culture"
        assert user_anonymized.firstName == "user_anonymized"

        # only one profile should have been anonymized
        for beneficiary_fraud_check in user_to_anonymize.beneficiaryFraudChecks:
            assert beneficiary_fraud_check.resultContent == None
            assert beneficiary_fraud_check.reason == "Anonymized"
            assert beneficiary_fraud_check.dateCreated.day == 1
            assert beneficiary_fraud_check.dateCreated.month == 1
            assert beneficiary_fraud_check.updatedAt.day == 1
            assert beneficiary_fraud_check.updatedAt.month == 1

        for beneficiary_fraud_review in user_to_anonymize.beneficiaryFraudReviews:
            assert beneficiary_fraud_review.reason == "Anonymized"
            assert beneficiary_fraud_review.dateReviewed.day == 1
            assert beneficiary_fraud_review.dateReviewed.month == 1

        assert user_to_anonymize.email == f"anonymous_{user_to_anonymize.id}@anonymized.passculture"
        assert user_to_anonymize.password == b"Anonymized"
        assert user_to_anonymize.firstName == f"Anonymous_{user_to_anonymize.id}"
        assert user_to_anonymize.lastName == f"Anonymous_{user_to_anonymize.id}"
        assert user_to_anonymize.married_name == None
        assert user_to_anonymize.postalCode == None
        assert user_to_anonymize.phoneNumber == None
        assert user_to_anonymize.dateOfBirth.day == 1
        assert user_to_anonymize.dateOfBirth.month == 1
        assert user_to_anonymize.address == None
        assert user_to_anonymize.city == None
        assert user_to_anonymize.externalIds == []
        assert user_to_anonymize.idPieceNumber == None
        assert user_to_anonymize.login_device_history == []
        assert user_to_anonymize.user_email_history == []
        assert user_to_anonymize.isActive == False
        assert user_to_anonymize.irisFrance == iris
        assert user_to_anonymize.validatedBirthDate.day == 1
        assert user_to_anonymize.validatedBirthDate.month == 1
        assert user_to_anonymize.roles == [users_models.UserRole.ANONYMIZED]
        assert user_to_anonymize.login_device_history == []
        assert user_to_anonymize.trusted_devices == []
        assert len(user_to_anonymize.action_history) == 1
        assert user_to_anonymize.action_history[0].actionType == history_models.ActionType.USER_ANONYMIZED
        assert user_to_anonymize.action_history[0].authorUserId == None
        assert user_to_anonymize.action_history[0].actionType == history_models.ActionType.USER_ANONYMIZED

    def test_anonymize_non_pro_non_beneficiary_user_force_iris_not_found(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=((3 * 365) + 1)),
        )

        users_api.anonymize_non_pro_non_beneficiary_users(force=True)

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert len(batch_testing.requests) == 1
        assert batch_testing.requests[0]["user_id"] == user_to_anonymize.id
        assert user_to_anonymize.firstName == f"Anonymous_{user_to_anonymize.id}"

    def test_anonymize_non_pro_non_beneficiary_user_keep_history_on_offere(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=((3 * 365) + 1)),
        )
        history_factories.ActionHistoryFactory(
            authorUser=user_to_anonymize,
            user=user_to_anonymize,
            offerer=offerers_factories.OffererFactory(),
            actionType=history_models.ActionType.OFFERER_VALIDATED,
        )

        users_api.anonymize_non_pro_non_beneficiary_users(force=True)

        db.session.refresh(user_to_anonymize)

        assert user_to_anonymize.firstName == f"Anonymous_{user_to_anonymize.id}"
        assert (
            history_models.ActionHistory.query.filter(
                history_models.ActionHistory.userId == user_to_anonymize.id
            ).count()
            == 2
        )

    def test_anonymize_non_pro_non_beneficiary_user_iris_not_found(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=((3 * 365) + 1)),
        )

        users_api.anonymize_non_pro_non_beneficiary_users(force=False)

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_to_anonymize.firstName == "user_to_anonymize"

    def test_anonymize_non_pro_non_beneficiary_user_no_addr_api(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=((3 * 365) + 1)),
        )

        users_api.anonymize_non_pro_non_beneficiary_users(force=False)
        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_to_anonymize.firstName == "user_to_anonymize"

    def test_anonymize_non_pro_non_beneficiary_user_keep_email_in_brevo_if_used_for_venue(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=((3 * 365) + 1)),
        )
        offerers_factories.VenueFactory(bookingEmail=user_to_anonymize.email)

        users_api.anonymize_non_pro_non_beneficiary_users(force=True)
        db.session.refresh(user_to_anonymize)

        assert user_to_anonymize.firstName == f"Anonymous_{user_to_anonymize.id}"
        assert user_to_anonymize.email == f"anonymous_{user_to_anonymize.id}@anonymized.passculture"
        assert sendinblue_testing.sendinblue_requests[0]["attributes"]["FIRSTNAME"] == ""
