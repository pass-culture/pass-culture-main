import datetime
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
import freezegun
import pytest
from requests.auth import _basic_auth_str

from pcapi import settings
from pcapi.admin.custom_views.beneficiary_user_view import BeneficiaryUserView
from pcapi.admin.custom_views.beneficiary_user_view import _update_underage_beneficiary_deposit_expiration_date
from pcapi.admin.custom_views.mixins.suspension_mixin import _allow_suspension_and_unsuspension
from pcapi.core import testing
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.finance.models as finance_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.testing import override_settings
from pcapi.core.users import testing as sendinblue_testing
import pcapi.core.users.factories as users_factories
from pcapi.core.users.models import User
import pcapi.notifications.push.testing as push_testing

from tests.conftest import TestClient
from tests.conftest import clean_database


@pytest.mark.usefixtures("db_session")
class BeneficiaryUserViewUnitTest:
    def test_update_underage_beneficiary_deposit_expiration_date_when_both_dates_in_the_past(self):
        three_month_in_the_past = datetime.date.today() - relativedelta(months=3)
        six_month_in_the_past = datetime.date.today() - relativedelta(months=6)

        user_previous_18th_birth_day = six_month_in_the_past
        user_new_18th_birth_day = three_month_in_the_past

        user = users_factories.UnderageBeneficiaryFactory(
            deposit__expirationDate=user_previous_18th_birth_day,
            validatedBirthDate=user_new_18th_birth_day - relativedelta(years=18),
        )

        _update_underage_beneficiary_deposit_expiration_date(user)

        assert user.deposit.expirationDate == datetime.datetime.combine(
            user_previous_18th_birth_day, datetime.datetime.min.time()
        )

    def test_update_underage_beneficiary_deposit_expiration_date_when_new_expiration_date_after_previous_one(self):
        three_month_in_the_past = datetime.date.today() - relativedelta(months=3)
        six_month_in_the_future = datetime.date.today() + relativedelta(months=6)

        user_previous_18th_birth_day = three_month_in_the_past
        user_new_18th_birth_day = six_month_in_the_future

        user = users_factories.UnderageBeneficiaryFactory(
            deposit__expirationDate=user_previous_18th_birth_day,
            validatedBirthDate=user_new_18th_birth_day - relativedelta(years=18),
        )

        _update_underage_beneficiary_deposit_expiration_date(user)

        assert user.deposit.expirationDate == datetime.datetime.combine(
            six_month_in_the_future, datetime.datetime.min.time()
        )

    @freezegun.freeze_time("2020-01-01 12:03:27")
    def test_update_underage_beneficiary_deposit_expiration_date_when_new_expiration_date_before_previous_one_and_in_the_past(
        self,
    ):
        three_month_in_the_past = datetime.date.today() - relativedelta(months=3)
        six_month_in_the_future = datetime.date.today() + relativedelta(months=6)

        user_previous_18th_birth_day = six_month_in_the_future
        user_new_18th_birth_day = three_month_in_the_past

        user = users_factories.UnderageBeneficiaryFactory(
            deposit__expirationDate=user_previous_18th_birth_day,
            validatedBirthDate=user_new_18th_birth_day - relativedelta(years=18),
        )

        _update_underage_beneficiary_deposit_expiration_date(user)

        assert user.deposit.expirationDate == datetime.datetime.utcnow()

    def test_update_underage_beneficiary_deposit_expiration_date_when_new_expiration_date_before_previous_one_and_in_the_future(
        self,
    ):
        three_month_in_the_future = datetime.date.today() + relativedelta(months=3)
        six_month_in_the_future = datetime.date.today() + relativedelta(months=6)

        user_previous_18th_birth_day = six_month_in_the_future
        user_new_18th_birth_day = three_month_in_the_future

        user = users_factories.UnderageBeneficiaryFactory(
            deposit__expirationDate=user_previous_18th_birth_day,
            validatedBirthDate=user_new_18th_birth_day - relativedelta(years=18),
        )

        _update_underage_beneficiary_deposit_expiration_date(user)

        assert user.deposit.expirationDate == datetime.datetime.combine(
            user_new_18th_birth_day, datetime.datetime.min.time()
        )


