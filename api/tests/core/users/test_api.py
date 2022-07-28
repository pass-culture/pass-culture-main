import datetime
from decimal import Decimal
from typing import Optional

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest
import requests_mock

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.payments.conf import GRANT_18_VALIDITY_IN_YEARS
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
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.user_session import UserSession
from pcapi.notifications.push import testing as batch_testing
from pcapi.routes.serialization.users import ProUserCreationBodyModel


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
        users_factories.ResetPasswordToken(user=user)
        users_factories.EmailValidationToken(user=user)

        other_user = users_factories.BeneficiaryGrant18Factory()
        other_token = users_factories.EmailValidationToken(user=other_user)

        users_api.delete_all_users_tokens(user)

        assert users_models.Token.query.one_or_none() == other_token


def _datetime_within_last_5sec(when: datetime.datetime) -> bool:
    return datetime.datetime.utcnow() - relativedelta(seconds=5) < when < datetime.datetime.utcnow()


def _assert_user_suspension_history(
    user: users_models.User,
    event_type: users_constants.SuspensionEventType,
    reason: Optional[users_constants.SuspensionReason],
    actor: users_models.User,
    expected_history_length: int = 1,
):
    assert len(user.suspension_history) == expected_history_length
    # suspension_history is sorted by ascending date, check the most recent event
    last_suspension_event = user.suspension_history[-1]
    assert last_suspension_event.userId == user.id
    assert last_suspension_event.actorUserId == actor.id
    assert last_suspension_event.eventType == event_type
    assert _datetime_within_last_5sec(last_suspension_event.eventDate)
    if reason:
        assert last_suspension_event.reasonCode == reason
    else:
        assert not last_suspension_event.reasonCode


@pytest.mark.usefixtures("db_session")
class SuspendAccountTest:
    def test_suspend_admin(self):
        user = users_factories.AdminFactory()
        users_factories.UserSessionFactory(user=user)
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION
        actor = users_factories.AdminFactory()

        users_api.suspend_account(user, reason, actor)

        assert user.suspension_reason == reason
        assert _datetime_within_last_5sec(user.suspension_date)
        assert not user.isActive
        assert not user.has_admin_role
        assert not user.has_admin_role
        assert not UserSession.query.filter_by(userId=user.id).first()
        assert actor.isActive

        _assert_user_suspension_history(user, users_constants.SuspensionEventType.SUSPENDED, reason, actor)

    def test_suspend_beneficiary(self):
        user = users_factories.BeneficiaryGrant18Factory()
        cancellable_booking = bookings_factories.IndividualBookingFactory(individualBooking__user=user)
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        confirmed_booking = bookings_factories.IndividualBookingFactory(
            individualBooking__user=user, cancellation_limit_date=yesterday, status=BookingStatus.CONFIRMED
        )
        used_booking = bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user)
        actor = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION
        old_password_hash = user.password

        users_api.suspend_account(user, reason, actor)

        db.session.refresh(user)

        assert not user.isActive
        assert user.password == old_password_hash
        assert user.suspension_reason == reason
        assert _datetime_within_last_5sec(user.suspension_date)

        assert cancellable_booking.status is BookingStatus.CANCELLED
        assert confirmed_booking.status is BookingStatus.CANCELLED
        assert used_booking.status is BookingStatus.USED

        _assert_user_suspension_history(user, users_constants.SuspensionEventType.SUSPENDED, reason, actor)

    def test_suspend_pro(self):
        booking = bookings_factories.IndividualBookingFactory()
        pro = offerers_factories.UserOffererFactory(offerer=booking.offerer).user
        actor = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION

        users_api.suspend_account(pro, reason, actor)

        assert not pro.isActive
        assert booking.status is BookingStatus.CANCELLED

        _assert_user_suspension_history(pro, users_constants.SuspensionEventType.SUSPENDED, reason, actor)

    def test_suspend_pro_with_other_offerer_users(self):
        booking = bookings_factories.IndividualBookingFactory()
        pro = offerers_factories.UserOffererFactory(offerer=booking.offerer).user
        offerers_factories.UserOffererFactory(offerer=booking.offerer)
        actor = users_factories.AdminFactory()
        reason = users_constants.SuspensionReason.FRAUD_SUSPICION

        users_api.suspend_account(pro, reason, actor)

        assert not pro.isActive
        assert booking.status is not BookingStatus.CANCELLED

        _assert_user_suspension_history(pro, users_constants.SuspensionEventType.SUSPENDED, reason, actor)


