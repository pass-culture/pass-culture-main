import datetime
from decimal import Decimal
import logging

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.categories import subcategories_v2
import pcapi.core.finance.conf as finance_conf
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.history import models as history_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import testing as sendinblue_testing
from pcapi.core.users.repository import get_user_with_valid_token
from pcapi.core.users.utils import encode_jwt_payload
from pcapi.models import db
from pcapi.notifications.push import testing as batch_testing
from pcapi.routes.native.v1.serialization import account as account_serialization
from pcapi.routes.serialization.users import ProUserCreationBodyModel

from tests.test_utils import gen_offerer_tags


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
        users_factories.PasswordResetTokenFactory(user=user)
        users_factories.EmailValidationTokenFactory(user=user)

        other_user = users_factories.BeneficiaryGrant18Factory()
        other_token = users_factories.EmailValidationTokenFactory(user=other_user)

        users_api.delete_all_users_tokens(user)

        assert users_models.Token.query.one_or_none() == other_token


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

    def test_bulk_unsuspend_account(self):
        author = users_factories.AdminFactory()
        user1 = users_factories.UserFactory(isActive=False)
        user2 = users_factories.UserFactory(isActive=False)
        user3 = users_factories.UserFactory(isActive=False)

        users_api.bulk_unsuspend_account([user1.id, user2.id, user3.id], author)

        for user in [user1, user2, user3]:
            assert not user.suspension_reason
            assert not user.suspension_date
            assert user.isActive

            history = history_models.ActionHistory.query.filter_by(userId=user.id).all()
            assert len(history) == 1
            _assert_user_action_history_as_expected(
                history[0], user, author, history_models.ActionType.USER_UNSUSPENDED, reason=None
            )
            assert _datetime_within_last_5sec(history[0].actionDate)


@pytest.mark.usefixtures("db_session")
class ChangeUserEmailTest:
    def test_change_user_email(self):
        # Given
        old_email = "oldemail@mail.com"
        user = users_factories.UserFactory(email=old_email, firstName="UniqueNameForEmailChangeTest")
        users_factories.UserSessionFactory(user=user)
        new_email = "newemail@mail.com"

        # When
        users_api.change_user_email(old_email, new_email)

        # Then
        reloaded_user = users_models.User.query.get(user.id)
        assert reloaded_user.email == new_email
        assert users_models.User.query.filter_by(email=old_email).first() is None
        assert users_models.UserSession.query.filter_by(userId=reloaded_user.id).first() is None

        assert len(reloaded_user.email_history) == 1

        history = reloaded_user.email_history[0]
        assert history.oldEmail == old_email
        assert history.newEmail == new_email
        assert history.eventType == users_models.EmailHistoryEventTypeEnum.VALIDATION
        assert history.id is not None

    def test_change_user_email_new_email_already_existing(self):
        # Given
        user = users_factories.UserFactory(email="oldemail@mail.com", firstName="UniqueNameForEmailChangeTest")
        other_user = users_factories.UserFactory(email="newemail@mail.com")

        # When
        with pytest.raises(users_exceptions.EmailExistsError):
            users_api.change_user_email(user.email, other_user.email)

        # Then
        user = users_models.User.query.get(user.id)
        assert user.email == "oldemail@mail.com"

        other_user = users_models.User.query.get(other_user.id)
        assert other_user.email == "newemail@mail.com"

    def test_change_email_user_not_existing(self):
        # When
        with pytest.raises(users_exceptions.UserDoesNotExist):
            users_api.change_user_email("oldemail@mail.com", "newemail@mail.com")

        # Then
        old_user = users_models.User.query.filter_by(email="oldemail@mail.com").first()
        assert old_user is None

        new_user = users_models.User.query.filter_by(email="newemail@mail.com").first()
        assert new_user is None

    def test_no_history_on_error(self):
        # Given
        old_email = "oldemail@mail.com"
        user = users_factories.UserFactory(email=old_email, firstName="UniqueNameForEmailChangeTest")
        users_factories.UserSessionFactory(user=user)
        new_email = "newemail@mail.com"

        # When
        with pytest.raises(users_exceptions.UserDoesNotExist):
            users_api.change_user_email(old_email + "_error", new_email)

        # Then
        reloaded_user = users_models.User.query.get(user.id)
        assert not reloaded_user.email_history

    def test_change_user_email_twice(self):
        """
        Test that when the function is called twice:
            1. no error is raised
            2. no email updated is performed (email history stays the
               same)
        Update has been done, no need to panic.
        """
        old_email = "oldemail@mail.com"
        new_email = "newemail@mail.com"

        user = users_factories.UserFactory(email=old_email)
        users_factories.UserSessionFactory(user=user)

        # first call, email is updated as expected
        users_api.change_user_email(old_email, new_email)
        db.session.commit()

        reloaded_user = users_models.User.query.get(user.id)
        assert reloaded_user.email == new_email
        assert len(reloaded_user.email_history) == 1

        # second call, no error, no update
        users_api.change_user_email(old_email, new_email)

        reloaded_user = users_models.User.query.get(user.id)
        assert reloaded_user.email == new_email
        assert len(reloaded_user.email_history) == 1


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