class BeneficiaryUserViewTest:
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.date.today() - relativedelta(years=18, months=4)

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_list_beneficiaries(self, mocked_validate_csrf_token, app):
        users_factories.AdminFactory(email="admin@example.com")
        users_factories.BeneficiaryGrant18Factory.create_batch(3)

        client = TestClient(app.test_client()).with_session_auth("admin@example.com")
        n_queries = testing.AUTHENTICATION_QUERIES
        n_queries += 1  # select COUNT
        n_queries += 1  # select users
        with testing.assert_num_queries(n_queries):
            response = client.get("/pc/back-office/beneficiary_users")

        assert response.status_code == 200

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_beneficiary_user_creation_for_deposit_v2(self, mocked_validate_csrf_token, app):
        users_factories.AdminFactory(email="user@example.com")

        data = dict(
            email="toto@example.com",
            firstName="Serge",
            lastName="Lama",
            validatedBirthDate=f"{self.AGE18_ELIGIBLE_BIRTH_DATE:%Y-%m-%d}",
            departementCode="93",
            postalCode="93000",
            phoneNumber="0601020304",
            depositVersion="2",
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/pc/back-office/beneficiary_users/new", form=data)

        assert response.status_code == 302

        user_created = User.query.filter_by(email="toto@example.com").one()
        assert user_created.firstName == "Serge"
        assert user_created.lastName == "Lama"
        assert user_created.publicName == "Serge Lama"
        assert user_created.validatedBirthDate == self.AGE18_ELIGIBLE_BIRTH_DATE
        assert user_created.departementCode == "93"
        assert user_created.postalCode == "93000"
        assert user_created.phoneNumber == "+33601020304"
        assert len(user_created.deposits) == 1
        assert user_created.deposit.version == 2
        assert user_created.deposit.source == "pass-culture-admin"
        assert user_created.deposit.amount == 300

        assert push_testing.requests[0]["attribute_values"]["u.credit"] == 30000

    @clean_database
    def test_the_deposit_version_is_specified(self, app, db_session):
        # Given
        beneficiary_view = BeneficiaryUserView(User, db_session)
        beneficiary_view_create_form = beneficiary_view.get_create_form()
        data = dict(
            email="toto@example.com",
            firstName="Serge",
            lastName="Lama",
            dateOfBirth=f"{self.AGE18_ELIGIBLE_BIRTH_DATE:%Y-%m-%d %H:%M:%S}",
            departementCode="93",
            postalCode="93000",
            phoneNumber="0601020304",
            depositVersion="2",
        )

        form = beneficiary_view_create_form(data=data)
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)

        # When
        beneficiary_view.on_model_change(form, user, True)

        # Then
        assert user.deposit_version == 2

    @clean_database
    @testing.override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=["admin@example.com"])
    def test_form_has_no_deposit_field_for_production(self, app, db_session):
        # We need an authenticated user to initialize the admin class
        # and call `get_create_form()`, because `scaffold_form()` is
        # called, which in turn calls the `form_columns` property,
        # which expects to see an authenticated user.
        admin = users_factories.AdminFactory()
        headers = {"Authorization": _basic_auth_str(admin.email, settings.TEST_DEFAULT_PASSWORD)}
        with app.test_request_context(headers=headers):
            form_class = BeneficiaryUserView(User, db_session)
            form = form_class.get_create_form()
        assert hasattr(form, "phoneNumber")
        assert not hasattr(form, "depositVersion")

    @clean_database
    @testing.override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=[])
    def test_beneficiary_user_creation_is_restricted_in_prod(self, app, db_session):
        users_factories.AdminFactory(email="user@example.com")

        data = dict(
            email="toto@example.com",
            firstName="Serge",
            lastName="Lama",
            dateOfBirth=f"{self.AGE18_ELIGIBLE_BIRTH_DATE:%Y-%m-%d %H:%M:%S}",
            departementCode="93",
            postalCode="93000",
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/pc/back-office/beneficiary_users/new", form=data)

        assert response.status_code == 302

        filtered_users = User.query.filter_by(email="toto@example.com").all()
        deposits = finance_models.Deposit.query.all()
        assert len(filtered_users) == 0
        assert len(deposits) == 0
        assert len(push_testing.requests) == 0

    @clean_database
    # FIXME (dbaty, 2020-12-16): I could not find a quick way to
    #  generate a valid CSRF token in tests. This should be fixed.
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_suspend_beneficiary(self, mocked_validate_csrf_token, app):
        admin = users_factories.AdminFactory(email="admin15@example.com")
        booking = bookings_factories.IndividualBookingFactory()
        beneficiary = booking.individualBooking.user

        client = TestClient(app.test_client()).with_session_auth(admin.email)
        url = f"/pc/back-office/beneficiary_users/suspend?user_id={beneficiary.id}"
        data = {
            "reason": "fraud suspicion",
            "csrf_token": "token",
        }
        response = client.post(url, form=data)

        assert response.status_code == 302
        assert not beneficiary.isActive
        assert booking.status is BookingStatus.CANCELLED

    @clean_database
    # FIXME (dbaty, 2020-12-16): I could not find a quick way to
    #  generate a valid CSRF token in tests. This should be fixed.
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_unsuspend_beneficiary(self, mocked_validate_csrf_token, app):
        admin = users_factories.AdminFactory(email="admin15@example.com")
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="user15@example.com", isActive=False)

        client = TestClient(app.test_client()).with_session_auth(admin.email)
        url = f"/pc/back-office/beneficiary_users/unsuspend?user_id={beneficiary.id}"
        data = {
            "reason": "fraud",
            "csrf_token": "token",
        }
        response = client.post(url, form=data)

        assert response.status_code == 302
        assert beneficiary.isActive

    @clean_database
    @patch("pcapi.settings.IS_PROD", True)
    def test_suspend_beneficiary_is_restricted(self, app):
        admin = users_factories.AdminFactory(email="admin@example.com")
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="user@example.com")

        client = TestClient(app.test_client()).with_session_auth(admin.email)
        url = f"/pc/back-office/beneficiary_users/suspend?user_id={beneficiary.id}"
        data = {
            "reason": "fraud",
            "csrf_token": "token",
        }
        response = client.post(url, form=data)

        assert response.status_code == 403

    @testing.override_settings(
        IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=["super-admin@example.com", "boss@example.com"]
    )
    @pytest.mark.usefixtures("db_session")
    def test_allow_suspension_and_unsuspension(self):
        basic_admin = users_factories.AdminFactory(email="admin@example.com")
        assert not _allow_suspension_and_unsuspension(basic_admin)
        super_admin = users_factories.AdminFactory(email="super-admin@example.com")
        assert _allow_suspension_and_unsuspension(super_admin)

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_beneficiary_user_edition_does_not_send_email(self, mocked_validate_csrf_token, app):
        users_factories.AdminFactory(email="user@example.com")
        user_to_edit = users_factories.BeneficiaryGrant18Factory(email="not_yet_edited@email.com")

        data = dict(
            email="edited@email.com",
            firstName=user_to_edit.firstName,
            lastName=user_to_edit.lastName,
            dateOfBirth=user_to_edit.dateOfBirth.isoformat(sep=" ", timespec="seconds"),
            departementCode=user_to_edit.departementCode,
            postalCode="76000",
        )

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/beneficiary_users/edit/?id={user_to_edit.id}", form=data)

        assert response.status_code == 302

        user_edited = User.query.filter_by(email="edited@email.com").one_or_none()
        assert user_edited is not None
        assert len(push_testing.requests) == 2

        assert not mails_testing.outbox
        assert len(push_testing.requests) == 2
        assert len(sendinblue_testing.sendinblue_requests) == 1

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("pcapi.admin.custom_views.mixins.resend_validation_email_mixin.users_api.request_email_confirmation")
    def test_resend_validation_email_to_beneficiary(
        self, mocked_request_email_confirmation, mocked_validate_csrf_token, app
    ):
        admin = users_factories.AdminFactory(email="admin@example.com")
        beneficiary = users_factories.BeneficiaryGrant18Factory(email="partner@example.com", isEmailValidated=False)
        client = TestClient(app.test_client()).with_session_auth(admin.email)

        url = f"/pc/back-office/beneficiary_users/resend-validation-email?user_id={beneficiary.id}"
        resend_validation_email_response = client.post(url, form={"csrf_token": "token"})
        assert resend_validation_email_response.status_code == 302
        mocked_request_email_confirmation.assert_called_once_with(beneficiary)