class UnsuspendAccountTest:
    def test_unsuspend_account(self):
        suspension = users_factories.UserSuspensionByFraudFactory()
        user = suspension.user

        users_api.unsuspend_account(user, suspension.actorUser)

        assert not user.suspension_reason
        assert not user.suspension_date
        assert user.isActive

        _assert_user_suspension_history(
            user, users_constants.SuspensionEventType.UNSUSPENDED, None, suspension.actorUser, expected_history_length=2
        )

    def test_bulk_unsuspend_account(self):
        actor = users_factories.AdminFactory()
        suspension1 = users_factories.UserSuspensionByFraudFactory(actorUser=actor)
        suspension2 = users_factories.UserSuspensionByFraudFactory(actorUser=actor)
        suspension3 = users_factories.UserSuspensionByFraudFactory(actorUser=actor)

        users_api.bulk_unsuspend_account([suspension1.user.id, suspension2.user.id, suspension3.user.id], actor)

        for user in [suspension1.user, suspension2.user, suspension3.user]:
            assert not user.suspension_reason
            assert not user.suspension_date
            assert user.isActive

        user_suspensions = users_models.UserSuspension.query.order_by(users_models.UserSuspension.id.asc()).all()
        assert len(user_suspensions) == 6

        user_unsuspensions = user_suspensions[3:]
        assert {event.userId for event in user_unsuspensions} == {
            suspension1.user.id,
            suspension2.user.id,
            suspension3.user.id,
        }
        for event in user_unsuspensions:
            assert event.actorUserId == actor.id
            assert event.eventType == users_constants.SuspensionEventType.UNSUSPENDED
            assert _datetime_within_last_5sec(event.eventDate)


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
        assert UserSession.query.filter_by(userId=reloaded_user.id).first() is None

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