class FulfillBeneficiaryDataTest:
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.datetime.utcnow() - relativedelta(years=18, months=4)

    def test_fill_user_with_password_token_and_deposit(self):
        # given
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)

        # when
        user = users_api.fulfill_beneficiary_data(user, "deposit_source", users_models.EligibilityType.AGE18)

        # then
        assert isinstance(user, users_models.User)
        assert user.password is not None
        assert len(user.deposits) == 1

    def test_fill_user_with_specific_deposit_version(self):
        # given
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)

        # when
        user = users_api.fulfill_beneficiary_data(user, "deposit_source", users_models.EligibilityType.AGE18)

        # then
        assert isinstance(user, users_models.User)
        assert user.password is not None
        assert len(user.deposits) == 1
        assert user.deposit_version == 2


class FulfillAccountPasswordTest:
    def test_fill_user_with_password_token(self):
        # given
        user = users_models.User()

        # when
        user = users_api.fulfill_account_password(user)

        # then
        assert isinstance(user, users_models.User)
        assert user.password is not None
        assert len(user.deposits) == 0


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
        assert users_models.User.query.one().hasSeenProTutorials == True


@pytest.mark.usefixtures("db_session")
class SetProRgsAsSeenTest:
    def should_set_has_seen_pro_rgs_to_true_for_user(self):
        # Given
        user = users_factories.UserFactory(hasSeenProRgs=False)

        # When
        users_api.set_pro_rgs_as_seen(user)

        # Then
        assert users_models.User.query.one().hasSeenProRgs == True


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
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )
        bookings_factories.BookingFactory(
            user=user,
            amount=5,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )

        # booking in digital domain
        bookings_factories.BookingFactory(
            user=user,
            amount=80,
            stock__offer__subcategoryId=subcategories.JEU_EN_LIGNE.id,
            stock__offer__url="http://on.line",
        )

        # booking in physical domain
        bookings_factories.BookingFactory(
            user=user,
            amount=150,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )

        # cancelled booking
        bookings_factories.CancelledBookingFactory(
            user=user,
            amount=150,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
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
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
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
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
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
        pro_user_creation_body = ProUserCreationBodyModel(**self.data)

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
        pro_user_creation_body = ProUserCreationBodyModel(**self.data)

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
        user_info = ProUserCreationBodyModel(
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
        user = users_api.create_pro_user_and_offerer(user_info)

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


class SkipPhoneValidationTest:
    def test_can_skip_phone_validation(self):
        # given
        user = users_factories.UserFactory(phoneNumber="+33612345678")

        # when
        users_api.skip_phone_validation_step(user)

        # then
        assert user.phoneValidationStatus == users_models.PhoneValidationStatusType.SKIPPED_BY_SUPPORT

    def test_cannot_skip_phone_validation_when_already_validated(self):
        # given
        user = users_factories.UserFactory(
            phoneNumber="+33612345678", phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )

        # then
        with pytest.raises(phone_validation_exceptions.UserPhoneNumberAlreadyValidated):
            # when
            users_api.skip_phone_validation_step(user)

        # then
        assert user.phoneNumber == "+33612345678"
        assert user.phoneValidationStatus == users_models.PhoneValidationStatusType.VALIDATED


class UserEmailValidationTest:
    @override_features(WIP_ENABLE_NEW_ONBOARDING=False)
    def test_validate_pro_user_email_from_pro_ff_off(self):
        user_offerer = offerers_factories.UserOffererFactory(
            user__validationToken="token", user__isEmailValidated=False
        )

        users_api.validate_pro_user_email(user_offerer.user)

        assert history_models.ActionHistory.query.count() == 0
        assert user_offerer.user.validationToken is None
        assert user_offerer.user.isEmailValidated is True
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"]["id_not_prod"] == TransactionalEmail.WELCOME_TO_PRO.value.id
        )

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    def test_validate_pro_user_email_from_pro_ff_on(self):
        user_offerer = offerers_factories.UserOffererFactory(
            user__validationToken="token", user__isEmailValidated=False
        )

        users_api.validate_pro_user_email(user_offerer.user)

        assert history_models.ActionHistory.query.count() == 0
        assert user_offerer.user.validationToken is None
        assert user_offerer.user.isEmailValidated is True
        assert len(mails_testing.outbox) == 0

    @override_features(WIP_ENABLE_NEW_ONBOARDING=False)
    def test_validate_pro_user_email_from_backoffice_ff_off(self):
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
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"]["id_not_prod"] == TransactionalEmail.WELCOME_TO_PRO.value.id
        )

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
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

    def test_old_email(self):
        event = users_factories.EmailValidationEntryFactory()
        event.user.email = event.newEmail

        query = users_api.search_public_account(event.oldEmail)
        users = query.all()

        assert len(users) == 1
        assert users[0].id == event.user.id

    def test_old_email_but_not_validated(self):
        event = users_factories.EmailUpdateEntryFactory()
        # ensure that the current email is different from the event's
        # old one
        event.user.email = event.newEmail

        query = users_api.search_public_account(event.oldEmail)
        assert not query.all()

    def test_unknown_email(self):
        query = users_api.search_public_account("no@user.com")
        assert not query.all()


class SaveTrustedDeviceTest:
    def test_should_not_save_trusted_device_when_no_info_provided(self):
        user = users_factories.UserFactory(email="py@test.com")

        users_api.save_trusted_device(device_info=None, user=user)

        assert users_models.TrustedDevice.query.count() == 0

    def test_should_not_save_trusted_device_when_no_device_id_provided(self):
        user = users_factories.UserFactory(email="py@test.com")
        device_info = account_serialization.TrustedDevice(
            deviceId="",
            source="iPhone 13",
            os="iOS",
        )

        users_api.save_trusted_device(device_info=device_info, user=user)

        assert users_models.TrustedDevice.query.count() == 0

    def test_can_save_trusted_device(self):
        user = users_factories.UserFactory(email="py@test.com")
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
        user = users_factories.UserFactory(email="py@test.com")
        device_info = account_serialization.TrustedDevice(
            deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
            source="iPhone 13",
            os="iOS",
        )

        users_api.save_trusted_device(device_info=device_info, user=user)

        trusted_device = users_models.TrustedDevice.query.one()

        assert user.trusted_devices == [trusted_device]

    def test_should_log_when_no_device_id(self, caplog):
        user = users_factories.UserFactory(email="py@test.com")
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
