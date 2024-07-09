import dataclasses
import datetime
from decimal import Decimal
import json
import logging
import os
import pathlib
from unittest import mock
import zipfile

from dateutil.relativedelta import relativedelta
import fakeredis
from flask import current_app
from flask_jwt_extended.utils import decode_token
import pytest
import time_machine

from pcapi import settings
from pcapi.core import token as token_utils
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories_v2
from pcapi.core.finance import enum as finance_enum
from pcapi.core.finance import models as finance_models
import pcapi.core.finance.conf as finance_conf
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.geography import api as geography_api
from pcapi.core.geography import models as geography_models
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
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
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.notifications.push import testing as batch_testing
from pcapi.routes.native.v1.serialization import account as account_serialization
from pcapi.routes.serialization import users as users_serialization

import tests
from tests.test_utils import StorageFolderManager


DATA_DIR = pathlib.Path(tests.__path__[0]) / "files"
pytestmark = pytest.mark.usefixtures("db_session")


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

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert sendinblue_testing.sendinblue_requests[0]["email"] == user.email
        assert sendinblue_testing.sendinblue_requests[0]["action"] == "delete"

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

        assert len(sendinblue_testing.sendinblue_requests) == 2
        # update venue attributes after booking is canceled
        assert sendinblue_testing.sendinblue_requests[0]["email"] == cancellable_booking.venue.bookingEmail
        assert len(sendinblue_testing.sendinblue_requests[0]["attributes"]) > 0
        # delete suspended user contact
        assert sendinblue_testing.sendinblue_requests[1]["email"] == user.email
        assert sendinblue_testing.sendinblue_requests[1]["action"] == "delete"

    def test_suspend_pro(self):
        booking = bookings_factories.BookingFactory()
        pro = offerers_factories.UserOffererFactory(offerer=booking.offerer).user
        author = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.END_OF_CONTRACT

        users_api.suspend_account(pro, reason, author)

        assert not pro.isActive
        assert booking.status is BookingStatus.CONFIRMED  # not canceled

        history = history_models.ActionHistory.query.filter_by(userId=pro.id).all()
        assert len(history) == 1
        _assert_user_action_history_as_expected(
            history[0], pro, author, history_models.ActionType.USER_SUSPENDED, reason
        )

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert sendinblue_testing.sendinblue_requests[0]["email"] == pro.email
        assert sendinblue_testing.sendinblue_requests[0]["action"] == "delete"

    def test_suspend_pro_fraud_suspicion(self):
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

        assert len(sendinblue_testing.sendinblue_requests) == 3
        # update beneficiary and venue attributes after booking is canceled
        assert sendinblue_testing.sendinblue_requests[0]["email"] == booking.user.email
        assert len(sendinblue_testing.sendinblue_requests[0]["attributes"]) > 0
        assert sendinblue_testing.sendinblue_requests[1]["email"] == booking.venue.bookingEmail
        assert len(sendinblue_testing.sendinblue_requests[1]["attributes"]) > 0
        # delete suspended user contact
        assert sendinblue_testing.sendinblue_requests[2]["email"] == pro.email
        assert sendinblue_testing.sendinblue_requests[2]["action"] == "delete"

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

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert sendinblue_testing.sendinblue_requests[0]["email"] == user.email
        assert len(sendinblue_testing.sendinblue_requests[0]["attributes"]) > 0

    def should_send_reset_password_email_when_user_is_suspended_for_suspicious_login(self):
        user = users_factories.UserFactory(isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(
            user=user, reason=users_constants.SuspensionReason.SUSPICIOUS_LOGIN_REPORTED_BY_USER
        )
        author = users_factories.AdminFactory()

        users_api.unsuspend_account(user, author)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.NEW_PASSWORD_REQUEST_FOR_SUSPICIOUS_LOGIN.value
        )
        assert mails_testing.outbox[0]["params"]["RESET_PASSWORD_LINK"]

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
        users_factories.SingleSignOnFactory(user=user)
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
        assert users_models.SingleSignOn.query.filter_by(userId=reloaded_user.id).first() is None

        assert len(reloaded_user.email_history) == 1

        history = reloaded_user.email_history[0]
        assert history.oldEmail == self.old_email
        assert history.newEmail == self.new_email
        assert history.eventType == users_models.EmailHistoryEventTypeEnum.VALIDATION
        assert history.id is not None

    def test_change_user_email_new_email_already_existing(self):
        # Given
        user = users_factories.UserFactory(email=self.old_email, firstName="UniqueNameForEmailChangeTest")
        users_factories.SingleSignOnFactory(user=user)
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

        single_sign_on = users_models.SingleSignOn.query.filter(
            users_models.SingleSignOn.userId == user.id
        ).one_or_none()
        assert single_sign_on is not None

    def test_change_user_email_expired_token(self, app):
        # Given
        user = users_factories.UserFactory(email=self.old_email, firstName="UniqueNameForEmailChangeTest")
        users_factories.UserSessionFactory(user=user)
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            with time_machine.travel("2021-01-01"):
                token = self._init_token(user)

            # When
            with time_machine.travel("2021-01-03"):
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

    def test_apps_flyer_called_for_underage_beneficiary(self, requests_mock):
        apps_flyer_data = {
            "apps_flyer": {"user": "some-user-id", "platform": "ANDROID"},
            "firebase_pseudo_id": "firebase_pseudo_id",
        }
        user = users_factories.UserFactory(
            externalIds=apps_flyer_data, validatedBirthDate=datetime.date.today() - relativedelta(years=16, months=4)
        )
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        posted = requests_mock.post("https://api2.appsflyer.com/inappevent/app.passculture.webapp")
        user = subscription_api.activate_beneficiary_for_eligibility(
            user, fraud_check, users_models.EligibilityType.UNDERAGE
        )

        first_request, second_request, third_request = posted.request_history
        assert first_request.json() == {
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary",
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": "GRANT_15_17",
            },
        }
        assert second_request.json() == {
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary_underage",
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": "GRANT_15_17",
            },
        }
        assert third_request.json() == {
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary_16",
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": "GRANT_15_17",
            },
        }

        assert user.has_underage_beneficiary_role
        assert len(user.deposits) == 1

    def test_apps_flyer_called_for_eighteen_beneficiary(self, requests_mock):
        apps_flyer_data = {
            "apps_flyer": {"user": "some-user-id", "platform": "ANDROID"},
            "firebase_pseudo_id": "firebase_pseudo_id",
        }
        user = users_factories.UserFactory(externalIds=apps_flyer_data)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        posted = requests_mock.post("https://api2.appsflyer.com/inappevent/app.passculture.webapp")
        user = subscription_api.activate_beneficiary_for_eligibility(
            user, fraud_check, users_models.EligibilityType.AGE18
        )

        first_request, second_request = posted.request_history
        assert first_request.json() == {
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary",
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": "GRANT_18",
            },
        }
        assert second_request.json() == {
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary_18",
            "eventValue": {
                "af_user_id": str(user.id),
                "af_firebase_pseudo_id": "firebase_pseudo_id",
                "type": "GRANT_18",
            },
        }

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

    def test_15yo_that_started_at_14_is_activated(self):
        fifteen_years_and_one_week_ago = datetime.datetime.utcnow() - relativedelta(years=15, weeks=1)
        one_month_ago = datetime.datetime.utcnow() - relativedelta(months=1)

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
            user, author=user, first_name="Hubert", last_name="Bonisseur de la Bath", commit=False
        )
        assert modified_info.to_dict() == {
            "firstName": {"new_info": "Hubert", "old_info": "Noël"},
            "lastName": {"new_info": "Bonisseur de la Bath", "old_info": "Flantier"},
        }

    def test_update_user_info_also_updates_underage_deposit_expiration_date(self):
        # Given a user with an underage deposit
        underaged_beneficiary_birthday = datetime.datetime.utcnow() - relativedelta(years=17, months=4)
        underaged_beneficiary_expiration_date = underaged_beneficiary_birthday + relativedelta(
            years=18, hour=0, minute=0, second=0, microsecond=0
        )
        user = users_factories.BeneficiaryFactory(age=17)
        users_api.update_user_info(user, author=user, validated_birth_date=underaged_beneficiary_birthday)

        assert user.deposits[0].expirationDate == underaged_beneficiary_expiration_date


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

        with time_machine.travel(
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
        "firstName": "Jean",
        "lastName": "Test",
        "password": "P@ssword12345",
        "phoneNumber": "0666666666",
        "contactOk": False,
        "token": "token",
    }

    def test_create_pro_user(self):
        pro_user_creation_body = users_serialization.ProUserCreationBodyV2Model(**self.data)

        pro_user = users_api.create_pro_user(pro_user_creation_body)

        assert pro_user.email == "prouser@example.com"
        assert not pro_user.has_admin_role
        assert not pro_user.needsToFillCulturalSurvey
        assert not pro_user.has_pro_role
        assert not pro_user.has_admin_role
        assert not pro_user.has_beneficiary_role
        assert not pro_user.deposits

    @override_settings(MAKE_PROS_BENEFICIARIES_IN_APP=True)
    def test_create_pro_user_in_integration(self):
        pro_user_creation_body = users_serialization.ProUserCreationBodyV2Model(**self.data)

        pro_user = users_api.create_pro_user(pro_user_creation_body)

        assert pro_user.email == "prouser@example.com"
        assert not pro_user.has_admin_role
        assert not pro_user.needsToFillCulturalSurvey
        assert not pro_user.has_pro_role
        assert not pro_user.has_admin_role
        assert pro_user.has_beneficiary_role
        assert pro_user.deposits


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
    @time_machine.travel("2021-9-20 11:11:11", tick=False)
    def test_first_update(self):
        user = users_factories.UserFactory()

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime.datetime(2021, 9, 20, 11, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 1

    @time_machine.travel("2021-9-20 01:11:11", tick=False)
    def test_update_day_after(self):
        user = users_factories.UserFactory(lastConnectionDate=datetime.datetime(2021, 9, 19, 23, 00, 11))

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime.datetime(2021, 9, 20, 1, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 1

    @time_machine.travel("2021-9-20 11:11:11", tick=False)
    def test_update_same_day(self):
        user = users_factories.UserFactory(lastConnectionDate=datetime.datetime(2021, 9, 20, 9, 0))

        users_api.update_last_connection_date(user)

        db.session.refresh(user)

        assert user.lastConnectionDate == datetime.datetime(2021, 9, 20, 11, 11, 11)
        assert len(sendinblue_testing.sendinblue_requests) == 0

    @time_machine.travel("2021-9-20 11:11:11", tick=False)
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
        user_offerer = offerers_factories.UserOffererFactory(user__isEmailValidated=False)

        users_api.validate_pro_user_email(user_offerer.user)

        assert history_models.ActionHistory.query.count() == 0
        assert user_offerer.user.isEmailValidated is True
        assert len(mails_testing.outbox) == 0

    def test_validate_pro_user_email_from_backoffice_ff_on(self):
        backoffice_user = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserOffererFactory(user__isEmailValidated=False)

        users_api.validate_pro_user_email(user_offerer.user, backoffice_user)

        assert history_models.ActionHistory.query.count() == 1
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_EMAIL_VALIDATED
        assert action.user == user_offerer.user
        assert action.authorUser == backoffice_user

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
    @time_machine.travel("2023-06-19 10:30:00", tick=False)
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

    @time_machine.travel("2023-06-02 16:10:00", tick=False)
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
    def should_create_access_token_with_default_lifetime_when_no_device_info(self):
        user = users_factories.UserFactory()

        refresh_token = users_api.create_user_refresh_token(user=user, device_info=None)
        decoded_refresh_token = decode_token(refresh_token)

        token_issue_date = decoded_refresh_token["iat"]
        token_expiration_date = decoded_refresh_token["exp"]
        refresh_token_lifetime = token_expiration_date - token_issue_date

        assert refresh_token_lifetime == settings.JWT_REFRESH_TOKEN_EXPIRES

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

    @override_features(WIP_ENABLE_SUSPICIOUS_EMAIL_SEND=False)
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

    @override_features(WIP_ENABLE_TRUSTED_DEVICE=False)
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
        assert mails_testing.outbox[0]["params"]["FIRSTNAME"] == user.firstName
        assert mails_testing.outbox[0]["To"] == user.email

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
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            validatedBirthDate=datetime.date.today(),
        )
        user_too_new = users_factories.UserFactory(
            firstName="user_too_new",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=-11),
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
        assert user_to_anonymize.irisFrance == iris
        assert user_to_anonymize.validatedBirthDate.day == 1
        assert user_to_anonymize.validatedBirthDate.month == 1
        assert user_to_anonymize.roles == [users_models.UserRole.ANONYMIZED]
        assert user_to_anonymize.login_device_history == []
        assert user_to_anonymize.trusted_devices == []
        assert len(user_to_anonymize.action_history) == 1
        assert user_to_anonymize.action_history[0].actionType == history_models.ActionType.USER_ANONYMIZED
        assert user_to_anonymize.action_history[0].authorUserId == None

    def test_anonymize_non_pro_non_beneficiary_user_force_iris_not_found(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
        )

        users_api.anonymize_non_pro_non_beneficiary_users(force=True)

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert len(batch_testing.requests) == 1
        assert batch_testing.requests[0]["user_id"] == user_to_anonymize.id
        assert user_to_anonymize.firstName == f"Anonymous_{user_to_anonymize.id}"

    def test_anonymize_non_pro_non_beneficiary_user_keep_history_on_offerer(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
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
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
        )

        users_api.anonymize_non_pro_non_beneficiary_users(force=False)

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_to_anonymize.firstName == "user_to_anonymize"

    def test_anonymize_non_pro_non_beneficiary_user_no_addr_api(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
        )

        users_api.anonymize_non_pro_non_beneficiary_users(force=False)
        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_to_anonymize.firstName == "user_to_anonymize"

    def test_anonymize_non_pro_non_beneficiary_user_keep_email_in_brevo_if_used_for_venue(self) -> None:
        user_to_anonymize = users_factories.UserFactory(
            firstName="user_to_anonymize",
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
        )
        offerers_factories.VenueFactory(bookingEmail=user_to_anonymize.email)

        users_api.anonymize_non_pro_non_beneficiary_users(force=True)
        db.session.refresh(user_to_anonymize)

        assert user_to_anonymize.firstName == f"Anonymous_{user_to_anonymize.id}"
        assert user_to_anonymize.email == f"anonymous_{user_to_anonymize.id}@anonymized.passculture"
        assert sendinblue_testing.sendinblue_requests[0]["attributes"]["FIRSTNAME"] == ""


class AnonymizeProUserTest:
    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_anonymize_pro_user(self, delete_beamer_user_mock):
        user_offerer_to_delete = offerers_factories.UserOffererFactory(
            user__lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=(365 * 3 + 1)),
        )
        user_offerer_to_keep = offerers_factories.UserOffererFactory(
            offerer=user_offerer_to_delete.offerer,
            user__lastConnectionDate=datetime.datetime.utcnow(),
        )
        user_id = user_offerer_to_delete.user.id
        users_api.anonymize_pro_users()

        assert users_models.User.query.filter_by(id=user_id).count() == 0
        assert users_models.User.query.filter_by(id=user_offerer_to_keep.user.id).count() == 1
        delete_beamer_user_mock.assert_called_once_with(user_id)

    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_keep_pro_users_with_activity_less_than_three_years(self, delete_beamer_user_mock):
        users_factories.ProFactory(
            lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=(365 * 3 - 1)),
            roles=[users_models.UserRole.NON_ATTACHED_PRO],
        )
        users_factories.ProFactory(
            lastConnectionDate=datetime.datetime.utcnow(), roles=[users_models.UserRole.NON_ATTACHED_PRO]
        )

        users_api.anonymize_pro_users()

        assert users_models.User.query.count() == 2
        delete_beamer_user_mock.assert_not_called()

    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_keep_last_user_in_offerer(self, delete_beamer_user_mock):
        user_offerer_to_delete = offerers_factories.UserOffererFactory(
            user__lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=(365 * 3 + 1)),
        )
        user_id = user_offerer_to_delete.user.id
        users_api.anonymize_pro_users()

        assert users_models.User.query.filter_by(id=user_id).count() == 1
        delete_beamer_user_mock.assert_not_called()

    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_anonymize_non_attached_pro_user(self, delete_beamer_user_mock):
        user_to_delete = users_factories.ProFactory(
            lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=(365 * 3 + 1)),
            roles=[users_models.UserRole.NON_ATTACHED_PRO],
        )
        user_to_keep1 = users_factories.ProFactory(
            lastConnectionDate=datetime.datetime.utcnow(), roles=[users_models.UserRole.NON_ATTACHED_PRO]
        )
        user_to_keep2 = users_factories.ProFactory(
            roles=[users_models.UserRole.NON_ATTACHED_PRO],
        )
        user_id = user_to_delete.id
        users_api.anonymize_pro_users()

        assert users_models.User.query.filter_by(id=user_id).count() == 0
        assert users_models.User.query.filter_by(id=user_to_keep1.id).count() == 1
        assert users_models.User.query.filter_by(id=user_to_keep2.id).count() == 1
        delete_beamer_user_mock.assert_called_once_with(user_id)

    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_anonymize_invalid_attachement_pro_user(self, delete_beamer_user_mock):
        user_offerer_to_delete = offerers_factories.UserOffererFactory(
            validationStatus=ValidationStatus.PENDING,
            user__lastConnectionDate=datetime.datetime.utcnow() - datetime.timedelta(days=(365 * 3 + 1)),
        )
        user_offerer_to_keep = offerers_factories.UserOffererFactory(
            validationStatus=ValidationStatus.PENDING,
            user__lastConnectionDate=datetime.datetime.utcnow(),
        )
        user_id = user_offerer_to_delete.user.id
        users_api.anonymize_pro_users()

        assert users_models.User.query.filter_by(id=user_id).count() == 0
        assert users_models.User.query.filter_by(id=user_offerer_to_keep.userId).count() == 1
        delete_beamer_user_mock.assert_called_once_with(user_id)

    @mock.patch("pcapi.core.users.api.delete_beamer_user")
    def test_anonymize_non_attached_never_connected_pro(self, delete_beamer_user_mock):
        user_to_delete = users_factories.ProFactory(
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=(365 * 3 + 1))
        )
        user_to_keep = users_factories.ProFactory()
        user_id = user_to_delete.id
        users_api.anonymize_pro_users()

        assert users_models.User.query.filter_by(id=user_id).count() == 0
        assert users_models.User.query.filter_by(id=user_to_keep.id).count() == 1
        delete_beamer_user_mock.assert_called_once_with(user_id)