class CreateBeneficiaryTest:
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.datetime.utcnow() - relativedelta(years=18, months=4)

    def test_with_eligible_user(self):
        user = users_factories.UserFactory(roles=[], dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        user = subscription_api.activate_beneficiary_for_eligibility(user, "test", users_models.EligibilityType.AGE18)
        assert user.has_beneficiary_role
        assert len(user.deposits) == 1

    def test_with_eligible_underage_user(self):
        user = users_factories.UserFactory(
            roles=[], dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=16, months=4)
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(registration_datetime=datetime.datetime.utcnow()),
        )
        user = subscription_api.activate_beneficiary_for_eligibility(
            user, "test", users_models.EligibilityType.UNDERAGE
        )
        assert user.has_underage_beneficiary_role
        assert len(user.deposits) == 1
        assert user.has_active_deposit
        assert user.deposit.amount == 30

    def test_apps_flyer_called(self):
        apps_flyer_data = {"apps_flyer": {"user": "some-user-id", "platform": "ANDROID"}}
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE, externalIds=apps_flyer_data)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        expected = {
            "customer_user_id": str(user.id),
            "appsflyer_id": "some-user-id",
            "eventName": "af_complete_beneficiary_registration",
            "eventValue": {"af_user_id": str(user.id)},
        }

        with requests_mock.Mocker() as mock:
            posted = mock.post("https://api2.appsflyer.com/inappevent/app.passculture.webapp")
            user = subscription_api.activate_beneficiary_for_eligibility(
                user, "test", users_models.EligibilityType.AGE18
            )

            assert posted.last_request.json() == expected

            assert user.has_beneficiary_role
            assert len(user.deposits) == 1

    def test_external_users_updated(self):
        user = users_factories.UserFactory(roles=[], dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        subscription_api.activate_beneficiary_for_eligibility(user, "test", users_models.EligibilityType.AGE18)

        assert len(batch_testing.requests) == 2
        assert len(sendinblue_testing.sendinblue_requests) == 1


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
    def should_set_user_department_to_undefined_department_code_when_offerer_has_none(self):
        # Given
        new_user = users_factories.ProFactory.build()
        offerer = create_offerer(postal_code=None)

        # When
        updated_user = users_api._set_offerer_departement_code(new_user, offerer)

        # Then
        assert updated_user.departementCode == None

    def should_set_user_department_code_based_on_offerer(self):
        # Given
        new_user = users_factories.ProFactory.build()
        offerer = create_offerer(postal_code="75019")

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

        users_api.update_user_info(user, public_name="New Name")
        user = users_models.User.query.one()
        assert user.email == "initial@example.com"
        assert user.publicName == "New Name"

        users_api.update_user_info(user, email="new@example.com")
        user = users_models.User.query.one()
        assert user.email == "new@example.com"
        assert user.publicName == "New Name"

    def test_update_user_info_sanitizes_email(self):
        user = users_factories.UserFactory(email="initial@example.com")

        users_api.update_user_info(user, email="  NEW@example.com   ")
        user = users_models.User.query.one()
        assert user.email == "new@example.com"


@pytest.mark.usefixtures("db_session")
class DomainsCreditTest:
    def test_get_domains_credit_v1(self):
        user = users_factories.BeneficiaryGrant18Factory(deposit__version=1, deposit__amount=500)

        # booking only in all domains
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
            amount=50,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
            amount=5,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )

        # booking in digital domain
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
            amount=80,
            stock__offer__subcategoryId=subcategories.JEU_EN_LIGNE.id,
            stock__offer__url="http://on.line",
        )

        # booking in physical domain
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
            amount=150,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )

        # cancelled booking
        bookings_factories.CancelledIndividualBookingFactory(
            individualBooking__user=user,
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
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
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
        bookings_factories.IndividualBookingFactory(
            individualBooking__user=user,
            amount=250,
            stock__offer__subcategoryId=subcategories.JEU_SUPPORT_PHYSIQUE.id,
        )

        with freeze_time(datetime.datetime.utcnow() + relativedelta(years=GRANT_18_VALIDITY_IN_YEARS, days=2)):
            assert users_api.get_domains_credit(user) == users_models.DomainsCredit(
                all=users_models.Credit(initial=Decimal(300), remaining=Decimal(0)),
                digital=users_models.Credit(initial=Decimal(100), remaining=Decimal(0)),
                physical=None,
            )

    def test_get_domains_credit_no_deposit(self):
        user = users_factories.UserFactory()

        assert not users_api.get_domains_credit(user)


class CreateProUserTest:
    def test_create_pro_user(self):
        pro_user_creation_body = ProUserCreationBodyModel(
            email="prouser@example.com", password="P@ssword12345", phoneNumber="0666666666"
        )

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
        pro_user_creation_body = ProUserCreationBodyModel(
            email="prouser@example.com", password="P@ssword12345", phoneNumber="0666666666"
        )

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
        user = users_factories.UserFactory(
            activity=None,
            address=None,
            city=None,
            firstName=None,
            lastName=None,
            postalCode=None,
            publicName="UNSET",
        )
        beneficiary_information = fraud_models.DMSContent(
            last_name="Doe",
            first_name="Jane",
            activity="Lycéen",
            civility=users_models.GenderEnum.F,
            birth_date=datetime.date(2000, 5, 1),
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
        assert beneficiary.publicName == "Jane Doe"
        assert beneficiary.phoneNumber == "+33612345678"
        assert beneficiary.postalCode == "67200"
        assert beneficiary.address == "11 Rue du Test"
        assert beneficiary.dateOfBirth == datetime.datetime(2000, 5, 1, 0, 0)
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
        assert new_user.dateOfBirth == datetime.datetime(2000, 5, 1, 0, 0)
        assert new_user.ineHash == "identifiantnati0naleleve"

    def test_update_user_information_from_ubble(self):
        user = users_factories.UserFactory(civility=None)
        ubble_data = fraud_factories.UbbleContentFactory(
            first_name="Raoul",
            last_name="Dufy",
            birth_date=datetime.date(2000, 5, 1).isoformat(),
            id_document_number="123456789",
            gender="M",
        )
        new_user = users_api.update_user_information_from_external_source(user, ubble_data)

        assert new_user.firstName == "Raoul"
        assert new_user.lastName == "Dufy"
        assert new_user.dateOfBirth == datetime.datetime(2000, 5, 1, 0, 0)
        assert new_user.idPieceNumber == "123456789"
        assert new_user.civility == "M."

    def test_update_id_piece_number(self):
        user = users_factories.UserFactory(activity="Etudiant", postalCode="75001", idPieceNumber=None)
        dms_data = fraud_factories.DMSContentFactory(id_piece_number="140767100016")

        users_api.update_user_information_from_external_source(user, dms_data)
        assert user.idPieceNumber == "140767100016"

    @override_features(ENABLE_PHONE_VALIDATION=True)
    def test_phone_number_does_not_update(self):

        user = users_factories.UserFactory(phoneNumber="+33611111111")
        dms_data = fraud_factories.DMSContentFactory(phoneNumber="+33622222222")

        users_api.update_user_information_from_external_source(user, dms_data)

        assert user.phoneNumber == "+33611111111"

    @override_features(ENABLE_PHONE_VALIDATION=False)
    def test_phone_number_update_if_empty(self):

        user = users_factories.UserFactory(phoneNumber=None)
        dms_data = fraud_factories.DMSContentFactory(phone="+33622222222")

        users_api.update_user_information_from_external_source(user, dms_data)

        assert user.phoneNumber == "+33622222222"

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


class PublicAccountHistoryTest:
    def test_history_contains_email_changes(self):
        # given
        user = users_factories.UserFactory()
        email_request = users_factories.EmailUpdateEntryFactory(
            user=user, creationDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
        )
        email_validation = users_factories.EmailValidationEntryFactory(
            user=user, creationDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        )

        # when
        history = users_api.public_account_history(user)

        # then
        assert len(history) == 2
        assert {
            "action": "demande de changement d'email",
            "datetime": email_request.creationDate,
            "message": (
                f"de {email_request.oldUserEmail}@{email_request.oldDomainEmail} "
                f"à {email_request.newUserEmail}@{email_request.newDomainEmail}"
            ),
        } in history
        assert {
            "action": "validation de changement d'email",
            "datetime": email_validation.creationDate,
            "message": (
                f"de {email_validation.oldUserEmail}@{email_validation.oldDomainEmail} "
                f"à {email_validation.newUserEmail}@{email_validation.newDomainEmail}"
            ),
        } in history

    def test_history_contains_suspensions(self):
        # given
        user = users_factories.UserFactory()
        actor_user = users_factories.UserFactory()
        deactivation = users_factories.UserSuspensionByFraudFactory(
            user=user,
            actorUser=actor_user,
            eventDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
            reasonCode=users_constants.SuspensionReason.FRAUD_SUSPICION,
        )
        reactivation = users_factories.UnsuspendedSuspensionFactory(
            user=user,
            actorUser=actor_user,
            eventDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=5),
        )

        # when
        history = users_api.public_account_history(user)

        # then
        assert len(history) == 2
        assert {
            "action": "désactivation de compte",
            "datetime": deactivation.eventDate,
            "message": f"par {deactivation.actorUser.publicName}: fraud suspicion",
        } in history
        assert {
            "action": "réactivation de compte",
            "datetime": reactivation.eventDate,
            "message": f"par {deactivation.actorUser.publicName}: [aucun motif renseigné]",
        } in history

    def test_history_contains_fraud_checks(self):
        # given
        user = users_factories.UserFactory()
        dms = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
        )
        phone = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
        )
        honor = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(minutes=5),
        )

        # when
        history = users_api.public_account_history(user)

        # then
        assert len(history) == 3
        assert {
            "action": "fraud check",
            "datetime": dms.dateCreated,
            "message": f"{dms.type.value}, {dms.eligibilityType.value}, {dms.status.value}, [raison inconnue], {dms.reason}",
        } in history
        assert {
            "action": "fraud check",
            "datetime": phone.dateCreated,
            "message": f"{phone.type.value}, {phone.eligibilityType.value}, {phone.status.value}, [raison inconnue], {phone.reason}",
        } in history
        assert {
            "action": "fraud check",
            "datetime": honor.dateCreated,
            "message": f"{honor.type.value}, {honor.eligibilityType.value}, {honor.status.value}, [raison inconnue], {honor.reason}",
        } in history

    def test_history_contains_reviews(self):
        # given
        user = users_factories.UserFactory()
        author_user = users_factories.UserFactory()
        ko = fraud_factories.BeneficiaryFraudReviewFactory(
            user=user,
            author=author_user,
            dateReviewed=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
            review=fraud_models.FraudReviewStatus.KO,
            reason="pas glop",
        )
        dms = fraud_factories.BeneficiaryFraudReviewFactory(
            user=user,
            author=author_user,
            dateReviewed=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
            review=fraud_models.FraudReviewStatus.REDIRECTED_TO_DMS,
            reason="",
        )

        # when
        history = users_api.public_account_history(user)

        # then
        assert len(history) == 2
        assert {
            "action": "revue manuelle",
            "datetime": ko.dateReviewed,
            "message": f"revue {ko.review.value} par {ko.author.publicName}: {ko.reason}",
        } in history
        assert {
            "action": "revue manuelle",
            "datetime": dms.dateReviewed,
            "message": f"revue {dms.review.value} par {dms.author.publicName}: {dms.reason}",
        } in history

    def test_history_contains_imports(self):
        # given
        user = users_factories.UserFactory()
        author_user = users_factories.UserFactory()
        dms = users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
            statuses=[
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.DRAFT,
                    date=datetime.datetime.utcnow() - datetime.timedelta(minutes=30),
                    author=author_user,
                    detail="c'est parti",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.ONGOING,
                    date=datetime.datetime.utcnow() - datetime.timedelta(minutes=25),
                    author=author_user,
                    detail="patience",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.REJECTED,
                    date=datetime.datetime.utcnow() - datetime.timedelta(minutes=20),
                    author=author_user,
                    detail="échec",
                ),
            ],
        )
        ubble = users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.ubble.value,
            statuses=[
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.DRAFT,
                    date=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
                    author=author_user,
                    detail="c'est reparti",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.ONGOING,
                    date=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
                    author=author_user,
                    detail="loading, please wait",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.CREATED,
                    date=datetime.datetime.utcnow() - datetime.timedelta(minutes=5),
                    author=author_user,
                    detail="félicitation",
                ),
            ],
        )

        # when
        history = users_api.public_account_history(user)

        # then
        assert len(history) == 6
        for status in dms.statuses:
            assert {
                "action": "import demarches_simplifiees",
                "datetime": status.date,
                "message": f"par {status.author.publicName}: {status.status.value} ({status.detail})",
            } in history
        for status in ubble.statuses:
            assert {
                "action": "import ubble",
                "datetime": status.date,
                "message": f"par {status.author.publicName}: {status.status.value} ({status.detail})",
            } in history

    def test_history_is_sorted_antichronologically(self):
        # given
        user = users_factories.UserFactory()
        author_user = users_factories.UserFactory()
        actor_user = users_factories.UserFactory()

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(minutes=55),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(minutes=50),
        )
        users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.ubble.value,
            statuses=[
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.DRAFT,
                    date=datetime.datetime.utcnow() - datetime.timedelta(minutes=45),
                    author=author_user,
                    detail="bonne chance",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.ONGOING,
                    date=datetime.datetime.utcnow() - datetime.timedelta(minutes=40),
                    author=author_user,
                    detail="ça vient",
                ),
                users_factories.BeneficiaryImportStatusFactory(
                    status=ImportStatus.REJECTED,
                    date=datetime.datetime.utcnow() - datetime.timedelta(minutes=20),
                    author=author_user,
                    detail="raté",
                ),
            ],
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(minutes=35),
        )
        users_factories.EmailUpdateEntryFactory(
            user=user, creationDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
        )
        users_factories.UserSuspensionByFraudFactory(
            user=user,
            actorUser=actor_user,
            eventDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=25),
            reasonCode=users_constants.SuspensionReason.FRAUD_SUSPICION,
        )
        users_factories.EmailValidationEntryFactory(
            user=user, creationDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
        )
        users_factories.UnsuspendedSuspensionFactory(
            user=user,
            actorUser=actor_user,
            eventDate=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
        )
        fraud_factories.BeneficiaryFraudReviewFactory(
            user=user,
            author=author_user,
            dateReviewed=datetime.datetime.utcnow() - datetime.timedelta(minutes=5),
            review=fraud_models.FraudReviewStatus.OK,
        )

        # when
        history = users_api.public_account_history(user)

        # then
        assert len(history) == 11
        datetimes = [item["datetime"] for item in history]
        assert datetimes == sorted(datetimes, reverse=True)