@override_settings(IS_PROD=True, SUPER_ADMIN_EMAIL_ADDRESSES=["superadmin@example.com"])
@pytest.mark.usefixtures("db_session")
class BeneficiaryUserUpdateTest:
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_update_idpiecenumber(self, token, client):
        super_admin = users_factories.AdminFactory(email="superadmin@example.com")
        client.with_session_auth(super_admin.email)

        user_to_update = users_factories.BeneficiaryGrant18Factory(departementCode="92", postalCode="92700")

        url = f"/pc/back-office/beneficiary_users/edit/?id={user_to_update.id}"
        client.post(
            url,
            form={
                "id": user_to_update.id,
                "idPieceNumber": "123123123",
                "departementCode": user_to_update.departementCode,
                "csrf_token": "token",
                "email": user_to_update.email,
                "postalCode": user_to_update.postalCode,
            },
        )

        assert user_to_update.idPieceNumber == "123123123"

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_clear_idpiecenumber(self, token, client):
        super_admin = users_factories.AdminFactory(email="superadmin@example.com")
        client.with_session_auth(super_admin.email)

        user_to_update = users_factories.BeneficiaryGrant18Factory(
            departementCode="92", postalCode="92700", idPieceNumber="123123123"
        )

        client.post(
            f"/pc/back-office/beneficiary_users/edit/?id={user_to_update.id}",
            form={
                "id": user_to_update.id,
                "idPieceNumber": "",
                "departementCode": user_to_update.departementCode,
                "csrf_token": "token",
                "email": user_to_update.email,
                "postalCode": user_to_update.postalCode,
            },
        )

        assert user_to_update.idPieceNumber is None

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_update_idpiecenumber_not_updated(self, token, client):
        admin = users_factories.AdminFactory()  # not superadmin

        user_to_update = users_factories.BeneficiaryGrant18Factory(departementCode="92", postalCode="92700")
        client.with_session_auth(admin.email)

        url = f"/pc/back-office/beneficiary_users/edit/?id={user_to_update.id}"
        client.post(
            url,
            form={
                "idPieceNumber": "123123123",
                "departementCode": user_to_update.departementCode,
                "csrf_token": "token",
                "email": user_to_update.email,
                "postalCode": user_to_update.postalCode,
            },
        )

        assert user_to_update.idPieceNumber != "123123123"

    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_clear_ine_hash(self, token, client):
        super_admin = users_factories.AdminFactory(email="superadmin@example.com")
        client.with_session_auth(super_admin.email)

        user_to_update = users_factories.BeneficiaryGrant18Factory(
            departementCode="92", postalCode="92700", ineHash="123123123"
        )

        client.post(
            f"/pc/back-office/beneficiary_users/edit/?id={user_to_update.id}",
            form={
                "id": user_to_update.id,
                "ineHash": "",
                "departementCode": user_to_update.departementCode,
                "csrf_token": "token",
                "email": user_to_update.email,
                "postalCode": user_to_update.postalCode,
            },
        )

        assert user_to_update.ineHash is None

    @patch("flask_wtf.csrf.validate_csrf")
    def test_deposit_expiration_date_updated_when_user_is_underage_beneficiary(self, token, client):
        super_admin = users_factories.AdminFactory(email="superadmin@example.com")
        client.with_session_auth(super_admin.email)

        user_to_update = users_factories.UnderageBeneficiaryFactory(departementCode="92", postalCode="92700")

        old_deposit_expiration_date = user_to_update.deposit.expirationDate
        old_user_birth_date = user_to_update.validatedBirthDate
        new_user_birth_date = old_user_birth_date + relativedelta(months=1)

        client.post(
            f"/pc/back-office/beneficiary_users/edit/?id={user_to_update.id}",
            form={
                "id": user_to_update.id,
                "validatedBirthDate": new_user_birth_date,
                "departementCode": user_to_update.departementCode,
                "csrf_token": "token",
                "email": user_to_update.email,
                "postalCode": user_to_update.postalCode,
            },
        )

        assert user_to_update.validatedBirthDate == new_user_birth_date
        assert user_to_update.deposit.expirationDate == old_deposit_expiration_date + relativedelta(months=1)