class AnonymizeBeneficiaryUsersTest:
    def import_iris(self):
        path = DATA_DIR / "iris_min.7z"
        geography_api.import_iris_from_7z(str(path))

    def test_anonymize_beneficiary_users(self) -> None:
        user_beneficiary_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_beneficiary_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )
        user_underage_beneficiary_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_underage_beneficiary_to_anonymize",
            age=17,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )
        user_too_new = users_factories.BeneficiaryFactory(
            firstName="user_too_new",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=-11),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )
        user_deposit_too_new = users_factories.BeneficiaryFactory(
            firstName="user_deposit_too_new",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=-11),
        )
        user_never_connected = users_factories.UserFactory(firstName="user_never_connected", lastConnectionDate=None)
        user_no_role = users_factories.UserFactory(
            firstName="user_no_role",
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
            users_api.anonymize_beneficiary_users(force=False)

        db.session.refresh(user_beneficiary_to_anonymize)
        db.session.refresh(user_underage_beneficiary_to_anonymize)
        db.session.refresh(user_too_new)
        db.session.refresh(user_deposit_too_new)
        db.session.refresh(user_never_connected)
        db.session.refresh(user_no_role)
        db.session.refresh(user_pro)
        db.session.refresh(user_pass_culture)
        db.session.refresh(user_anonymized)

        assert len(sendinblue_testing.sendinblue_requests) == 2
        assert len(batch_testing.requests) == 2
        user_id_set = set(request["user_id"] for request in batch_testing.requests)
        assert user_id_set == {user_beneficiary_to_anonymize.id, user_underage_beneficiary_to_anonymize.id}

        # these profiles should not have been anonymized
        assert user_too_new.firstName == "user_too_new"
        assert user_deposit_too_new.firstName == "user_deposit_too_new"
        assert user_never_connected.firstName == "user_never_connected"
        assert user_no_role.firstName == "user_no_role"
        assert user_pro.firstName == "user_pro"
        assert user_pass_culture.firstName == "user_pass_culture"
        assert user_anonymized.firstName == "user_anonymized"

        for user_to_anonymize in [user_beneficiary_to_anonymize, user_underage_beneficiary_to_anonymize]:
            for beneficiary_fraud_check in user_to_anonymize.beneficiaryFraudChecks:
                assert beneficiary_fraud_check.resultContent == None
                assert beneficiary_fraud_check.reason == "Anonymized"
                assert beneficiary_fraud_check.dateCreated.day == 1
                assert beneficiary_fraud_check.dateCreated.month == 1

            for beneficiary_fraud_review in user_to_anonymize.beneficiaryFraudReviews:
                assert beneficiary_fraud_review.reason == "Anonymized"
                assert beneficiary_fraud_review.dateReviewed.day == 1
                assert beneficiary_fraud_review.dateReviewed.month == 1

            for deposit in user_to_anonymize.deposits:
                assert deposit.source == "Anonymized"

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
            assert user_to_anonymize.irisFrance == iris
            assert user_to_anonymize.validatedBirthDate.day == 1
            assert user_to_anonymize.validatedBirthDate.month == 1
            assert user_to_anonymize.roles == [users_models.UserRole.ANONYMIZED]
            assert user_to_anonymize.login_device_history == []
            assert user_to_anonymize.trusted_devices == []
            assert len(user_to_anonymize.action_history) == 1
            assert user_to_anonymize.action_history[0].actionType == history_models.ActionType.USER_ANONYMIZED
            assert user_to_anonymize.action_history[0].authorUserId == None

    def test_anonymize_beneficiary_user_force_iris_not_found(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )

        users_api.anonymize_beneficiary_users(force=True)

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 1
        assert len(batch_testing.requests) == 1
        assert batch_testing.requests[0]["user_id"] == user_to_anonymize.id
        assert user_to_anonymize.firstName == f"Anonymous_{user_to_anonymize.id}"

    def test_anonymize_beneficiary_user_iris_not_found(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )

        users_api.anonymize_beneficiary_users(force=False)

        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_to_anonymize.firstName == "user_to_anonymize"

    def test_anonymize_beneficiary_user_no_addr_api(self) -> None:
        user_to_anonymize = users_factories.BeneficiaryFactory(
            firstName="user_to_anonymize",
            age=18,
            lastConnectionDate=datetime.datetime.utcnow() - relativedelta(years=3, days=1),
            deposit__expirationDate=datetime.datetime.utcnow() - relativedelta(years=5, days=1),
        )

        users_api.anonymize_beneficiary_users(force=False)
        db.session.refresh(user_to_anonymize)

        assert len(sendinblue_testing.sendinblue_requests) == 0
        assert user_to_anonymize.firstName == "user_to_anonymize"


class AnonymizeUserDepositsTest:
    def test_anonymize_user_deposits(self) -> None:
        now = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        user_recent_deposit = users_factories.BeneficiaryFactory(
            deposit__dateCreated=now - relativedelta(years=6),
            deposit__expirationDate=now - relativedelta(years=5, days=1),
        )
        user_old_deposit = users_factories.BeneficiaryFactory(
            deposit__dateCreated=now - relativedelta(years=11, days=1),
            deposit__expirationDate=now - relativedelta(years=10, days=1),
        )

        users_api.anonymize_user_deposits()

        db.session.refresh(user_recent_deposit)
        db.session.refresh(user_old_deposit)

        for deposit in user_recent_deposit.deposits:
            assert deposit.dateCreated == now - relativedelta(years=6)
            assert deposit.expirationDate == now - relativedelta(years=5, days=1)

        for deposit in user_old_deposit.deposits:
            assert deposit.dateCreated == now - relativedelta(years=11, day=1, month=1)
            assert deposit.expirationDate == now - relativedelta(years=10, day=1, month=1)


class EnableNewProNavTest:
    def test_user_without_new_nav_state_raises(self) -> None:
        user = users_factories.ProFactory()

        with pytest.raises(users_exceptions.ProUserNotEligibleForNewNav):
            users_api.enable_new_pro_nav(user)

    def test_user_with_new_nav_state_not_eligible_raises(self) -> None:
        pro_new_nav_state = users_factories.UserProNewNavStateFactory(eligibilityDate=None, newNavDate=None)

        with pytest.raises(users_exceptions.ProUserNotEligibleForNewNav):
            users_api.enable_new_pro_nav(pro_new_nav_state.user)

        assert not pro_new_nav_state.newNavDate

    def test_user_eligible_in_the_future_raises(self) -> None:
        pro_new_nav_state = users_factories.UserProNewNavStateFactory(
            eligibilityDate=datetime.datetime.utcnow() + datetime.timedelta(days=2), newNavDate=None
        )

        with pytest.raises(users_exceptions.ProUserNotYetEligibleForNewNav):
            users_api.enable_new_pro_nav(pro_new_nav_state.user)

        assert not pro_new_nav_state.newNavDate

    def test_user_eligible(self) -> None:
        pro_new_nav_state = users_factories.UserProNewNavStateFactory(
            eligibilityDate=datetime.datetime.utcnow() - datetime.timedelta(days=1), newNavDate=None
        )

        users_api.enable_new_pro_nav(pro_new_nav_state.user)

        assert pro_new_nav_state.newNavDate

    def test_user_already_with_new_nav_should_not_update_date(self) -> None:
        yesterday_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        pro_new_nav_state = users_factories.UserProNewNavStateFactory(
            eligibilityDate=yesterday_date - datetime.timedelta(days=2), newNavDate=yesterday_date
        )

        users_api.enable_new_pro_nav(pro_new_nav_state.user)

        assert pro_new_nav_state.newNavDate == yesterday_date


class DeleteGdprExtractTest(StorageFolderManager):
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER

    def test_nominal(self):
        # given
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=datetime.datetime.utcnow())
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        users_api.delete_gdpr_extract(extract.id)

        # then
        assert users_models.GdprUserDataExtract.query.count() == 0
        assert len(os.listdir(self.storage_folder)) == 0

    def test_extract_file_does_not_exists(self):
        # given
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(dateProcessed=datetime.datetime.utcnow())
        # when
        users_api.delete_gdpr_extract(extract.id)

        # then
        assert users_models.GdprUserDataExtract.query.count() == 0


class CleanGdprExtractTest(StorageFolderManager):
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER

    def test_delete_expired_extracts(self):
        # given
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateProcessed=datetime.datetime.utcnow() - datetime.timedelta(days=6),
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=8),
        )
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        users_api.clean_gdpr_extracts()
        # then
        assert users_models.GdprUserDataExtract.query.count() == 0
        assert len(os.listdir(self.storage_folder)) == 0

    def test_delete_extracts_files_not_in_db(self):
        # given
        with open(self.storage_folder / "1.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        users_api.clean_gdpr_extracts()
        # then
        assert len(os.listdir(self.storage_folder)) == 0

    def test_delete_expired_unprocessed_extracts(self):
        # given
        users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=8)
        )
        # when
        users_api.clean_gdpr_extracts()
        # then
        assert users_models.GdprUserDataExtract.query.count() == 0

    def test_keep_unexpired_extracts(self):
        # given
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateProcessed=datetime.datetime.utcnow() - datetime.timedelta(days=5),
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=6),
        )
        with open(self.storage_folder / f"{extract.id}.zip", "wb") as fp:
            fp.write(b"[personal data compressed with deflate]")
        # when
        users_api.clean_gdpr_extracts()
        # then
        assert users_models.GdprUserDataExtract.query.count() == 1
        assert len(os.listdir(self.storage_folder)) == 1


def generate_beneficiary():
    now = datetime.datetime(2024, 1, 1)
    user = users_factories.UserFactory(
        activity="Lycéen",
        address="123 rue du pass",
        civility="M.",
        city="Paris",
        culturalSurveyFilledDate=now,
        departementCode="75",
        dateCreated=now,
        dateOfBirth=datetime.datetime(2010, 1, 1),
        email="valid_email@example.com",
        firstName="Beneficiary",
        isActive=True,
        isEmailValidated=True,
        lastName="bénéficiaire",
        married_name="married_name",
        postalCode="75000",
        schoolType=users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL,
        validatedBirthDate=datetime.date(2010, 1, 1),
        notificationSubscriptions={
            "marketing_email": True,
            "marketing_push": False,
        },
        roles=[users_models.UserRole.BENEFICIARY],
    )
    users_factories.LoginDeviceHistoryFactory(
        dateCreated=now - datetime.timedelta(days=2),
        deviceId="anotsorandomdeviceid2",
        location="Lyon",
        source="phone1",
        os="oldOs",
        user=user,
    )
    users_factories.LoginDeviceHistoryFactory(
        dateCreated=now,
        deviceId="anotsorandomdeviceid",
        location="Paris",
        source="phone 2",
        os="os/2",
        user=user,
    )
    users_factories.EmailConfirmationEntryFactory(
        creationDate=now - datetime.timedelta(days=2),
        newUserEmail="intermediary",
        newDomainEmail="example.com",
        oldUserEmail="old",
        oldDomainEmail="example.com",
        user=user,
    )
    users_factories.EmailAdminValidationEntryFactory(
        eventType=users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE,
        creationDate=now,
        newUserEmail="beneficiary",
        newDomainEmail="example.com",
        oldUserEmail="intermediary",
        oldDomainEmail="example.com",
        user=user,
    )
    history_factories.ActionHistoryFactory(
        actionDate=now - datetime.timedelta(days=2),
        actionType=history_models.ActionType.USER_SUSPENDED,
        user=user,
    )
    history_factories.ActionHistoryFactory(
        actionDate=now,
        actionType=history_models.ActionType.USER_UNSUSPENDED,
        user=user,
    )
    fraud_factories.BeneficiaryFraudCheckFactory(
        dateCreated=now,
        eligibilityType=users_models.EligibilityType.AGE18,
        status=fraud_models.FraudCheckStatus.OK,
        type=fraud_models.FraudCheckType.DMS,
        updatedAt=now + datetime.timedelta(days=1),
        user=user,
    )
    users_factories.DepositGrantFactory(
        user=user,
        dateCreated=now - datetime.timedelta(days=2),
        dateUpdated=now + datetime.timedelta(days=1),
        expirationDate=now + datetime.timedelta(days=15000),
        amount=Decimal("300.0"),
        source="source",
        type=finance_enum.DepositType.GRANT_18,
    )
    bookings_factories.BookingFactory(
        user=user,
        dateCreated=now,
        dateUsed=now,
        quantity=1,
        amount=Decimal("10.00"),
        status=bookings_models.BookingStatus.CONFIRMED,
        stock__offer__name="offer_name",
        stock__offer__venue__name="venue_name",
        stock__offer__venue__managingOfferer__name="offerer_name",
    )
    bookings_factories.BookingFactory(
        user=user,
        cancellationDate=now,
        dateCreated=now,
        quantity=1,
        amount=Decimal("50.00"),
        status=bookings_models.BookingStatus.CANCELLED,
        stock__offer__name="offer2_name",
        stock__offer__venue__name="venue2_name",
        stock__offer__venue__managingOfferer__name="offerer2_name",
    )
    return user


def generate_minimal_beneficiary():
    # generate a user with all objects where all optional fields to None
    now = datetime.datetime(2024, 1, 1)
    user = users_models.User(
        dateCreated=now,
        email="empty@example.com",
        hasSeenProTutorials=False,
        hasSeenProRgs=False,
        needsToFillCulturalSurvey=False,
        notificationSubscriptions=None,
        roles=[users_models.UserRole.BENEFICIARY],
    )
    db.session.add(user)
    db.session.flush()
    db.session.add(
        users_models.LoginDeviceHistory(
            user=user,
            deviceId="a device id",
            dateCreated=now,
        )
    )
    db.session.add(
        users_models.UserEmailHistory(
            user=user,
            oldUserEmail="oldUserEmail",
            oldDomainEmail="example.com",
            creationDate=now,
            eventType=users_models.EmailHistoryEventTypeEnum.ADMIN_UPDATE,
        )
    )
    db.session.add(
        history_models.ActionHistory(
            user=user,
            actionType=history_models.ActionType.USER_SUSPENDED,
            actionDate=now,
        )
    )
    db.session.add(
        fraud_models.BeneficiaryFraudCheck(
            user=user,
            dateCreated=now,
            thirdPartyId="third_party_id",
            type=fraud_models.FraudCheckType.DMS,
            updatedAt=now,
        )
    )
    deposit = finance_models.Deposit(
        user=user,
        amount=Decimal("300.00"),
        source="démarches simplifiées dossier [1234567]",
        dateCreated=now,
        version=1,
        type=finance_enum.DepositType.GRANT_18,
    )
    db.session.add(deposit)
    stock = offers_factories.StockFactory(
        offer__name="offer_name",
        offer__venue__name="venue_name",
        offer__venue__managingOfferer__name="offerer_name",
    )
    db.session.add(
        bookings_models.Booking(
            user=user,
            dateCreated=now,
            stock=stock,
            venue=stock.offer.venue,
            offerer=stock.offer.venue.managingOfferer,
            quantity=1,
            token="token",
            amount=Decimal("13.34"),
            status=bookings_models.BookingStatus.CANCELLED,
            cancellationDate=now,
            deposit=deposit,
        )
    )
    db.session.flush()
    db.session.refresh(user)
    return user


class ExtractBeneficiaryDataTest(StorageFolderManager):
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER
    # 1 select gdpr_user_data_extract
    # 2 update gdpr user data
    # 3 refresh extract_gdpr_user_data
    # 4 select user
    # 5 select login device history
    # 6 select user_email_history
    # 7 select action_history
    # 8 select beneficiary_fraud_check
    # 9 select deposit
    # 10 select bookings
    # 11 select user (authorUser)
    # 12 insert action history
    expected_queries = 12
    # 1 json
    # 2 pdf
    output_files_count = 2

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_json_output(self, pdf_generator_mock) -> None:
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        with assert_num_queries(self.expected_queries):
            users_api.extract_beneficiary_data(extract=extract)

        file_path = self.storage_folder / f"{extract.id}.zip"

        json_file_name = f"{user.email}.json"
        with zipfile.ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert json_file_name in files
            with zip_pointer.open(json_file_name) as json_pointer:
                raw_data = json_pointer.read()
                json_data = raw_data.decode("utf-8")
                result = json.loads(json_data)

        assert "generationDate" in result
        del result["generationDate"]
        assert result == {
            "external": {
                "brevo": {
                    "attributes": {
                        "ADDRESS": "987 5th avenue",
                        "AREA": "NY",
                        "CITY": "New-York",
                        "CIV": "1",
                        "DOB": "1986-04-13",
                        "FIRST_NAME": "valid",
                        "LAST_NAME": "email",
                        "SMS": "3087433387669",
                        "ZIP_CODE": "87544",
                    },
                    "createdAt": "2017-05-02T16:40:31Z",
                    "email": "valid_email@example.com",
                    "emailBlacklisted": False,
                    "id": 42,
                    "listIds": [40],
                    "modifiedAt": "2017-05-02T16:40:31Z",
                    "smsBlacklisted": False,
                    "statistics": {
                        "clicked": [
                            {
                                "campaignId": 21,
                                "links": [
                                    {
                                        "count": 2,
                                        "eventTime": "2016-05-03T21:25:01Z",
                                        "ip": "66.249.93.118",
                                        "url": "https://url.domain.com/fbe5387ec717e333628380454f68670010b205ff/1/go?uid={EMAIL}&utm_source=brevo&utm_campaign=test_camp&utm_medium=email",
                                    }
                                ],
                            }
                        ],
                        "delivered": [
                            {"campaignId": 21, "count": 2, "eventTime": "2016-05-03T21:24:56Z", "ip": "66.249.93.118"}
                        ],
                        "messagesSent": [
                            {"campaignId": 21, "eventTime": "2016-05-03T20:15:13Z"},
                            {"campaignId": 42, "eventTime": "2016-10-17T10:30:01Z"},
                        ],
                        "opened": [
                            {"campaignId": 21, "count": 2, "eventTime": "2016-05-03T21:24:56Z", "ip": "66.249.93.118"},
                            {"campaignId": 68, "count": 1, "eventTime": "2017-01-30T13:56:40Z", "ip": "66.249.93.217"},
                        ],
                    },
                }
            },
            "internal": {
                "actionsHistory": [
                    {"actionDate": "2023-12-30T00:00:00", "actionType": "Compte suspendu"},
                    {"actionDate": "2024-01-01T00:00:00", "actionType": "Compte réactivé"},
                ],
                "beneficiaryValidations": [
                    {
                        "dateCreated": "2024-01-01T00:00:00",
                        "eligibilityType": "Pass 18",
                        "status": "Succès",
                        "type": "Démarches simplifiées",
                        "updatedAt": "2024-01-02T00:00:00",
                    }
                ],
                "bookings": [
                    {
                        "amount": 10.0,
                        "cancellationDate": None,
                        "dateCreated": "2024-01-01T00:00:00",
                        "dateUsed": "2024-01-01T00:00:00",
                        "name": "offer_name",
                        "offerer": "offerer_name",
                        "quantity": 1,
                        "status": "Réservé",
                        "venue": "venue_name",
                    },
                    {
                        "amount": 50.0,
                        "cancellationDate": "2024-01-01T00:00:00",
                        "dateCreated": "2024-01-01T00:00:00",
                        "dateUsed": None,
                        "name": "offer2_name",
                        "offerer": "offerer2_name",
                        "quantity": 1,
                        "status": "Annulé",
                        "venue": "venue2_name",
                    },
                ],
                "deposits": [
                    {
                        "amount": 300.0,
                        "dateCreated": "2023-12-30T00:00:00",
                        "dateUpdated": "2024-01-02T00:00:00",
                        "expirationDate": "2065-01-25T00:00:00",
                        "source": "source",
                        "type": "Pass 18",
                    }
                ],
                "emailsHistory": [
                    {
                        "dateCreated": "2023-12-30T00:00:00",
                        "newEmail": "intermediary@example.com",
                        "oldEmail": "old@example.com",
                    },
                    {
                        "dateCreated": "2024-01-01T00:00:00",
                        "newEmail": "beneficiary@example.com",
                        "oldEmail": "intermediary@example.com",
                    },
                ],
                "loginDevices": [
                    {
                        "dateCreated": "2023-12-30T00:00:00",
                        "deviceId": "anotsorandomdeviceid2",
                        "location": "Lyon",
                        "os": "oldOs",
                        "source": "phone1",
                    },
                    {
                        "dateCreated": "2024-01-01T00:00:00",
                        "deviceId": "anotsorandomdeviceid",
                        "location": "Paris",
                        "os": "os/2",
                        "source": "phone 2",
                    },
                ],
                "marketing": {"marketingEmails": True, "marketingNotifications": False},
                "user": {
                    "activity": "Lycéen",
                    "address": "123 rue du pass",
                    "city": "Paris",
                    "civility": "M.",
                    "culturalSurveyFilledDate": "2024-01-01T00:00:00",
                    "dateCreated": "2024-01-01T00:00:00",
                    "dateOfBirth": "2010-01-01T00:00:00",
                    "departementCode": "75",
                    "email": "valid_email@example.com",
                    "firstName": "Beneficiary",
                    "isActive": True,
                    "isEmailValidated": True,
                    "lastName": "bénéficiaire",
                    "marriedName": "married_name",
                    "postalCode": "75000",
                    "schoolType": "Collège public",
                    "validatedBirthDate": "2010-01-01",
                },
            },
        }

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_pdf_html(self, pdf_generator_mock) -> None:
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        with assert_num_queries(self.expected_queries):
            users_api.extract_beneficiary_data(extract=extract)

        file_path = self.storage_folder / f"{extract.id}.zip"

        pdf_file_name = f"{user.email}.pdf"
        with zipfile.ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read() == b"content of a pdf"

        pdf_generator_mock.assert_called_once_with(
            html_content="""<!DOCTYPE html>\n<html lang="fr">\n    <head>\n        <meta charset="utf-8">\n        <title>Réponse à ta demande d’accès</title>\n        <style>\n            @import url(\'https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,700;0,800;1,400\');\n\n            @page {\n                size: A4;\n                margin: 2cm 1cm;\n                @bottom-left {\n                    font-size: 6pt;\n                    content: "Pass Culture - SAS au capital de 1 000 000 € - 87/89 rue de la Boétie 75008 PARIS - RCS Paris B 853 318 459 – Siren 853318459 – NAF 7021 Z - N° TVA FR65853318459";\n                }\n                @bottom-right-corner {\n                    font-size: 8pt;\n                    content: counter(page) "/" counter(pages);\n                }\n            }\n            html {\n                font-family: Montserrat;\n                font-size: 8pt;\n                line-height: 1.5;\n                font-weight: normal;\n            }\n            h1 {\n                color: #870087;\n                position: relative;\n                top: -0.5cm;\n                font-size: 16pt;\n                font-weight: bold;\n            }\n            h3 {\n                color: #870087;\n                font-size: 10pt;\n                font-style: normal;\n                font-weight: normal;\n                text-decoration: underline;\n            }\n            .headerImage {\n                position: absolute;\n                width: 19.5cm;\n                top: -1cm;\n            }\n            .purple-background {\n                background-color:rgba(135, 0, 135, 0.1);\n\n            }\n            table {\n                border-left-color: black;\n                border-left-width: 1px;\n                border-left-style: solid;\n                margin-top: 0.5cm;\n                margin-bottom: 0.5cm;\n            }\n            td{\n                padding-right: 0.5cm;\n            }\n        </style>\n\n        <meta name="description" content="Réponse à ta demande d’accès">\n    </head>\n    <body>\n        <svg class="headerImage" width="563" height="125" viewBox="0 0 563 125" fill="none" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">\n            <g fill="none" fill-rule="evenodd" transform="matrix(1.1867861,0,0,1.1867861,405.09345,0.26463512)">\n                <g fill="#870087" fill-rule="nonzero">\n                    <path d="m 33.362,13.427 c 0.677,-0.417 1.2,-1.004 1.571,-1.76 C 35.304,10.911 35.49,10.035 35.49,9.04 35.49,8.033 35.301,7.142 34.925,6.368 34.547,5.594 34.015,4.995 33.327,4.571 32.639,4.146 31.845,3.934 30.948,3.934 c -0.646,0 -1.229,0.133 -1.75,0.397 -0.52,0.265 -0.954,0.648 -1.3,1.153 V 4.027 H 25.132 V 17.52 h 2.765 v -5.013 c 0.358,0.504 0.799,0.888 1.319,1.152 0.52,0.264 1.116,0.396 1.786,0.396 0.898,0 1.684,-0.209 2.36,-0.627 z M 28.57,10.94 c -0.448,-0.503 -0.672,-1.167 -0.672,-1.99 0,-0.8 0.224,-1.454 0.672,-1.964 0.45,-0.51 1.027,-0.765 1.733,-0.765 0.706,0 1.28,0.255 1.723,0.765 0.443,0.51 0.664,1.165 0.664,1.963 0,0.811 -0.221,1.472 -0.664,1.982 -0.442,0.51 -1.017,0.764 -1.723,0.764 -0.706,0 -1.283,-0.251 -1.733,-0.755 z m 34.313,0.857 c -0.222,0.129 -0.517,0.194 -0.888,0.194 -0.539,0 -1.11,-0.108 -1.715,-0.324 -0.604,-0.214 -1.152,-0.518 -1.642,-0.91 l -0.898,1.915 c 0.538,0.443 1.173,0.784 1.903,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.148,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.163,-1.176 -0.485,-1.577 C 65.045,8.964 64.662,8.663 64.219,8.461 63.777,8.258 63.215,8.052 62.532,7.843 61.91,7.659 61.462,7.493 61.186,7.346 60.911,7.198 60.773,6.989 60.773,6.719 c 0,-0.246 0.103,-0.43 0.305,-0.553 0.204,-0.122 0.474,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.035,0.402 1.562,0.71 L 65.782,5.006 C 65.243,4.649 64.644,4.375 63.986,4.184 63.328,3.994 62.67,3.899 62.013,3.899 c -1.102,0 -2.011,0.27 -2.73,0.81 -0.717,0.541 -1.076,1.303 -1.076,2.287 0,0.639 0.155,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.121,0.894 0.437,0.196 0.985,0.394 1.643,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.28,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z m -37.75,20.111 h 2.765 V 18.231 h -2.765 v 13.676 z m -5.09,-5.014 c 0,0.737 -0.191,1.34 -0.575,1.807 -0.382,0.467 -0.903,0.707 -1.561,0.718 -0.562,0 -1.005,-0.177 -1.329,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.475,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 H 22.79 V 21.99 h -2.747 v 4.903 z M 8.76,29.041 C 8.179,29.317 7.608,29.456 7.046,29.456 6.34,29.456 5.693,29.275 5.106,28.912 4.52,28.549 4.06,28.058 3.724,27.437 3.389,26.817 3.222,26.132 3.222,25.382 c 0,-0.75 0.167,-1.432 0.502,-2.045 0.336,-0.616 0.796,-1.1 1.383,-1.457 0.586,-0.357 1.233,-0.535 1.939,-0.535 0.585,0 1.169,0.151 1.75,0.452 0.58,0.302 1.085,0.716 1.516,1.244 l 1.651,-2.083 c -0.622,-0.664 -1.375,-1.189 -2.261,-1.576 -0.885,-0.386 -1.783,-0.58 -2.693,-0.58 -1.244,0 -2.378,0.289 -3.4,0.866 -1.024,0.578 -1.83,1.37 -2.415,2.378 -0.586,1.007 -0.88,2.132 -0.88,3.373 0,1.254 0.288,2.39 0.862,3.41 0.574,1.02 1.364,1.822 2.37,2.405 1.004,0.584 2.123,0.876 3.356,0.876 0.909,0 1.815,-0.209 2.72,-0.627 0.903,-0.417 1.69,-0.983 2.36,-1.696 l -1.67,-1.861 C 9.857,28.392 9.339,28.764 8.76,29.041 Z m 25.873,0.599 c -0.587,0 -0.88,-0.38 -0.88,-1.143 v -4.092 h 2.62 v -1.972 h -2.62 v -2.728 h -2.746 v 2.728 H 29.66 v 1.954 h 1.347 v 4.59 c 0,0.983 0.281,1.738 0.843,2.267 0.563,0.529 1.293,0.792 2.19,0.792 0.443,0 0.883,-0.058 1.32,-0.175 0.436,-0.117 0.834,-0.286 1.193,-0.507 l -0.574,-2.083 c -0.49,0.246 -0.94,0.369 -1.346,0.369 z m 17.78,-5.862 V 21.99 H 49.65 v 9.917 h 2.764 v -4.774 c 0,-0.786 0.248,-1.416 0.745,-1.889 0.496,-0.473 1.17,-0.71 2.019,-0.71 0.192,0 0.335,0.007 0.43,0.019 V 21.88 c -0.717,0.012 -1.345,0.178 -1.884,0.497 -0.538,0.32 -0.975,0.787 -1.31,1.4 z m 8.681,-1.88 c -0.968,0 -1.83,0.212 -2.584,0.636 -0.753,0.424 -1.34,1.02 -1.759,1.788 -0.418,0.768 -0.628,1.656 -0.628,2.664 0,0.995 0.207,1.873 0.62,2.635 0.412,0.763 0.999,1.353 1.759,1.77 0.759,0.417 1.648,0.627 2.665,0.627 0.862,0 1.643,-0.15 2.342,-0.452 0.7,-0.3 1.296,-0.734 1.786,-1.3 l -1.454,-1.511 c -0.335,0.345 -0.712,0.605 -1.13,0.783 -0.42,0.178 -0.856,0.268 -1.311,0.268 -0.622,0 -1.155,-0.176 -1.597,-0.525 -0.443,-0.35 -0.742,-0.839 -0.897,-1.466 h 6.928 c 0.012,-0.16 0.018,-0.387 0.018,-0.682 0,-1.647 -0.404,-2.931 -1.211,-3.853 -0.808,-0.921 -1.99,-1.382 -3.547,-1.382 z m -2.243,4.24 c 0.109,-0.663 0.363,-1.189 0.764,-1.576 0.4,-0.387 0.9,-0.58 1.498,-0.58 0.634,0 1.143,0.196 1.526,0.589 0.383,0.393 0.586,0.915 0.61,1.567 z m -14.202,0.755 c 0,0.737 -0.192,1.34 -0.575,1.807 -0.383,0.467 -0.903,0.707 -1.562,0.718 -0.562,0 -1.004,-0.177 -1.328,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.474,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 h 2.747 V 21.99 H 44.65 v 4.903 z M 53.16,11.796 c -0.22,0.129 -0.517,0.194 -0.889,0.194 -0.538,0 -1.11,-0.108 -1.713,-0.324 -0.605,-0.214 -1.152,-0.518 -1.643,-0.91 l -0.897,1.915 c 0.538,0.443 1.172,0.784 1.902,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.149,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.161,-1.176 -0.485,-1.577 C 55.323,8.963 54.94,8.662 54.497,8.46 54.055,8.257 53.492,8.051 52.811,7.842 52.187,7.658 51.739,7.492 51.464,7.345 51.188,7.197 51.051,6.988 51.051,6.718 c 0,-0.246 0.102,-0.43 0.305,-0.553 0.203,-0.122 0.473,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.036,0.402 1.562,0.71 l 0.95,-1.935 C 55.52,4.648 54.922,4.374 54.264,4.183 53.605,3.993 52.947,3.898 52.289,3.898 c -1.1,0 -2.01,0.27 -2.728,0.81 -0.719,0.541 -1.077,1.303 -1.077,2.287 0,0.639 0.156,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.122,0.894 0.436,0.196 0.984,0.394 1.642,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.281,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z M 40.786,7.99 c -1.173,0.012 -2.08,0.279 -2.72,0.802 -0.64,0.522 -0.96,1.25 -0.96,2.184 0,0.922 0.3,1.668 0.897,2.24 0.598,0.57 1.407,0.857 2.424,0.857 0.67,0 1.262,-0.111 1.777,-0.332 0.514,-0.221 0.933,-0.54 1.256,-0.959 v 1.161 h 2.71 L 46.153,7.473 C 46.141,6.355 45.779,5.483 45.066,4.856 44.355,4.23 43.353,3.916 42.06,3.916 c -0.802,0 -1.538,0.093 -2.208,0.277 -0.67,0.184 -1.388,0.473 -2.154,0.867 l 0.862,1.953 c 1.017,-0.577 1.974,-0.867 2.872,-0.867 0.658,0 1.157,0.146 1.498,0.434 0.341,0.289 0.512,0.697 0.512,1.225 V 7.99 Z m 2.656,2.562 c -0.084,0.43 -0.335,0.787 -0.754,1.069 -0.418,0.283 -0.915,0.424 -1.49,0.424 -0.467,0 -0.835,-0.113 -1.103,-0.342 -0.27,-0.226 -0.404,-0.53 -0.404,-0.911 0,-0.393 0.129,-0.679 0.386,-0.857 0.257,-0.179 0.654,-0.268 1.193,-0.268 h 2.172 z M 82.516,9.44 c 0.059,0.107 0.17,0.168 0.285,0.168 0.053,0 0.106,-0.013 0.156,-0.04 0.156,-0.087 0.214,-0.284 0.127,-0.442 L 80.812,4.983 C 80.726,4.826 80.528,4.768 80.372,4.855 80.215,4.941 80.158,5.139 80.244,5.296 l 2.272,4.143 z M 79.588,4.1 c 0.06,0.108 0.17,0.169 0.285,0.169 0.053,0 0.106,-0.013 0.155,-0.04 0.158,-0.087 0.215,-0.285 0.129,-0.442 L 79.227,2.093 C 79.142,1.936 78.944,1.879 78.787,1.965 78.63,2.051 78.574,2.249 78.66,2.407 Z m 6.066,7.826 c 0.038,0.147 0.17,0.245 0.314,0.245 0.027,0 0.054,-0.004 0.081,-0.01 0.173,-0.045 0.278,-0.222 0.233,-0.396 L 83.666,1.553 C 83.622,1.379 83.446,1.274 83.272,1.319 83.098,1.363 82.994,1.541 83.038,1.714 l 2.616,10.213 z M 83.4,10.38 c -0.156,0.086 -0.214,0.284 -0.128,0.442 l 0.648,1.18 c 0.059,0.108 0.17,0.17 0.284,0.17 0.053,0 0.106,-0.013 0.156,-0.041 0.157,-0.086 0.214,-0.284 0.128,-0.441 l -0.647,-1.182 c -0.087,-0.157 -0.284,-0.215 -0.44,-0.128 z m -1.18,2.323 c 0.064,0.068 0.15,0.102 0.236,0.102 0.08,0 0.16,-0.03 0.222,-0.088 0.13,-0.123 0.137,-0.329 0.015,-0.46 L 76.782,5.947 C 76.659,5.817 76.454,5.81 76.324,5.933 76.193,6.056 76.186,6.261 76.309,6.393 l 5.91,6.31 z m 6.755,-0.54 c 0.027,0.006 0.054,0.01 0.08,0.01 0.145,0 0.276,-0.098 0.314,-0.245 L 91.827,2.333 C 91.872,2.159 91.767,1.982 91.594,1.937 91.42,1.893 91.244,1.997 91.199,2.171 l -2.458,9.596 c -0.044,0.174 0.06,0.35 0.234,0.396 z m -8.844,9.52 c 0.046,0 0.093,-0.01 0.138,-0.032 l 1.367,-0.645 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 l -1.367,0.645 c -0.163,0.076 -0.232,0.27 -0.156,0.432 0.055,0.118 0.172,0.187 0.294,0.187 z m 1.367,-5.44 c 0.136,0 0.264,-0.088 0.308,-0.226 0.056,-0.17 -0.038,-0.354 -0.208,-0.41 l -6.353,-2.068 c -0.17,-0.055 -0.353,0.038 -0.408,0.208 -0.055,0.171 0.038,0.355 0.208,0.41 l 6.353,2.07 c 0.033,0.01 0.067,0.015 0.1,0.015 z m -2.817,5.439 -3.52,1.66 c -0.162,0.077 -0.232,0.27 -0.156,0.433 0.056,0.117 0.173,0.186 0.294,0.186 0.046,0 0.093,-0.01 0.138,-0.03 l 3.52,-1.661 c 0.163,-0.077 0.232,-0.27 0.156,-0.433 -0.077,-0.162 -0.27,-0.232 -0.432,-0.155 z m 3.135,-2.717 c -0.034,-0.177 -0.203,-0.292 -0.379,-0.259 l -9.755,1.866 c -0.176,0.033 -0.292,0.203 -0.258,0.38 0.03,0.156 0.165,0.264 0.318,0.264 0.02,0 0.04,-0.002 0.06,-0.006 l 9.757,-1.865 c 0.175,-0.034 0.291,-0.204 0.257,-0.38 z m -4.622,-1.415 4.284,0.27 0.02,0.001 c 0.17,0 0.313,-0.132 0.323,-0.304 0.012,-0.18 -0.124,-0.334 -0.303,-0.345 l -4.284,-0.27 c -0.178,-0.012 -0.332,0.125 -0.343,0.304 -0.012,0.179 0.124,0.333 0.303,0.344 z M 93.21,14.252 c 0.062,0.098 0.166,0.151 0.274,0.151 0.06,0 0.12,-0.016 0.173,-0.05 l 8.228,-5.236 c 0.15,-0.096 0.196,-0.297 0.1,-0.45 -0.096,-0.15 -0.296,-0.195 -0.447,-0.1 l -8.228,5.237 c -0.151,0.096 -0.196,0.297 -0.1,0.448 z m 6.54,-0.362 c -0.056,-0.171 -0.239,-0.265 -0.409,-0.21 l -5.917,1.928 c -0.17,0.055 -0.263,0.239 -0.208,0.41 0.044,0.137 0.172,0.224 0.308,0.224 0.034,0 0.068,-0.005 0.1,-0.016 l 5.917,-1.927 c 0.17,-0.055 0.264,-0.239 0.208,-0.41 z m -6.246,3.282 c -0.178,0.011 -0.314,0.166 -0.303,0.345 0.01,0.172 0.153,0.304 0.323,0.304 h 0.02 l 3.547,-0.224 c 0.18,-0.011 0.315,-0.165 0.303,-0.345 -0.01,-0.179 -0.165,-0.315 -0.343,-0.304 z m -0.118,3.834 6.2,2.924 c 0.044,0.021 0.09,0.031 0.137,0.031 0.122,0 0.238,-0.069 0.294,-0.186 0.076,-0.163 0.007,-0.356 -0.156,-0.433 l -6.198,-2.924 c -0.162,-0.076 -0.356,-0.006 -0.432,0.156 -0.076,0.162 -0.006,0.356 0.155,0.432 z m -2.725,-8.874 c 0.05,0.028 0.103,0.04 0.156,0.04 0.114,0 0.225,-0.06 0.284,-0.168 L 93.024,8.497 C 93.111,8.34 93.054,8.142 92.897,8.056 92.74,7.969 92.543,8.026 92.457,8.184 l -1.924,3.507 c -0.087,0.157 -0.029,0.355 0.128,0.441 z m -8.949,1.67 -1.408,-0.896 c -0.151,-0.096 -0.351,-0.051 -0.447,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 l 1.408,0.896 c 0.053,0.034 0.114,0.05 0.173,0.05 0.108,0 0.212,-0.053 0.274,-0.15 0.096,-0.152 0.051,-0.353 -0.1,-0.449 z m 19.148,-0.274 c 0.045,0.137 0.172,0.225 0.308,0.225 0.034,0 0.068,-0.006 0.1,-0.017 l 2.27,-0.739 c 0.17,-0.055 0.263,-0.239 0.208,-0.41 -0.055,-0.17 -0.238,-0.263 -0.409,-0.208 l -2.269,0.74 c -0.17,0.055 -0.263,0.238 -0.208,0.409 z m -7.033,-2.394 c 0.063,0.058 0.143,0.088 0.222,0.088 0.086,0 0.173,-0.035 0.237,-0.103 L 97.307,7.893 C 97.43,7.763 97.423,7.557 97.293,7.433 97.163,7.311 96.957,7.317 96.835,7.448 l -3.022,3.226 c -0.123,0.131 -0.116,0.337 0.014,0.46 z m -0.557,0.594 c -0.13,-0.123 -0.336,-0.116 -0.458,0.015 l -0.483,0.514 c -0.123,0.13 -0.116,0.336 0.014,0.46 0.062,0.058 0.142,0.087 0.222,0.087 0.087,0 0.173,-0.034 0.236,-0.102 l 0.484,-0.514 c 0.122,-0.131 0.116,-0.337 -0.015,-0.46 z m 0.16,-4.646 c 0.05,0.028 0.103,0.04 0.156,0.04 0.115,0 0.226,-0.06 0.285,-0.168 l 2.32,-4.23 C 96.277,2.566 96.22,2.368 96.063,2.282 95.906,2.196 95.709,2.252 95.623,2.41 l -2.32,4.23 c -0.087,0.158 -0.03,0.356 0.127,0.442 z m -1.858,16.395 c -0.145,0.105 -0.178,0.308 -0.072,0.453 l 1.729,2.387 c 0.063,0.087 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.146,-0.106 0.177,-0.309 0.072,-0.454 L 92.024,23.548 C 91.919,23.403 91.717,23.371 91.572,23.477 Z M 98.15,6.843 c 0.086,0 0.173,-0.034 0.236,-0.102 l 1.721,-1.837 c 0.123,-0.131 0.116,-0.337 -0.014,-0.46 -0.13,-0.123 -0.336,-0.116 -0.459,0.014 l -1.72,1.838 c -0.123,0.13 -0.117,0.336 0.013,0.46 0.063,0.058 0.143,0.087 0.223,0.087 z m -24.604,2.532 5.208,3.313 c 0.054,0.034 0.114,0.05 0.174,0.05 0.107,0 0.212,-0.053 0.274,-0.15 0.095,-0.152 0.05,-0.353 -0.1,-0.449 L 73.894,8.826 c -0.152,-0.096 -0.352,-0.051 -0.448,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 z m 20.057,23.038 c -0.066,-0.166 -0.254,-0.248 -0.42,-0.182 -0.167,0.066 -0.249,0.255 -0.183,0.422 l 0.626,1.584 c 0.05,0.128 0.173,0.206 0.302,0.206 0.04,0 0.08,-0.008 0.12,-0.023 0.165,-0.066 0.247,-0.255 0.181,-0.422 z m -2.985,-7.558 -0.424,-1.072 c -0.065,-0.167 -0.254,-0.249 -0.42,-0.183 -0.167,0.067 -0.248,0.256 -0.183,0.422 l 0.424,1.072 c 0.05,0.128 0.173,0.205 0.302,0.205 0.039,0 0.08,-0.007 0.119,-0.022 0.166,-0.067 0.248,-0.256 0.182,-0.422 z m -1.592,5.035 c 0.178,-0.022 0.304,-0.185 0.281,-0.363 l -0.714,-5.665 c -0.022,-0.178 -0.184,-0.304 -0.362,-0.282 -0.177,0.023 -0.303,0.185 -0.28,0.364 l 0.713,5.664 c 0.02,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,-0.001 0.041,-0.003 z m 0.114,0.902 c -0.178,0.022 -0.304,0.185 -0.28,0.363 l 0.416,3.31 c 0.021,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,0 0.042,-0.003 0.177,-0.022 0.303,-0.185 0.28,-0.363 l -0.416,-3.31 C 89.48,30.896 89.318,30.77 89.14,30.792 Z m 4.23,-8.48 c -0.137,-0.114 -0.341,-0.095 -0.456,0.043 -0.114,0.139 -0.095,0.344 0.043,0.458 l 6.931,5.747 c 0.06,0.05 0.134,0.074 0.207,0.074 0.093,0 0.185,-0.04 0.25,-0.118 0.114,-0.138 0.095,-0.343 -0.044,-0.457 l -6.93,-5.747 z m 11.55,-5.86 -6.456,0.406 c -0.178,0.012 -0.314,0.166 -0.303,0.345 0.01,0.172 0.154,0.305 0.323,0.305 h 0.021 L 104.96,17.1 c 0.179,-0.011 0.315,-0.166 0.303,-0.345 -0.011,-0.179 -0.164,-0.315 -0.344,-0.304 z m -1.091,4.212 -10.242,-1.959 c -0.177,-0.033 -0.346,0.082 -0.38,0.259 -0.033,0.176 0.082,0.346 0.258,0.38 l 10.242,1.958 c 0.02,0.004 0.041,0.006 0.061,0.006 0.153,0 0.289,-0.108 0.319,-0.264 0.033,-0.176 -0.083,-0.346 -0.258,-0.38 z M 87.512,0.08 c -0.179,0 -0.324,0.145 -0.324,0.325 v 2.458 c 0,0.179 0.145,0.324 0.324,0.324 0.179,0 0.324,-0.145 0.324,-0.324 V 0.405 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m 7.403,27.455 c -0.106,-0.145 -0.309,-0.177 -0.453,-0.072 -0.145,0.106 -0.177,0.309 -0.072,0.454 l 2.42,3.338 c 0.063,0.088 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.145,-0.105 0.178,-0.308 0.072,-0.454 l -2.42,-3.338 z m 8.662,-2.442 -2.269,-1.07 c -0.162,-0.077 -0.355,-0.007 -0.431,0.155 -0.077,0.163 -0.008,0.357 0.155,0.433 l 2.269,1.07 c 0.045,0.021 0.091,0.032 0.138,0.032 0.121,0 0.238,-0.07 0.293,-0.187 0.077,-0.163 0.007,-0.356 -0.155,-0.433 z m -12.36,1.279 c -0.066,-0.167 -0.254,-0.249 -0.421,-0.183 -0.166,0.067 -0.248,0.255 -0.182,0.422 l 1.736,4.397 c 0.051,0.127 0.173,0.205 0.302,0.205 0.04,0 0.08,-0.007 0.12,-0.023 0.166,-0.066 0.247,-0.255 0.181,-0.422 z m -9.105,-4.018 c -0.114,-0.139 -0.318,-0.158 -0.457,-0.043 l -6.715,5.568 c -0.138,0.114 -0.158,0.32 -0.044,0.458 0.064,0.077 0.157,0.117 0.25,0.117 0.073,0 0.146,-0.024 0.207,-0.074 l 6.716,-5.569 c 0.138,-0.114 0.157,-0.319 0.043,-0.457 z m -8.277,1.613 -2.23,1.052 c -0.162,0.076 -0.231,0.27 -0.155,0.432 0.055,0.118 0.172,0.187 0.293,0.187 0.047,0 0.094,-0.01 0.138,-0.031 l 2.23,-1.052 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 z m 1.926,-6.508 c 0.17,0 0.312,-0.133 0.323,-0.305 0.011,-0.18 -0.124,-0.334 -0.303,-0.345 l -5.676,-0.358 c -0.179,-0.011 -0.333,0.125 -0.344,0.304 -0.011,0.18 0.125,0.334 0.303,0.345 l 5.676,0.358 h 0.021 z m -4.924,-4.674 2.732,0.89 c 0.033,0.01 0.067,0.016 0.1,0.016 0.137,0 0.264,-0.087 0.309,-0.225 0.055,-0.17 -0.038,-0.354 -0.208,-0.41 l -2.732,-0.889 c -0.17,-0.055 -0.354,0.038 -0.409,0.209 -0.055,0.17 0.038,0.354 0.208,0.41 z m 7.721,16.891 -1.552,2.141 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.057,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.047 0.263,-0.134 l 1.552,-2.14 c 0.105,-0.146 0.073,-0.35 -0.072,-0.455 -0.145,-0.105 -0.348,-0.073 -0.453,0.072 z m 4.894,-6.2 c -0.145,-0.105 -0.348,-0.073 -0.453,0.072 l -3.502,4.832 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.058,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.046 0.263,-0.134 l 3.502,-4.832 c 0.105,-0.145 0.073,-0.348 -0.072,-0.454 z M 85.25,23.6 c -0.166,-0.066 -0.354,0.016 -0.42,0.183 l -1.385,3.507 c -0.066,0.167 0.015,0.356 0.182,0.422 0.039,0.015 0.08,0.023 0.119,0.023 0.13,0 0.25,-0.078 0.301,-0.205 l 1.386,-3.508 C 85.498,23.856 85.417,23.667 85.25,23.6 Z m 1.543,-0.02 c -0.177,-0.022 -0.34,0.104 -0.362,0.282 l -1.442,11.442 c -0.023,0.178 0.103,0.34 0.28,0.363 l 0.042,0.003 c 0.161,0 0.3,-0.12 0.32,-0.285 l 1.443,-11.441 c 0.023,-0.179 -0.103,-0.341 -0.28,-0.364 z m 0.72,-18.765 c -0.18,0 -0.325,0.145 -0.325,0.325 v 6.707 c 0,0.179 0.145,0.325 0.324,0.325 0.179,0 0.324,-0.146 0.324,-0.325 V 5.14 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m -4.28,23.893 c -0.166,-0.066 -0.355,0.016 -0.42,0.183 l -2.018,5.107 c -0.066,0.167 0.016,0.356 0.182,0.422 0.04,0.015 0.08,0.023 0.12,0.023 0.129,0 0.25,-0.078 0.301,-0.206 L 83.416,29.13 C 83.481,28.963 83.4,28.774 83.233,28.708 Z" transform="translate(0.741)"/>\n                </g>\n            </g>\n            <rect y="64" width="4" height="531" transform="rotate(-90 0 64)" fill="#870087"/>\n            <defs>\n                <clipPath>\n                    <rect width="181" height="65" fill="white" transform="translate(382 60)"/>\n                </clipPath>\n            </defs>\n        </svg>\n        <h1>Réponse à ta demande d’accès</h1>\n        <div class="purple-background">\n            <p>\n                <i>\n                    Dans le cadre de l’utilisation des services du pass Culture nous sommes susceptibles de collecter les données personnelles de nos utilisateurs, par exemple, pour assurer la gestion des réservations, adresser des bulletins d’actualité, lutter contre la fraude ou répondre à des demandes d’information. Le présent document te permet de prendre connaissance des données qui te concernent et qui sont utilisées pour le bon fonctionnement de nos services.\n                </i>\n            </p>\n            <p>\n                <i>\n                    Pour plus d’informations, tu peux également consulter notre <a href="https://pass.culture.fr/donnees-personnelles/">charte des données personnelles</a> ou contacter directement notre Délégué à la protection des données (DPO) : <a href="mailto:dpo@passculture.app">dpo@passculture.app</a>. \n                </i>\n            </p>\n        </div>\n        <h3>Données de l’utilisateur</h3>\n        <table class="borderless">\n            <tr><td>Nom</td><td>Beneficiary</td></tr>\n            <tr><td>Prénom</td><td>bénéficiaire</td></tr>\n            <tr><td>Nom de mariage</td><td>married_name</td></tr> \n            <tr><td>Adresse de messagerie</td><td>valid_email@example.com</td></tr>\n            <tr><td>Adresse</td><td>123 rue du pass</td></tr>\n            <tr><td>Code postal</td><td>75000</td></tr>\n            <tr><td>Ville</td><td>Paris</td></tr>\n            <tr><td>Département</td><td>75</td></tr>\n            <tr><td>Date de naissance</td><td>01/01/2010</td></tr> \n            <tr><td>Date de naissance confirmée</td><td>01/01/2010</td></tr>\n            <tr><td>Date de création du compte</td><td>01/01/2024 00:00:00</td></tr>\n            <tr><td>Compte actif</td><td>oui</td></tr>\n            <tr><td>Activité</td><td>Lycéen</td></tr>\n            <tr><td>Type d\'école</td><td>Collège public</td></tr>\n        </table>\n\n        <h3>Informations marketing</h3>\n        <table class="borderless">\n            <tr><td>Accepte la récéption de mails</td><td>oui</td></tr>\n            <tr><td>Accepte les notifications mobiles</td><td>non</td></tr>\n        </table>\n\n        \n            <h3>Historique des moyens de connexion</h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de première connexion</td><td>30/12/2023 00:00:00</td></tr>\n                    <tr><td>Identifiant de l’appareil</td><td>anotsorandomdeviceid2</td></tr>\n                    <tr><td>Type d’appareil</td><td>phone1</td></tr>\n                    <tr><td>Système d’exploitation</td><td>oldOs</td></tr>\n                </table>\n            \n                <table class="borderless">\n                    <tr><td>Date de première connexion</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Identifiant de l’appareil</td><td>anotsorandomdeviceid</td></tr>\n                    <tr><td>Type d’appareil</td><td>phone 2</td></tr>\n                    <tr><td>Système d’exploitation</td><td>os/2</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>Historique des changements d’adresse de messagerie</h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de la demande</td><td>30/12/2023 00:00:00</td></tr>\n                    <tr><td>Ancienne adresse email</td><td>old@example.com</td></tr>\n                    <tr><td>Nouvelle adresse email</td><td>intermediary@example.com</td></tr>\n                </table>\n            \n                <table class="borderless">\n                    <tr><td>Date de la demande</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Ancienne adresse email</td><td>intermediary@example.com</td></tr>\n                    <tr><td>Nouvelle adresse email</td><td>beneficiary@example.com</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>Historique des blocages du compte « pass Culture »</h3>\n            \n                <table class="borderless">\n                    <tr><td>Date</td><td>30/12/2023 00:00:00</td></tr>\n                    <tr><td>Action</td><td>Compte suspendu</td></tr>\n                </table>\n            \n                <table class="borderless">\n                    <tr><td>Date</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Action</td><td>Compte réactivé</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>Validations d’identité</h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de la validation</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Moyen de la validation</td><td>Démarches simplifiées</td></tr>\n                    <tr><td>Résultat</td><td>Succès</td></tr>\n                     <tr><td>Dernière modification</td><td>02/01/2024 00:00:00</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>Crédits</h3>\n            \n                <table class="borderless">\n                    <tr><td>Date d’obtention</td><td>30/12/2023 00:00:00</td></tr>\n                    <tr><td>Date d’expiration</td><td>25/01/2065 00:00:00</td></tr>\n                    <tr><td>Valeur</td><td>300,00€</td></tr>\n                    <tr><td>Source</td><td>source</td></tr>\n                    <tr><td>Dernière modification</td><td>02/01/2024 00:00:00</td></tr>\n                    <tr><td>Type de crédit</td><td>Pass 18</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>Réservations effectuées depuis l’application « pass Culture »</h3>\n            \n                <table class="borderless">\n                    <tr><td>Nom</td><td>offer_name</td></tr>\n                    <tr><td>Quantité</td><td>1</td></tr>\n                    <tr><td>Prix unitaire</td><td>10,00€</td></tr>\n                    <tr><td>Date de réservation</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Date de retrait</td><td>01/01/2024 00:00:00</td></tr>\n                    \n                    <tr><td>État</td><td>Réservé</td></tr>\n                    <tr><td>Lieu de vente</td><td>venue_name</td></tr>\n                    <tr><td>Vendeur</td><td>offerer_name</td></tr>\n                </table>\n            \n                <table class="borderless">\n                    <tr><td>Nom</td><td>offer2_name</td></tr>\n                    <tr><td>Quantité</td><td>1</td></tr>\n                    <tr><td>Prix unitaire</td><td>50,00€</td></tr>\n                    <tr><td>Date de réservation</td><td>01/01/2024 00:00:00</td></tr>\n                    \n                    <tr><td>Date d’annulation</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>État</td><td>Annulé</td></tr>\n                    <tr><td>Lieu de vente</td><td>venue2_name</td></tr>\n                    <tr><td>Vendeur</td><td>offerer2_name</td></tr>\n                </table>\n            \n        \n    <div class="purple-background">\n        Bon à savoir : si tu souhaites récupérer ces données dans un format « interopérable » (fichier « .json »), lisible par une machine, tu peux contacter le DPO (dpo@passculture.app) afin d’exercer ton droit à la portabilité.\n    </div>\n    </body>\n</html>"""
        )

    def test_pdf_generated(self, css_font_http_request_mock):
        user = generate_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )

        users_api.extract_beneficiary_data(extract)

        file_path = self.storage_folder / f"{extract.id}.zip"
        pdf_file_name = f"{user.email}.pdf"
        with zipfile.ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read()

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_pdf_with_empty_user(self, pdf_generator_mock=None) -> None:
        user = users_models.User(
            firstName="firstname",
            lastName="lastName",
            email="firstname.lastname@example.com",
            dateCreated=datetime.datetime(2024, 6, 26, 13, 14, 28),
        )
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        with assert_num_queries(self.expected_queries):
            users_api.extract_beneficiary_data(extract=extract)

        file_path = self.storage_folder / f"{extract.id}.zip"

        pdf_file_name = f"{user.email}.pdf"
        with zipfile.ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read() == b"content of a pdf"

        pdf_generator_mock.assert_called_once_with(
            html_content="""<!DOCTYPE html>\n<html lang="fr">\n    <head>\n        <meta charset="utf-8">\n        <title>Réponse à ta demande d’accès</title>\n        <style>\n            @import url(\'https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,700;0,800;1,400\');\n\n            @page {\n                size: A4;\n                margin: 2cm 1cm;\n                @bottom-left {\n                    font-size: 6pt;\n                    content: "Pass Culture - SAS au capital de 1 000 000 € - 87/89 rue de la Boétie 75008 PARIS - RCS Paris B 853 318 459 – Siren 853318459 – NAF 7021 Z - N° TVA FR65853318459";\n                }\n                @bottom-right-corner {\n                    font-size: 8pt;\n                    content: counter(page) "/" counter(pages);\n                }\n            }\n            html {\n                font-family: Montserrat;\n                font-size: 8pt;\n                line-height: 1.5;\n                font-weight: normal;\n            }\n            h1 {\n                color: #870087;\n                position: relative;\n                top: -0.5cm;\n                font-size: 16pt;\n                font-weight: bold;\n            }\n            h3 {\n                color: #870087;\n                font-size: 10pt;\n                font-style: normal;\n                font-weight: normal;\n                text-decoration: underline;\n            }\n            .headerImage {\n                position: absolute;\n                width: 19.5cm;\n                top: -1cm;\n            }\n            .purple-background {\n                background-color:rgba(135, 0, 135, 0.1);\n\n            }\n            table {\n                border-left-color: black;\n                border-left-width: 1px;\n                border-left-style: solid;\n                margin-top: 0.5cm;\n                margin-bottom: 0.5cm;\n            }\n            td{\n                padding-right: 0.5cm;\n            }\n        </style>\n\n        <meta name="description" content="Réponse à ta demande d’accès">\n    </head>\n    <body>\n        <svg class="headerImage" width="563" height="125" viewBox="0 0 563 125" fill="none" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">\n            <g fill="none" fill-rule="evenodd" transform="matrix(1.1867861,0,0,1.1867861,405.09345,0.26463512)">\n                <g fill="#870087" fill-rule="nonzero">\n                    <path d="m 33.362,13.427 c 0.677,-0.417 1.2,-1.004 1.571,-1.76 C 35.304,10.911 35.49,10.035 35.49,9.04 35.49,8.033 35.301,7.142 34.925,6.368 34.547,5.594 34.015,4.995 33.327,4.571 32.639,4.146 31.845,3.934 30.948,3.934 c -0.646,0 -1.229,0.133 -1.75,0.397 -0.52,0.265 -0.954,0.648 -1.3,1.153 V 4.027 H 25.132 V 17.52 h 2.765 v -5.013 c 0.358,0.504 0.799,0.888 1.319,1.152 0.52,0.264 1.116,0.396 1.786,0.396 0.898,0 1.684,-0.209 2.36,-0.627 z M 28.57,10.94 c -0.448,-0.503 -0.672,-1.167 -0.672,-1.99 0,-0.8 0.224,-1.454 0.672,-1.964 0.45,-0.51 1.027,-0.765 1.733,-0.765 0.706,0 1.28,0.255 1.723,0.765 0.443,0.51 0.664,1.165 0.664,1.963 0,0.811 -0.221,1.472 -0.664,1.982 -0.442,0.51 -1.017,0.764 -1.723,0.764 -0.706,0 -1.283,-0.251 -1.733,-0.755 z m 34.313,0.857 c -0.222,0.129 -0.517,0.194 -0.888,0.194 -0.539,0 -1.11,-0.108 -1.715,-0.324 -0.604,-0.214 -1.152,-0.518 -1.642,-0.91 l -0.898,1.915 c 0.538,0.443 1.173,0.784 1.903,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.148,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.163,-1.176 -0.485,-1.577 C 65.045,8.964 64.662,8.663 64.219,8.461 63.777,8.258 63.215,8.052 62.532,7.843 61.91,7.659 61.462,7.493 61.186,7.346 60.911,7.198 60.773,6.989 60.773,6.719 c 0,-0.246 0.103,-0.43 0.305,-0.553 0.204,-0.122 0.474,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.035,0.402 1.562,0.71 L 65.782,5.006 C 65.243,4.649 64.644,4.375 63.986,4.184 63.328,3.994 62.67,3.899 62.013,3.899 c -1.102,0 -2.011,0.27 -2.73,0.81 -0.717,0.541 -1.076,1.303 -1.076,2.287 0,0.639 0.155,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.121,0.894 0.437,0.196 0.985,0.394 1.643,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.28,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z m -37.75,20.111 h 2.765 V 18.231 h -2.765 v 13.676 z m -5.09,-5.014 c 0,0.737 -0.191,1.34 -0.575,1.807 -0.382,0.467 -0.903,0.707 -1.561,0.718 -0.562,0 -1.005,-0.177 -1.329,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.475,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 H 22.79 V 21.99 h -2.747 v 4.903 z M 8.76,29.041 C 8.179,29.317 7.608,29.456 7.046,29.456 6.34,29.456 5.693,29.275 5.106,28.912 4.52,28.549 4.06,28.058 3.724,27.437 3.389,26.817 3.222,26.132 3.222,25.382 c 0,-0.75 0.167,-1.432 0.502,-2.045 0.336,-0.616 0.796,-1.1 1.383,-1.457 0.586,-0.357 1.233,-0.535 1.939,-0.535 0.585,0 1.169,0.151 1.75,0.452 0.58,0.302 1.085,0.716 1.516,1.244 l 1.651,-2.083 c -0.622,-0.664 -1.375,-1.189 -2.261,-1.576 -0.885,-0.386 -1.783,-0.58 -2.693,-0.58 -1.244,0 -2.378,0.289 -3.4,0.866 -1.024,0.578 -1.83,1.37 -2.415,2.378 -0.586,1.007 -0.88,2.132 -0.88,3.373 0,1.254 0.288,2.39 0.862,3.41 0.574,1.02 1.364,1.822 2.37,2.405 1.004,0.584 2.123,0.876 3.356,0.876 0.909,0 1.815,-0.209 2.72,-0.627 0.903,-0.417 1.69,-0.983 2.36,-1.696 l -1.67,-1.861 C 9.857,28.392 9.339,28.764 8.76,29.041 Z m 25.873,0.599 c -0.587,0 -0.88,-0.38 -0.88,-1.143 v -4.092 h 2.62 v -1.972 h -2.62 v -2.728 h -2.746 v 2.728 H 29.66 v 1.954 h 1.347 v 4.59 c 0,0.983 0.281,1.738 0.843,2.267 0.563,0.529 1.293,0.792 2.19,0.792 0.443,0 0.883,-0.058 1.32,-0.175 0.436,-0.117 0.834,-0.286 1.193,-0.507 l -0.574,-2.083 c -0.49,0.246 -0.94,0.369 -1.346,0.369 z m 17.78,-5.862 V 21.99 H 49.65 v 9.917 h 2.764 v -4.774 c 0,-0.786 0.248,-1.416 0.745,-1.889 0.496,-0.473 1.17,-0.71 2.019,-0.71 0.192,0 0.335,0.007 0.43,0.019 V 21.88 c -0.717,0.012 -1.345,0.178 -1.884,0.497 -0.538,0.32 -0.975,0.787 -1.31,1.4 z m 8.681,-1.88 c -0.968,0 -1.83,0.212 -2.584,0.636 -0.753,0.424 -1.34,1.02 -1.759,1.788 -0.418,0.768 -0.628,1.656 -0.628,2.664 0,0.995 0.207,1.873 0.62,2.635 0.412,0.763 0.999,1.353 1.759,1.77 0.759,0.417 1.648,0.627 2.665,0.627 0.862,0 1.643,-0.15 2.342,-0.452 0.7,-0.3 1.296,-0.734 1.786,-1.3 l -1.454,-1.511 c -0.335,0.345 -0.712,0.605 -1.13,0.783 -0.42,0.178 -0.856,0.268 -1.311,0.268 -0.622,0 -1.155,-0.176 -1.597,-0.525 -0.443,-0.35 -0.742,-0.839 -0.897,-1.466 h 6.928 c 0.012,-0.16 0.018,-0.387 0.018,-0.682 0,-1.647 -0.404,-2.931 -1.211,-3.853 -0.808,-0.921 -1.99,-1.382 -3.547,-1.382 z m -2.243,4.24 c 0.109,-0.663 0.363,-1.189 0.764,-1.576 0.4,-0.387 0.9,-0.58 1.498,-0.58 0.634,0 1.143,0.196 1.526,0.589 0.383,0.393 0.586,0.915 0.61,1.567 z m -14.202,0.755 c 0,0.737 -0.192,1.34 -0.575,1.807 -0.383,0.467 -0.903,0.707 -1.562,0.718 -0.562,0 -1.004,-0.177 -1.328,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.474,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 h 2.747 V 21.99 H 44.65 v 4.903 z M 53.16,11.796 c -0.22,0.129 -0.517,0.194 -0.889,0.194 -0.538,0 -1.11,-0.108 -1.713,-0.324 -0.605,-0.214 -1.152,-0.518 -1.643,-0.91 l -0.897,1.915 c 0.538,0.443 1.172,0.784 1.902,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.149,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.161,-1.176 -0.485,-1.577 C 55.323,8.963 54.94,8.662 54.497,8.46 54.055,8.257 53.492,8.051 52.811,7.842 52.187,7.658 51.739,7.492 51.464,7.345 51.188,7.197 51.051,6.988 51.051,6.718 c 0,-0.246 0.102,-0.43 0.305,-0.553 0.203,-0.122 0.473,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.036,0.402 1.562,0.71 l 0.95,-1.935 C 55.52,4.648 54.922,4.374 54.264,4.183 53.605,3.993 52.947,3.898 52.289,3.898 c -1.1,0 -2.01,0.27 -2.728,0.81 -0.719,0.541 -1.077,1.303 -1.077,2.287 0,0.639 0.156,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.122,0.894 0.436,0.196 0.984,0.394 1.642,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.281,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z M 40.786,7.99 c -1.173,0.012 -2.08,0.279 -2.72,0.802 -0.64,0.522 -0.96,1.25 -0.96,2.184 0,0.922 0.3,1.668 0.897,2.24 0.598,0.57 1.407,0.857 2.424,0.857 0.67,0 1.262,-0.111 1.777,-0.332 0.514,-0.221 0.933,-0.54 1.256,-0.959 v 1.161 h 2.71 L 46.153,7.473 C 46.141,6.355 45.779,5.483 45.066,4.856 44.355,4.23 43.353,3.916 42.06,3.916 c -0.802,0 -1.538,0.093 -2.208,0.277 -0.67,0.184 -1.388,0.473 -2.154,0.867 l 0.862,1.953 c 1.017,-0.577 1.974,-0.867 2.872,-0.867 0.658,0 1.157,0.146 1.498,0.434 0.341,0.289 0.512,0.697 0.512,1.225 V 7.99 Z m 2.656,2.562 c -0.084,0.43 -0.335,0.787 -0.754,1.069 -0.418,0.283 -0.915,0.424 -1.49,0.424 -0.467,0 -0.835,-0.113 -1.103,-0.342 -0.27,-0.226 -0.404,-0.53 -0.404,-0.911 0,-0.393 0.129,-0.679 0.386,-0.857 0.257,-0.179 0.654,-0.268 1.193,-0.268 h 2.172 z M 82.516,9.44 c 0.059,0.107 0.17,0.168 0.285,0.168 0.053,0 0.106,-0.013 0.156,-0.04 0.156,-0.087 0.214,-0.284 0.127,-0.442 L 80.812,4.983 C 80.726,4.826 80.528,4.768 80.372,4.855 80.215,4.941 80.158,5.139 80.244,5.296 l 2.272,4.143 z M 79.588,4.1 c 0.06,0.108 0.17,0.169 0.285,0.169 0.053,0 0.106,-0.013 0.155,-0.04 0.158,-0.087 0.215,-0.285 0.129,-0.442 L 79.227,2.093 C 79.142,1.936 78.944,1.879 78.787,1.965 78.63,2.051 78.574,2.249 78.66,2.407 Z m 6.066,7.826 c 0.038,0.147 0.17,0.245 0.314,0.245 0.027,0 0.054,-0.004 0.081,-0.01 0.173,-0.045 0.278,-0.222 0.233,-0.396 L 83.666,1.553 C 83.622,1.379 83.446,1.274 83.272,1.319 83.098,1.363 82.994,1.541 83.038,1.714 l 2.616,10.213 z M 83.4,10.38 c -0.156,0.086 -0.214,0.284 -0.128,0.442 l 0.648,1.18 c 0.059,0.108 0.17,0.17 0.284,0.17 0.053,0 0.106,-0.013 0.156,-0.041 0.157,-0.086 0.214,-0.284 0.128,-0.441 l -0.647,-1.182 c -0.087,-0.157 -0.284,-0.215 -0.44,-0.128 z m -1.18,2.323 c 0.064,0.068 0.15,0.102 0.236,0.102 0.08,0 0.16,-0.03 0.222,-0.088 0.13,-0.123 0.137,-0.329 0.015,-0.46 L 76.782,5.947 C 76.659,5.817 76.454,5.81 76.324,5.933 76.193,6.056 76.186,6.261 76.309,6.393 l 5.91,6.31 z m 6.755,-0.54 c 0.027,0.006 0.054,0.01 0.08,0.01 0.145,0 0.276,-0.098 0.314,-0.245 L 91.827,2.333 C 91.872,2.159 91.767,1.982 91.594,1.937 91.42,1.893 91.244,1.997 91.199,2.171 l -2.458,9.596 c -0.044,0.174 0.06,0.35 0.234,0.396 z m -8.844,9.52 c 0.046,0 0.093,-0.01 0.138,-0.032 l 1.367,-0.645 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 l -1.367,0.645 c -0.163,0.076 -0.232,0.27 -0.156,0.432 0.055,0.118 0.172,0.187 0.294,0.187 z m 1.367,-5.44 c 0.136,0 0.264,-0.088 0.308,-0.226 0.056,-0.17 -0.038,-0.354 -0.208,-0.41 l -6.353,-2.068 c -0.17,-0.055 -0.353,0.038 -0.408,0.208 -0.055,0.171 0.038,0.355 0.208,0.41 l 6.353,2.07 c 0.033,0.01 0.067,0.015 0.1,0.015 z m -2.817,5.439 -3.52,1.66 c -0.162,0.077 -0.232,0.27 -0.156,0.433 0.056,0.117 0.173,0.186 0.294,0.186 0.046,0 0.093,-0.01 0.138,-0.03 l 3.52,-1.661 c 0.163,-0.077 0.232,-0.27 0.156,-0.433 -0.077,-0.162 -0.27,-0.232 -0.432,-0.155 z m 3.135,-2.717 c -0.034,-0.177 -0.203,-0.292 -0.379,-0.259 l -9.755,1.866 c -0.176,0.033 -0.292,0.203 -0.258,0.38 0.03,0.156 0.165,0.264 0.318,0.264 0.02,0 0.04,-0.002 0.06,-0.006 l 9.757,-1.865 c 0.175,-0.034 0.291,-0.204 0.257,-0.38 z m -4.622,-1.415 4.284,0.27 0.02,0.001 c 0.17,0 0.313,-0.132 0.323,-0.304 0.012,-0.18 -0.124,-0.334 -0.303,-0.345 l -4.284,-0.27 c -0.178,-0.012 -0.332,0.125 -0.343,0.304 -0.012,0.179 0.124,0.333 0.303,0.344 z M 93.21,14.252 c 0.062,0.098 0.166,0.151 0.274,0.151 0.06,0 0.12,-0.016 0.173,-0.05 l 8.228,-5.236 c 0.15,-0.096 0.196,-0.297 0.1,-0.45 -0.096,-0.15 -0.296,-0.195 -0.447,-0.1 l -8.228,5.237 c -0.151,0.096 -0.196,0.297 -0.1,0.448 z m 6.54,-0.362 c -0.056,-0.171 -0.239,-0.265 -0.409,-0.21 l -5.917,1.928 c -0.17,0.055 -0.263,0.239 -0.208,0.41 0.044,0.137 0.172,0.224 0.308,0.224 0.034,0 0.068,-0.005 0.1,-0.016 l 5.917,-1.927 c 0.17,-0.055 0.264,-0.239 0.208,-0.41 z m -6.246,3.282 c -0.178,0.011 -0.314,0.166 -0.303,0.345 0.01,0.172 0.153,0.304 0.323,0.304 h 0.02 l 3.547,-0.224 c 0.18,-0.011 0.315,-0.165 0.303,-0.345 -0.01,-0.179 -0.165,-0.315 -0.343,-0.304 z m -0.118,3.834 6.2,2.924 c 0.044,0.021 0.09,0.031 0.137,0.031 0.122,0 0.238,-0.069 0.294,-0.186 0.076,-0.163 0.007,-0.356 -0.156,-0.433 l -6.198,-2.924 c -0.162,-0.076 -0.356,-0.006 -0.432,0.156 -0.076,0.162 -0.006,0.356 0.155,0.432 z m -2.725,-8.874 c 0.05,0.028 0.103,0.04 0.156,0.04 0.114,0 0.225,-0.06 0.284,-0.168 L 93.024,8.497 C 93.111,8.34 93.054,8.142 92.897,8.056 92.74,7.969 92.543,8.026 92.457,8.184 l -1.924,3.507 c -0.087,0.157 -0.029,0.355 0.128,0.441 z m -8.949,1.67 -1.408,-0.896 c -0.151,-0.096 -0.351,-0.051 -0.447,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 l 1.408,0.896 c 0.053,0.034 0.114,0.05 0.173,0.05 0.108,0 0.212,-0.053 0.274,-0.15 0.096,-0.152 0.051,-0.353 -0.1,-0.449 z m 19.148,-0.274 c 0.045,0.137 0.172,0.225 0.308,0.225 0.034,0 0.068,-0.006 0.1,-0.017 l 2.27,-0.739 c 0.17,-0.055 0.263,-0.239 0.208,-0.41 -0.055,-0.17 -0.238,-0.263 -0.409,-0.208 l -2.269,0.74 c -0.17,0.055 -0.263,0.238 -0.208,0.409 z m -7.033,-2.394 c 0.063,0.058 0.143,0.088 0.222,0.088 0.086,0 0.173,-0.035 0.237,-0.103 L 97.307,7.893 C 97.43,7.763 97.423,7.557 97.293,7.433 97.163,7.311 96.957,7.317 96.835,7.448 l -3.022,3.226 c -0.123,0.131 -0.116,0.337 0.014,0.46 z m -0.557,0.594 c -0.13,-0.123 -0.336,-0.116 -0.458,0.015 l -0.483,0.514 c -0.123,0.13 -0.116,0.336 0.014,0.46 0.062,0.058 0.142,0.087 0.222,0.087 0.087,0 0.173,-0.034 0.236,-0.102 l 0.484,-0.514 c 0.122,-0.131 0.116,-0.337 -0.015,-0.46 z m 0.16,-4.646 c 0.05,0.028 0.103,0.04 0.156,0.04 0.115,0 0.226,-0.06 0.285,-0.168 l 2.32,-4.23 C 96.277,2.566 96.22,2.368 96.063,2.282 95.906,2.196 95.709,2.252 95.623,2.41 l -2.32,4.23 c -0.087,0.158 -0.03,0.356 0.127,0.442 z m -1.858,16.395 c -0.145,0.105 -0.178,0.308 -0.072,0.453 l 1.729,2.387 c 0.063,0.087 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.146,-0.106 0.177,-0.309 0.072,-0.454 L 92.024,23.548 C 91.919,23.403 91.717,23.371 91.572,23.477 Z M 98.15,6.843 c 0.086,0 0.173,-0.034 0.236,-0.102 l 1.721,-1.837 c 0.123,-0.131 0.116,-0.337 -0.014,-0.46 -0.13,-0.123 -0.336,-0.116 -0.459,0.014 l -1.72,1.838 c -0.123,0.13 -0.117,0.336 0.013,0.46 0.063,0.058 0.143,0.087 0.223,0.087 z m -24.604,2.532 5.208,3.313 c 0.054,0.034 0.114,0.05 0.174,0.05 0.107,0 0.212,-0.053 0.274,-0.15 0.095,-0.152 0.05,-0.353 -0.1,-0.449 L 73.894,8.826 c -0.152,-0.096 -0.352,-0.051 -0.448,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 z m 20.057,23.038 c -0.066,-0.166 -0.254,-0.248 -0.42,-0.182 -0.167,0.066 -0.249,0.255 -0.183,0.422 l 0.626,1.584 c 0.05,0.128 0.173,0.206 0.302,0.206 0.04,0 0.08,-0.008 0.12,-0.023 0.165,-0.066 0.247,-0.255 0.181,-0.422 z m -2.985,-7.558 -0.424,-1.072 c -0.065,-0.167 -0.254,-0.249 -0.42,-0.183 -0.167,0.067 -0.248,0.256 -0.183,0.422 l 0.424,1.072 c 0.05,0.128 0.173,0.205 0.302,0.205 0.039,0 0.08,-0.007 0.119,-0.022 0.166,-0.067 0.248,-0.256 0.182,-0.422 z m -1.592,5.035 c 0.178,-0.022 0.304,-0.185 0.281,-0.363 l -0.714,-5.665 c -0.022,-0.178 -0.184,-0.304 -0.362,-0.282 -0.177,0.023 -0.303,0.185 -0.28,0.364 l 0.713,5.664 c 0.02,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,-0.001 0.041,-0.003 z m 0.114,0.902 c -0.178,0.022 -0.304,0.185 -0.28,0.363 l 0.416,3.31 c 0.021,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,0 0.042,-0.003 0.177,-0.022 0.303,-0.185 0.28,-0.363 l -0.416,-3.31 C 89.48,30.896 89.318,30.77 89.14,30.792 Z m 4.23,-8.48 c -0.137,-0.114 -0.341,-0.095 -0.456,0.043 -0.114,0.139 -0.095,0.344 0.043,0.458 l 6.931,5.747 c 0.06,0.05 0.134,0.074 0.207,0.074 0.093,0 0.185,-0.04 0.25,-0.118 0.114,-0.138 0.095,-0.343 -0.044,-0.457 l -6.93,-5.747 z m 11.55,-5.86 -6.456,0.406 c -0.178,0.012 -0.314,0.166 -0.303,0.345 0.01,0.172 0.154,0.305 0.323,0.305 h 0.021 L 104.96,17.1 c 0.179,-0.011 0.315,-0.166 0.303,-0.345 -0.011,-0.179 -0.164,-0.315 -0.344,-0.304 z m -1.091,4.212 -10.242,-1.959 c -0.177,-0.033 -0.346,0.082 -0.38,0.259 -0.033,0.176 0.082,0.346 0.258,0.38 l 10.242,1.958 c 0.02,0.004 0.041,0.006 0.061,0.006 0.153,0 0.289,-0.108 0.319,-0.264 0.033,-0.176 -0.083,-0.346 -0.258,-0.38 z M 87.512,0.08 c -0.179,0 -0.324,0.145 -0.324,0.325 v 2.458 c 0,0.179 0.145,0.324 0.324,0.324 0.179,0 0.324,-0.145 0.324,-0.324 V 0.405 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m 7.403,27.455 c -0.106,-0.145 -0.309,-0.177 -0.453,-0.072 -0.145,0.106 -0.177,0.309 -0.072,0.454 l 2.42,3.338 c 0.063,0.088 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.145,-0.105 0.178,-0.308 0.072,-0.454 l -2.42,-3.338 z m 8.662,-2.442 -2.269,-1.07 c -0.162,-0.077 -0.355,-0.007 -0.431,0.155 -0.077,0.163 -0.008,0.357 0.155,0.433 l 2.269,1.07 c 0.045,0.021 0.091,0.032 0.138,0.032 0.121,0 0.238,-0.07 0.293,-0.187 0.077,-0.163 0.007,-0.356 -0.155,-0.433 z m -12.36,1.279 c -0.066,-0.167 -0.254,-0.249 -0.421,-0.183 -0.166,0.067 -0.248,0.255 -0.182,0.422 l 1.736,4.397 c 0.051,0.127 0.173,0.205 0.302,0.205 0.04,0 0.08,-0.007 0.12,-0.023 0.166,-0.066 0.247,-0.255 0.181,-0.422 z m -9.105,-4.018 c -0.114,-0.139 -0.318,-0.158 -0.457,-0.043 l -6.715,5.568 c -0.138,0.114 -0.158,0.32 -0.044,0.458 0.064,0.077 0.157,0.117 0.25,0.117 0.073,0 0.146,-0.024 0.207,-0.074 l 6.716,-5.569 c 0.138,-0.114 0.157,-0.319 0.043,-0.457 z m -8.277,1.613 -2.23,1.052 c -0.162,0.076 -0.231,0.27 -0.155,0.432 0.055,0.118 0.172,0.187 0.293,0.187 0.047,0 0.094,-0.01 0.138,-0.031 l 2.23,-1.052 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 z m 1.926,-6.508 c 0.17,0 0.312,-0.133 0.323,-0.305 0.011,-0.18 -0.124,-0.334 -0.303,-0.345 l -5.676,-0.358 c -0.179,-0.011 -0.333,0.125 -0.344,0.304 -0.011,0.18 0.125,0.334 0.303,0.345 l 5.676,0.358 h 0.021 z m -4.924,-4.674 2.732,0.89 c 0.033,0.01 0.067,0.016 0.1,0.016 0.137,0 0.264,-0.087 0.309,-0.225 0.055,-0.17 -0.038,-0.354 -0.208,-0.41 l -2.732,-0.889 c -0.17,-0.055 -0.354,0.038 -0.409,0.209 -0.055,0.17 0.038,0.354 0.208,0.41 z m 7.721,16.891 -1.552,2.141 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.057,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.047 0.263,-0.134 l 1.552,-2.14 c 0.105,-0.146 0.073,-0.35 -0.072,-0.455 -0.145,-0.105 -0.348,-0.073 -0.453,0.072 z m 4.894,-6.2 c -0.145,-0.105 -0.348,-0.073 -0.453,0.072 l -3.502,4.832 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.058,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.046 0.263,-0.134 l 3.502,-4.832 c 0.105,-0.145 0.073,-0.348 -0.072,-0.454 z M 85.25,23.6 c -0.166,-0.066 -0.354,0.016 -0.42,0.183 l -1.385,3.507 c -0.066,0.167 0.015,0.356 0.182,0.422 0.039,0.015 0.08,0.023 0.119,0.023 0.13,0 0.25,-0.078 0.301,-0.205 l 1.386,-3.508 C 85.498,23.856 85.417,23.667 85.25,23.6 Z m 1.543,-0.02 c -0.177,-0.022 -0.34,0.104 -0.362,0.282 l -1.442,11.442 c -0.023,0.178 0.103,0.34 0.28,0.363 l 0.042,0.003 c 0.161,0 0.3,-0.12 0.32,-0.285 l 1.443,-11.441 c 0.023,-0.179 -0.103,-0.341 -0.28,-0.364 z m 0.72,-18.765 c -0.18,0 -0.325,0.145 -0.325,0.325 v 6.707 c 0,0.179 0.145,0.325 0.324,0.325 0.179,0 0.324,-0.146 0.324,-0.325 V 5.14 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m -4.28,23.893 c -0.166,-0.066 -0.355,0.016 -0.42,0.183 l -2.018,5.107 c -0.066,0.167 0.016,0.356 0.182,0.422 0.04,0.015 0.08,0.023 0.12,0.023 0.129,0 0.25,-0.078 0.301,-0.206 L 83.416,29.13 C 83.481,28.963 83.4,28.774 83.233,28.708 Z" transform="translate(0.741)"/>\n                </g>\n            </g>\n            <rect y="64" width="4" height="531" transform="rotate(-90 0 64)" fill="#870087"/>\n            <defs>\n                <clipPath>\n                    <rect width="181" height="65" fill="white" transform="translate(382 60)"/>\n                </clipPath>\n            </defs>\n        </svg>\n        <h1>Réponse à ta demande d’accès</h1>\n        <div class="purple-background">\n            <p>\n                <i>\n                    Dans le cadre de l’utilisation des services du pass Culture nous sommes susceptibles de collecter les données personnelles de nos utilisateurs, par exemple, pour assurer la gestion des réservations, adresser des bulletins d’actualité, lutter contre la fraude ou répondre à des demandes d’information. Le présent document te permet de prendre connaissance des données qui te concernent et qui sont utilisées pour le bon fonctionnement de nos services.\n                </i>\n            </p>\n            <p>\n                <i>\n                    Pour plus d’informations, tu peux également consulter notre <a href="https://pass.culture.fr/donnees-personnelles/">charte des données personnelles</a> ou contacter directement notre Délégué à la protection des données (DPO) : <a href="mailto:dpo@passculture.app">dpo@passculture.app</a>. \n                </i>\n            </p>\n        </div>\n        <h3>Données de l’utilisateur</h3>\n        <table class="borderless">\n            <tr><td>Nom</td><td>firstname</td></tr>\n            <tr><td>Prénom</td><td>lastName</td></tr>\n            \n            <tr><td>Adresse de messagerie</td><td>firstname.lastname@example.com</td></tr>\n            \n            \n            \n            \n            \n            \n            <tr><td>Date de création du compte</td><td>26/06/2024 13:14:28</td></tr>\n            <tr><td>Compte actif</td><td>oui</td></tr>\n            \n            \n        </table>\n\n        <h3>Informations marketing</h3>\n        <table class="borderless">\n            <tr><td>Accepte la récéption de mails</td><td>oui</td></tr>\n            <tr><td>Accepte les notifications mobiles</td><td>oui</td></tr>\n        </table>\n\n        \n\n        \n\n        \n\n        \n\n        \n\n        \n    <div class="purple-background">\n        Bon à savoir : si tu souhaites récupérer ces données dans un format « interopérable » (fichier « .json »), lisible par une machine, tu peux contacter le DPO (dpo@passculture.app) afin d’exercer ton droit à la portabilité.\n    </div>\n    </body>\n</html>"""
        )

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_pdf_with_minimal_non_empty_user(self, pdf_generator_mock):
        user = generate_minimal_beneficiary()
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            user=user,
        )
        with assert_num_queries(self.expected_queries):
            users_api.extract_beneficiary_data(extract=extract)

        file_path = self.storage_folder / f"{extract.id}.zip"

        pdf_file_name = f"{user.email}.pdf"
        with zipfile.ZipFile(file_path, mode="r") as zip_pointer:
            files = zip_pointer.namelist()
            assert len(files) == self.output_files_count
            assert pdf_file_name in files
            with zip_pointer.open(pdf_file_name) as pdf_pointer:
                assert pdf_pointer.read() == b"content of a pdf"

        pdf_generator_mock.assert_called_once_with(
            html_content="""<!DOCTYPE html>\n<html lang="fr">\n    <head>\n        <meta charset="utf-8">\n        <title>Réponse à ta demande d’accès</title>\n        <style>\n            @import url(\'https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,600;0,700;0,800;1,400\');\n\n            @page {\n                size: A4;\n                margin: 2cm 1cm;\n                @bottom-left {\n                    font-size: 6pt;\n                    content: "Pass Culture - SAS au capital de 1 000 000 € - 87/89 rue de la Boétie 75008 PARIS - RCS Paris B 853 318 459 – Siren 853318459 – NAF 7021 Z - N° TVA FR65853318459";\n                }\n                @bottom-right-corner {\n                    font-size: 8pt;\n                    content: counter(page) "/" counter(pages);\n                }\n            }\n            html {\n                font-family: Montserrat;\n                font-size: 8pt;\n                line-height: 1.5;\n                font-weight: normal;\n            }\n            h1 {\n                color: #870087;\n                position: relative;\n                top: -0.5cm;\n                font-size: 16pt;\n                font-weight: bold;\n            }\n            h3 {\n                color: #870087;\n                font-size: 10pt;\n                font-style: normal;\n                font-weight: normal;\n                text-decoration: underline;\n            }\n            .headerImage {\n                position: absolute;\n                width: 19.5cm;\n                top: -1cm;\n            }\n            .purple-background {\n                background-color:rgba(135, 0, 135, 0.1);\n\n            }\n            table {\n                border-left-color: black;\n                border-left-width: 1px;\n                border-left-style: solid;\n                margin-top: 0.5cm;\n                margin-bottom: 0.5cm;\n            }\n            td{\n                padding-right: 0.5cm;\n            }\n        </style>\n\n        <meta name="description" content="Réponse à ta demande d’accès">\n    </head>\n    <body>\n        <svg class="headerImage" width="563" height="125" viewBox="0 0 563 125" fill="none" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">\n            <g fill="none" fill-rule="evenodd" transform="matrix(1.1867861,0,0,1.1867861,405.09345,0.26463512)">\n                <g fill="#870087" fill-rule="nonzero">\n                    <path d="m 33.362,13.427 c 0.677,-0.417 1.2,-1.004 1.571,-1.76 C 35.304,10.911 35.49,10.035 35.49,9.04 35.49,8.033 35.301,7.142 34.925,6.368 34.547,5.594 34.015,4.995 33.327,4.571 32.639,4.146 31.845,3.934 30.948,3.934 c -0.646,0 -1.229,0.133 -1.75,0.397 -0.52,0.265 -0.954,0.648 -1.3,1.153 V 4.027 H 25.132 V 17.52 h 2.765 v -5.013 c 0.358,0.504 0.799,0.888 1.319,1.152 0.52,0.264 1.116,0.396 1.786,0.396 0.898,0 1.684,-0.209 2.36,-0.627 z M 28.57,10.94 c -0.448,-0.503 -0.672,-1.167 -0.672,-1.99 0,-0.8 0.224,-1.454 0.672,-1.964 0.45,-0.51 1.027,-0.765 1.733,-0.765 0.706,0 1.28,0.255 1.723,0.765 0.443,0.51 0.664,1.165 0.664,1.963 0,0.811 -0.221,1.472 -0.664,1.982 -0.442,0.51 -1.017,0.764 -1.723,0.764 -0.706,0 -1.283,-0.251 -1.733,-0.755 z m 34.313,0.857 c -0.222,0.129 -0.517,0.194 -0.888,0.194 -0.539,0 -1.11,-0.108 -1.715,-0.324 -0.604,-0.214 -1.152,-0.518 -1.642,-0.91 l -0.898,1.915 c 0.538,0.443 1.173,0.784 1.903,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.148,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.163,-1.176 -0.485,-1.577 C 65.045,8.964 64.662,8.663 64.219,8.461 63.777,8.258 63.215,8.052 62.532,7.843 61.91,7.659 61.462,7.493 61.186,7.346 60.911,7.198 60.773,6.989 60.773,6.719 c 0,-0.246 0.103,-0.43 0.305,-0.553 0.204,-0.122 0.474,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.035,0.402 1.562,0.71 L 65.782,5.006 C 65.243,4.649 64.644,4.375 63.986,4.184 63.328,3.994 62.67,3.899 62.013,3.899 c -1.102,0 -2.011,0.27 -2.73,0.81 -0.717,0.541 -1.076,1.303 -1.076,2.287 0,0.639 0.155,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.121,0.894 0.437,0.196 0.985,0.394 1.643,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.28,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z m -37.75,20.111 h 2.765 V 18.231 h -2.765 v 13.676 z m -5.09,-5.014 c 0,0.737 -0.191,1.34 -0.575,1.807 -0.382,0.467 -0.903,0.707 -1.561,0.718 -0.562,0 -1.005,-0.177 -1.329,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.475,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 H 22.79 V 21.99 h -2.747 v 4.903 z M 8.76,29.041 C 8.179,29.317 7.608,29.456 7.046,29.456 6.34,29.456 5.693,29.275 5.106,28.912 4.52,28.549 4.06,28.058 3.724,27.437 3.389,26.817 3.222,26.132 3.222,25.382 c 0,-0.75 0.167,-1.432 0.502,-2.045 0.336,-0.616 0.796,-1.1 1.383,-1.457 0.586,-0.357 1.233,-0.535 1.939,-0.535 0.585,0 1.169,0.151 1.75,0.452 0.58,0.302 1.085,0.716 1.516,1.244 l 1.651,-2.083 c -0.622,-0.664 -1.375,-1.189 -2.261,-1.576 -0.885,-0.386 -1.783,-0.58 -2.693,-0.58 -1.244,0 -2.378,0.289 -3.4,0.866 -1.024,0.578 -1.83,1.37 -2.415,2.378 -0.586,1.007 -0.88,2.132 -0.88,3.373 0,1.254 0.288,2.39 0.862,3.41 0.574,1.02 1.364,1.822 2.37,2.405 1.004,0.584 2.123,0.876 3.356,0.876 0.909,0 1.815,-0.209 2.72,-0.627 0.903,-0.417 1.69,-0.983 2.36,-1.696 l -1.67,-1.861 C 9.857,28.392 9.339,28.764 8.76,29.041 Z m 25.873,0.599 c -0.587,0 -0.88,-0.38 -0.88,-1.143 v -4.092 h 2.62 v -1.972 h -2.62 v -2.728 h -2.746 v 2.728 H 29.66 v 1.954 h 1.347 v 4.59 c 0,0.983 0.281,1.738 0.843,2.267 0.563,0.529 1.293,0.792 2.19,0.792 0.443,0 0.883,-0.058 1.32,-0.175 0.436,-0.117 0.834,-0.286 1.193,-0.507 l -0.574,-2.083 c -0.49,0.246 -0.94,0.369 -1.346,0.369 z m 17.78,-5.862 V 21.99 H 49.65 v 9.917 h 2.764 v -4.774 c 0,-0.786 0.248,-1.416 0.745,-1.889 0.496,-0.473 1.17,-0.71 2.019,-0.71 0.192,0 0.335,0.007 0.43,0.019 V 21.88 c -0.717,0.012 -1.345,0.178 -1.884,0.497 -0.538,0.32 -0.975,0.787 -1.31,1.4 z m 8.681,-1.88 c -0.968,0 -1.83,0.212 -2.584,0.636 -0.753,0.424 -1.34,1.02 -1.759,1.788 -0.418,0.768 -0.628,1.656 -0.628,2.664 0,0.995 0.207,1.873 0.62,2.635 0.412,0.763 0.999,1.353 1.759,1.77 0.759,0.417 1.648,0.627 2.665,0.627 0.862,0 1.643,-0.15 2.342,-0.452 0.7,-0.3 1.296,-0.734 1.786,-1.3 l -1.454,-1.511 c -0.335,0.345 -0.712,0.605 -1.13,0.783 -0.42,0.178 -0.856,0.268 -1.311,0.268 -0.622,0 -1.155,-0.176 -1.597,-0.525 -0.443,-0.35 -0.742,-0.839 -0.897,-1.466 h 6.928 c 0.012,-0.16 0.018,-0.387 0.018,-0.682 0,-1.647 -0.404,-2.931 -1.211,-3.853 -0.808,-0.921 -1.99,-1.382 -3.547,-1.382 z m -2.243,4.24 c 0.109,-0.663 0.363,-1.189 0.764,-1.576 0.4,-0.387 0.9,-0.58 1.498,-0.58 0.634,0 1.143,0.196 1.526,0.589 0.383,0.393 0.586,0.915 0.61,1.567 z m -14.202,0.755 c 0,0.737 -0.192,1.34 -0.575,1.807 -0.383,0.467 -0.903,0.707 -1.562,0.718 -0.562,0 -1.004,-0.177 -1.328,-0.534 -0.322,-0.356 -0.485,-0.848 -0.485,-1.474 v -5.42 h -2.764 v 6.23 c 0,1.168 0.314,2.093 0.943,2.775 0.628,0.682 1.474,1.023 2.54,1.023 1.495,0 2.573,-0.62 3.23,-1.862 v 1.751 h 2.747 V 21.99 H 44.65 v 4.903 z M 53.16,11.796 c -0.22,0.129 -0.517,0.194 -0.889,0.194 -0.538,0 -1.11,-0.108 -1.713,-0.324 -0.605,-0.214 -1.152,-0.518 -1.643,-0.91 l -0.897,1.915 c 0.538,0.443 1.172,0.784 1.902,1.023 0.73,0.24 1.49,0.36 2.28,0.36 1.149,0 2.09,-0.273 2.827,-0.82 0.736,-0.547 1.104,-1.312 1.104,-2.295 0,-0.65 -0.161,-1.176 -0.485,-1.577 C 55.323,8.963 54.94,8.662 54.497,8.46 54.055,8.257 53.492,8.051 52.811,7.842 52.187,7.658 51.739,7.492 51.464,7.345 51.188,7.197 51.051,6.988 51.051,6.718 c 0,-0.246 0.102,-0.43 0.305,-0.553 0.203,-0.122 0.473,-0.184 0.808,-0.184 0.407,0 0.868,0.083 1.382,0.249 0.515,0.165 1.036,0.402 1.562,0.71 l 0.95,-1.935 C 55.52,4.648 54.922,4.374 54.264,4.183 53.605,3.993 52.947,3.898 52.289,3.898 c -1.1,0 -2.01,0.27 -2.728,0.81 -0.719,0.541 -1.077,1.303 -1.077,2.287 0,0.639 0.156,1.158 0.467,1.557 0.31,0.4 0.685,0.697 1.122,0.894 0.436,0.196 0.984,0.394 1.642,0.59 0.622,0.184 1.074,0.357 1.355,0.516 0.281,0.16 0.422,0.38 0.422,0.663 0,0.259 -0.11,0.451 -0.332,0.581 z M 40.786,7.99 c -1.173,0.012 -2.08,0.279 -2.72,0.802 -0.64,0.522 -0.96,1.25 -0.96,2.184 0,0.922 0.3,1.668 0.897,2.24 0.598,0.57 1.407,0.857 2.424,0.857 0.67,0 1.262,-0.111 1.777,-0.332 0.514,-0.221 0.933,-0.54 1.256,-0.959 v 1.161 h 2.71 L 46.153,7.473 C 46.141,6.355 45.779,5.483 45.066,4.856 44.355,4.23 43.353,3.916 42.06,3.916 c -0.802,0 -1.538,0.093 -2.208,0.277 -0.67,0.184 -1.388,0.473 -2.154,0.867 l 0.862,1.953 c 1.017,-0.577 1.974,-0.867 2.872,-0.867 0.658,0 1.157,0.146 1.498,0.434 0.341,0.289 0.512,0.697 0.512,1.225 V 7.99 Z m 2.656,2.562 c -0.084,0.43 -0.335,0.787 -0.754,1.069 -0.418,0.283 -0.915,0.424 -1.49,0.424 -0.467,0 -0.835,-0.113 -1.103,-0.342 -0.27,-0.226 -0.404,-0.53 -0.404,-0.911 0,-0.393 0.129,-0.679 0.386,-0.857 0.257,-0.179 0.654,-0.268 1.193,-0.268 h 2.172 z M 82.516,9.44 c 0.059,0.107 0.17,0.168 0.285,0.168 0.053,0 0.106,-0.013 0.156,-0.04 0.156,-0.087 0.214,-0.284 0.127,-0.442 L 80.812,4.983 C 80.726,4.826 80.528,4.768 80.372,4.855 80.215,4.941 80.158,5.139 80.244,5.296 l 2.272,4.143 z M 79.588,4.1 c 0.06,0.108 0.17,0.169 0.285,0.169 0.053,0 0.106,-0.013 0.155,-0.04 0.158,-0.087 0.215,-0.285 0.129,-0.442 L 79.227,2.093 C 79.142,1.936 78.944,1.879 78.787,1.965 78.63,2.051 78.574,2.249 78.66,2.407 Z m 6.066,7.826 c 0.038,0.147 0.17,0.245 0.314,0.245 0.027,0 0.054,-0.004 0.081,-0.01 0.173,-0.045 0.278,-0.222 0.233,-0.396 L 83.666,1.553 C 83.622,1.379 83.446,1.274 83.272,1.319 83.098,1.363 82.994,1.541 83.038,1.714 l 2.616,10.213 z M 83.4,10.38 c -0.156,0.086 -0.214,0.284 -0.128,0.442 l 0.648,1.18 c 0.059,0.108 0.17,0.17 0.284,0.17 0.053,0 0.106,-0.013 0.156,-0.041 0.157,-0.086 0.214,-0.284 0.128,-0.441 l -0.647,-1.182 c -0.087,-0.157 -0.284,-0.215 -0.44,-0.128 z m -1.18,2.323 c 0.064,0.068 0.15,0.102 0.236,0.102 0.08,0 0.16,-0.03 0.222,-0.088 0.13,-0.123 0.137,-0.329 0.015,-0.46 L 76.782,5.947 C 76.659,5.817 76.454,5.81 76.324,5.933 76.193,6.056 76.186,6.261 76.309,6.393 l 5.91,6.31 z m 6.755,-0.54 c 0.027,0.006 0.054,0.01 0.08,0.01 0.145,0 0.276,-0.098 0.314,-0.245 L 91.827,2.333 C 91.872,2.159 91.767,1.982 91.594,1.937 91.42,1.893 91.244,1.997 91.199,2.171 l -2.458,9.596 c -0.044,0.174 0.06,0.35 0.234,0.396 z m -8.844,9.52 c 0.046,0 0.093,-0.01 0.138,-0.032 l 1.367,-0.645 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 l -1.367,0.645 c -0.163,0.076 -0.232,0.27 -0.156,0.432 0.055,0.118 0.172,0.187 0.294,0.187 z m 1.367,-5.44 c 0.136,0 0.264,-0.088 0.308,-0.226 0.056,-0.17 -0.038,-0.354 -0.208,-0.41 l -6.353,-2.068 c -0.17,-0.055 -0.353,0.038 -0.408,0.208 -0.055,0.171 0.038,0.355 0.208,0.41 l 6.353,2.07 c 0.033,0.01 0.067,0.015 0.1,0.015 z m -2.817,5.439 -3.52,1.66 c -0.162,0.077 -0.232,0.27 -0.156,0.433 0.056,0.117 0.173,0.186 0.294,0.186 0.046,0 0.093,-0.01 0.138,-0.03 l 3.52,-1.661 c 0.163,-0.077 0.232,-0.27 0.156,-0.433 -0.077,-0.162 -0.27,-0.232 -0.432,-0.155 z m 3.135,-2.717 c -0.034,-0.177 -0.203,-0.292 -0.379,-0.259 l -9.755,1.866 c -0.176,0.033 -0.292,0.203 -0.258,0.38 0.03,0.156 0.165,0.264 0.318,0.264 0.02,0 0.04,-0.002 0.06,-0.006 l 9.757,-1.865 c 0.175,-0.034 0.291,-0.204 0.257,-0.38 z m -4.622,-1.415 4.284,0.27 0.02,0.001 c 0.17,0 0.313,-0.132 0.323,-0.304 0.012,-0.18 -0.124,-0.334 -0.303,-0.345 l -4.284,-0.27 c -0.178,-0.012 -0.332,0.125 -0.343,0.304 -0.012,0.179 0.124,0.333 0.303,0.344 z M 93.21,14.252 c 0.062,0.098 0.166,0.151 0.274,0.151 0.06,0 0.12,-0.016 0.173,-0.05 l 8.228,-5.236 c 0.15,-0.096 0.196,-0.297 0.1,-0.45 -0.096,-0.15 -0.296,-0.195 -0.447,-0.1 l -8.228,5.237 c -0.151,0.096 -0.196,0.297 -0.1,0.448 z m 6.54,-0.362 c -0.056,-0.171 -0.239,-0.265 -0.409,-0.21 l -5.917,1.928 c -0.17,0.055 -0.263,0.239 -0.208,0.41 0.044,0.137 0.172,0.224 0.308,0.224 0.034,0 0.068,-0.005 0.1,-0.016 l 5.917,-1.927 c 0.17,-0.055 0.264,-0.239 0.208,-0.41 z m -6.246,3.282 c -0.178,0.011 -0.314,0.166 -0.303,0.345 0.01,0.172 0.153,0.304 0.323,0.304 h 0.02 l 3.547,-0.224 c 0.18,-0.011 0.315,-0.165 0.303,-0.345 -0.01,-0.179 -0.165,-0.315 -0.343,-0.304 z m -0.118,3.834 6.2,2.924 c 0.044,0.021 0.09,0.031 0.137,0.031 0.122,0 0.238,-0.069 0.294,-0.186 0.076,-0.163 0.007,-0.356 -0.156,-0.433 l -6.198,-2.924 c -0.162,-0.076 -0.356,-0.006 -0.432,0.156 -0.076,0.162 -0.006,0.356 0.155,0.432 z m -2.725,-8.874 c 0.05,0.028 0.103,0.04 0.156,0.04 0.114,0 0.225,-0.06 0.284,-0.168 L 93.024,8.497 C 93.111,8.34 93.054,8.142 92.897,8.056 92.74,7.969 92.543,8.026 92.457,8.184 l -1.924,3.507 c -0.087,0.157 -0.029,0.355 0.128,0.441 z m -8.949,1.67 -1.408,-0.896 c -0.151,-0.096 -0.351,-0.051 -0.447,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 l 1.408,0.896 c 0.053,0.034 0.114,0.05 0.173,0.05 0.108,0 0.212,-0.053 0.274,-0.15 0.096,-0.152 0.051,-0.353 -0.1,-0.449 z m 19.148,-0.274 c 0.045,0.137 0.172,0.225 0.308,0.225 0.034,0 0.068,-0.006 0.1,-0.017 l 2.27,-0.739 c 0.17,-0.055 0.263,-0.239 0.208,-0.41 -0.055,-0.17 -0.238,-0.263 -0.409,-0.208 l -2.269,0.74 c -0.17,0.055 -0.263,0.238 -0.208,0.409 z m -7.033,-2.394 c 0.063,0.058 0.143,0.088 0.222,0.088 0.086,0 0.173,-0.035 0.237,-0.103 L 97.307,7.893 C 97.43,7.763 97.423,7.557 97.293,7.433 97.163,7.311 96.957,7.317 96.835,7.448 l -3.022,3.226 c -0.123,0.131 -0.116,0.337 0.014,0.46 z m -0.557,0.594 c -0.13,-0.123 -0.336,-0.116 -0.458,0.015 l -0.483,0.514 c -0.123,0.13 -0.116,0.336 0.014,0.46 0.062,0.058 0.142,0.087 0.222,0.087 0.087,0 0.173,-0.034 0.236,-0.102 l 0.484,-0.514 c 0.122,-0.131 0.116,-0.337 -0.015,-0.46 z m 0.16,-4.646 c 0.05,0.028 0.103,0.04 0.156,0.04 0.115,0 0.226,-0.06 0.285,-0.168 l 2.32,-4.23 C 96.277,2.566 96.22,2.368 96.063,2.282 95.906,2.196 95.709,2.252 95.623,2.41 l -2.32,4.23 c -0.087,0.158 -0.03,0.356 0.127,0.442 z m -1.858,16.395 c -0.145,0.105 -0.178,0.308 -0.072,0.453 l 1.729,2.387 c 0.063,0.087 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.146,-0.106 0.177,-0.309 0.072,-0.454 L 92.024,23.548 C 91.919,23.403 91.717,23.371 91.572,23.477 Z M 98.15,6.843 c 0.086,0 0.173,-0.034 0.236,-0.102 l 1.721,-1.837 c 0.123,-0.131 0.116,-0.337 -0.014,-0.46 -0.13,-0.123 -0.336,-0.116 -0.459,0.014 l -1.72,1.838 c -0.123,0.13 -0.117,0.336 0.013,0.46 0.063,0.058 0.143,0.087 0.223,0.087 z m -24.604,2.532 5.208,3.313 c 0.054,0.034 0.114,0.05 0.174,0.05 0.107,0 0.212,-0.053 0.274,-0.15 0.095,-0.152 0.05,-0.353 -0.1,-0.449 L 73.894,8.826 c -0.152,-0.096 -0.352,-0.051 -0.448,0.1 -0.096,0.152 -0.051,0.353 0.1,0.449 z m 20.057,23.038 c -0.066,-0.166 -0.254,-0.248 -0.42,-0.182 -0.167,0.066 -0.249,0.255 -0.183,0.422 l 0.626,1.584 c 0.05,0.128 0.173,0.206 0.302,0.206 0.04,0 0.08,-0.008 0.12,-0.023 0.165,-0.066 0.247,-0.255 0.181,-0.422 z m -2.985,-7.558 -0.424,-1.072 c -0.065,-0.167 -0.254,-0.249 -0.42,-0.183 -0.167,0.067 -0.248,0.256 -0.183,0.422 l 0.424,1.072 c 0.05,0.128 0.173,0.205 0.302,0.205 0.039,0 0.08,-0.007 0.119,-0.022 0.166,-0.067 0.248,-0.256 0.182,-0.422 z m -1.592,5.035 c 0.178,-0.022 0.304,-0.185 0.281,-0.363 l -0.714,-5.665 c -0.022,-0.178 -0.184,-0.304 -0.362,-0.282 -0.177,0.023 -0.303,0.185 -0.28,0.364 l 0.713,5.664 c 0.02,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,-0.001 0.041,-0.003 z m 0.114,0.902 c -0.178,0.022 -0.304,0.185 -0.28,0.363 l 0.416,3.31 c 0.021,0.165 0.16,0.285 0.321,0.285 0.014,0 0.028,0 0.042,-0.003 0.177,-0.022 0.303,-0.185 0.28,-0.363 l -0.416,-3.31 C 89.48,30.896 89.318,30.77 89.14,30.792 Z m 4.23,-8.48 c -0.137,-0.114 -0.341,-0.095 -0.456,0.043 -0.114,0.139 -0.095,0.344 0.043,0.458 l 6.931,5.747 c 0.06,0.05 0.134,0.074 0.207,0.074 0.093,0 0.185,-0.04 0.25,-0.118 0.114,-0.138 0.095,-0.343 -0.044,-0.457 l -6.93,-5.747 z m 11.55,-5.86 -6.456,0.406 c -0.178,0.012 -0.314,0.166 -0.303,0.345 0.01,0.172 0.154,0.305 0.323,0.305 h 0.021 L 104.96,17.1 c 0.179,-0.011 0.315,-0.166 0.303,-0.345 -0.011,-0.179 -0.164,-0.315 -0.344,-0.304 z m -1.091,4.212 -10.242,-1.959 c -0.177,-0.033 -0.346,0.082 -0.38,0.259 -0.033,0.176 0.082,0.346 0.258,0.38 l 10.242,1.958 c 0.02,0.004 0.041,0.006 0.061,0.006 0.153,0 0.289,-0.108 0.319,-0.264 0.033,-0.176 -0.083,-0.346 -0.258,-0.38 z M 87.512,0.08 c -0.179,0 -0.324,0.145 -0.324,0.325 v 2.458 c 0,0.179 0.145,0.324 0.324,0.324 0.179,0 0.324,-0.145 0.324,-0.324 V 0.405 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m 7.403,27.455 c -0.106,-0.145 -0.309,-0.177 -0.453,-0.072 -0.145,0.106 -0.177,0.309 -0.072,0.454 l 2.42,3.338 c 0.063,0.088 0.162,0.134 0.262,0.134 0.066,0 0.133,-0.02 0.19,-0.062 0.145,-0.105 0.178,-0.308 0.072,-0.454 l -2.42,-3.338 z m 8.662,-2.442 -2.269,-1.07 c -0.162,-0.077 -0.355,-0.007 -0.431,0.155 -0.077,0.163 -0.008,0.357 0.155,0.433 l 2.269,1.07 c 0.045,0.021 0.091,0.032 0.138,0.032 0.121,0 0.238,-0.07 0.293,-0.187 0.077,-0.163 0.007,-0.356 -0.155,-0.433 z m -12.36,1.279 c -0.066,-0.167 -0.254,-0.249 -0.421,-0.183 -0.166,0.067 -0.248,0.255 -0.182,0.422 l 1.736,4.397 c 0.051,0.127 0.173,0.205 0.302,0.205 0.04,0 0.08,-0.007 0.12,-0.023 0.166,-0.066 0.247,-0.255 0.181,-0.422 z m -9.105,-4.018 c -0.114,-0.139 -0.318,-0.158 -0.457,-0.043 l -6.715,5.568 c -0.138,0.114 -0.158,0.32 -0.044,0.458 0.064,0.077 0.157,0.117 0.25,0.117 0.073,0 0.146,-0.024 0.207,-0.074 l 6.716,-5.569 c 0.138,-0.114 0.157,-0.319 0.043,-0.457 z m -8.277,1.613 -2.23,1.052 c -0.162,0.076 -0.231,0.27 -0.155,0.432 0.055,0.118 0.172,0.187 0.293,0.187 0.047,0 0.094,-0.01 0.138,-0.031 l 2.23,-1.052 c 0.162,-0.076 0.231,-0.27 0.155,-0.432 -0.076,-0.162 -0.27,-0.232 -0.431,-0.156 z m 1.926,-6.508 c 0.17,0 0.312,-0.133 0.323,-0.305 0.011,-0.18 -0.124,-0.334 -0.303,-0.345 l -5.676,-0.358 c -0.179,-0.011 -0.333,0.125 -0.344,0.304 -0.011,0.18 0.125,0.334 0.303,0.345 l 5.676,0.358 h 0.021 z m -4.924,-4.674 2.732,0.89 c 0.033,0.01 0.067,0.016 0.1,0.016 0.137,0 0.264,-0.087 0.309,-0.225 0.055,-0.17 -0.038,-0.354 -0.208,-0.41 l -2.732,-0.889 c -0.17,-0.055 -0.354,0.038 -0.409,0.209 -0.055,0.17 0.038,0.354 0.208,0.41 z m 7.721,16.891 -1.552,2.141 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.057,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.047 0.263,-0.134 l 1.552,-2.14 c 0.105,-0.146 0.073,-0.35 -0.072,-0.455 -0.145,-0.105 -0.348,-0.073 -0.453,0.072 z m 4.894,-6.2 c -0.145,-0.105 -0.348,-0.073 -0.453,0.072 l -3.502,4.832 c -0.105,0.145 -0.073,0.348 0.072,0.454 0.058,0.042 0.124,0.062 0.19,0.062 0.1,0 0.2,-0.046 0.263,-0.134 l 3.502,-4.832 c 0.105,-0.145 0.073,-0.348 -0.072,-0.454 z M 85.25,23.6 c -0.166,-0.066 -0.354,0.016 -0.42,0.183 l -1.385,3.507 c -0.066,0.167 0.015,0.356 0.182,0.422 0.039,0.015 0.08,0.023 0.119,0.023 0.13,0 0.25,-0.078 0.301,-0.205 l 1.386,-3.508 C 85.498,23.856 85.417,23.667 85.25,23.6 Z m 1.543,-0.02 c -0.177,-0.022 -0.34,0.104 -0.362,0.282 l -1.442,11.442 c -0.023,0.178 0.103,0.34 0.28,0.363 l 0.042,0.003 c 0.161,0 0.3,-0.12 0.32,-0.285 l 1.443,-11.441 c 0.023,-0.179 -0.103,-0.341 -0.28,-0.364 z m 0.72,-18.765 c -0.18,0 -0.325,0.145 -0.325,0.325 v 6.707 c 0,0.179 0.145,0.325 0.324,0.325 0.179,0 0.324,-0.146 0.324,-0.325 V 5.14 c 0,-0.18 -0.145,-0.325 -0.324,-0.325 z m -4.28,23.893 c -0.166,-0.066 -0.355,0.016 -0.42,0.183 l -2.018,5.107 c -0.066,0.167 0.016,0.356 0.182,0.422 0.04,0.015 0.08,0.023 0.12,0.023 0.129,0 0.25,-0.078 0.301,-0.206 L 83.416,29.13 C 83.481,28.963 83.4,28.774 83.233,28.708 Z" transform="translate(0.741)"/>\n                </g>\n            </g>\n            <rect y="64" width="4" height="531" transform="rotate(-90 0 64)" fill="#870087"/>\n            <defs>\n                <clipPath>\n                    <rect width="181" height="65" fill="white" transform="translate(382 60)"/>\n                </clipPath>\n            </defs>\n        </svg>\n        <h1>Réponse à ta demande d’accès</h1>\n        <div class="purple-background">\n            <p>\n                <i>\n                    Dans le cadre de l’utilisation des services du pass Culture nous sommes susceptibles de collecter les données personnelles de nos utilisateurs, par exemple, pour assurer la gestion des réservations, adresser des bulletins d’actualité, lutter contre la fraude ou répondre à des demandes d’information. Le présent document te permet de prendre connaissance des données qui te concernent et qui sont utilisées pour le bon fonctionnement de nos services.\n                </i>\n            </p>\n            <p>\n                <i>\n                    Pour plus d’informations, tu peux également consulter notre <a href="https://pass.culture.fr/donnees-personnelles/">charte des données personnelles</a> ou contacter directement notre Délégué à la protection des données (DPO) : <a href="mailto:dpo@passculture.app">dpo@passculture.app</a>. \n                </i>\n            </p>\n        </div>\n        <h3>Données de l’utilisateur</h3>\n        <table class="borderless">\n            \n            \n            \n            <tr><td>Adresse de messagerie</td><td>empty@example.com</td></tr>\n            \n            \n            \n            \n            \n            \n            <tr><td>Date de création du compte</td><td>01/01/2024 00:00:00</td></tr>\n            <tr><td>Compte actif</td><td>oui</td></tr>\n            \n            \n        </table>\n\n        <h3>Informations marketing</h3>\n        <table class="borderless">\n            <tr><td>Accepte la récéption de mails</td><td>non</td></tr>\n            <tr><td>Accepte les notifications mobiles</td><td>non</td></tr>\n        </table>\n\n        \n            <h3>Historique des moyens de connexion</h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de première connexion</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Identifiant de l’appareil</td><td>a device id</td></tr>\n                    \n                    \n                </table>\n            \n        \n\n        \n            <h3>Historique des changements d’adresse de messagerie</h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de la demande</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Ancienne adresse email</td><td>oldUserEmail@example.com</td></tr>\n                    \n                </table>\n            \n        \n\n        \n            <h3>Historique des blocages du compte « pass Culture »</h3>\n            \n                <table class="borderless">\n                    <tr><td>Date</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Action</td><td>Compte suspendu</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>Validations d’identité</h3>\n            \n                <table class="borderless">\n                    <tr><td>Date de la validation</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>Moyen de la validation</td><td>Démarches simplifiées</td></tr>\n                    \n                     <tr><td>Dernière modification</td><td>01/01/2024 00:00:00</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>Crédits</h3>\n            \n                <table class="borderless">\n                    <tr><td>Date d’obtention</td><td>01/01/2024 00:00:00</td></tr>\n                    \n                    <tr><td>Valeur</td><td>300,00€</td></tr>\n                    <tr><td>Source</td><td>démarches simplifiées dossier [1234567]</td></tr>\n                    \n                    <tr><td>Type de crédit</td><td>Pass 18</td></tr>\n                </table>\n            \n        \n\n        \n            <h3>Réservations effectuées depuis l’application « pass Culture »</h3>\n            \n                <table class="borderless">\n                    <tr><td>Nom</td><td>offer_name</td></tr>\n                    <tr><td>Quantité</td><td>1</td></tr>\n                    <tr><td>Prix unitaire</td><td>13,34€</td></tr>\n                    <tr><td>Date de réservation</td><td>01/01/2024 00:00:00</td></tr>\n                    \n                    <tr><td>Date d’annulation</td><td>01/01/2024 00:00:00</td></tr>\n                    <tr><td>État</td><td>Annulé</td></tr>\n                    <tr><td>Lieu de vente</td><td>venue_name</td></tr>\n                    <tr><td>Vendeur</td><td>offerer_name</td></tr>\n                </table>\n            \n        \n    <div class="purple-background">\n        Bon à savoir : si tu souhaites récupérer ces données dans un format « interopérable » (fichier « .json »), lisible par une machine, tu peux contacter le DPO (dpo@passculture.app) afin d’exercer ton droit à la portabilité.\n    </div>\n    </body>\n</html>"""
        )


class ExtractBeneficiaryDataCommandTest(StorageFolderManager):
    # 1 extract gdpr_user_data + user
    # 2 update gdpr user data
    # 3 login device history
    # 4 user_email_history
    # 5 action_history
    # 6 beneficiary_fraud_check
    # 7 deposit
    # 8 bookings
    # 9 generate action history
    expected_queries = 9
    storage_folder = settings.LOCAL_STORAGE_DIR / settings.GCP_GDPR_EXTRACT_BUCKET / settings.GCP_GDPR_EXTRACT_FOLDER

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_nominal(self, generate_pdf_mock, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()
        with time_machine.travel("2023-12-15 10:11:00"):
            with assert_num_queries(self.expected_queries):
                result = users_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == True
        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "4"
        assert (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is not None

    def test_not_processing_expired_extract(self, clear_redis):
        redis = current_app.redis_client
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory(
            dateCreated=datetime.datetime(2023, 12, 5),
        )
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        with time_machine.travel("2023-12-15 10:11:00"):
            with assert_num_queries(1):
                result = users_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == False
        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "3"
        assert not (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is None

    def test_nothing_to_process(self, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        with time_machine.travel("2023-12-15 10:11:00"):
            with assert_num_queries(1):
                result = users_api.extract_beneficiary_data_command()

        assert result == False
        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "3"

    def test_lock_already_taken(self, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_LOCK, "locked", ex=123)
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()
        with time_machine.travel("2023-12-15 10:11:00"):
            with assert_num_queries(0):
                result = users_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == False
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_LOCK) == "locked"
        assert 0 < redis.ttl(users_constants.GDPR_EXTRACT_DATA_LOCK) <= 123
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "3"
        assert not (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is None

    def test_counter_overflow(self, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, settings.GDPR_MAX_EXTRACT_PER_DAY)
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()
        with time_machine.travel("2023-12-15 10:11:00"):
            with assert_num_queries(0):
                result = users_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == False
        assert redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == str(settings.GDPR_MAX_EXTRACT_PER_DAY)
        assert not (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is None

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", return_value=b"content of a pdf")
    def test_reset_counter_at_midnight(self, generate_pdf_mock, clear_redis):
        redis = current_app.redis_client
        extract = users_factories.GdprUserDataExtractBeneficiaryFactory()
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, settings.GDPR_MAX_EXTRACT_PER_DAY)

        with time_machine.travel("2023-12-15 00:01:00"):
            with assert_num_queries(self.expected_queries):
                result = users_api.extract_beneficiary_data_command()

        db.session.refresh(extract)
        assert result == True
        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "1"
        assert (self.storage_folder / f"{extract.id}.zip").exists()
        assert extract.dateProcessed is not None

    @mock.patch("pcapi.core.users.api.generate_pdf_from_html", side_effect=Exception)
    def test_extract_failed(self, clear_redis):
        redis = current_app.redis_client
        redis.set(users_constants.GDPR_EXTRACT_DATA_COUNTER, "3")
        users_factories.GdprUserDataExtractBeneficiaryFactory()

        with time_machine.travel("2023-12-15 10:11:00"):
            # crashes before writing the log history
            with assert_num_queries(self.expected_queries - 1):
                with pytest.raises(Exception):
                    users_api.extract_beneficiary_data_command()

        assert not redis.exists(users_constants.GDPR_EXTRACT_DATA_LOCK)
        assert redis.get(users_constants.GDPR_EXTRACT_DATA_COUNTER) == "3"
