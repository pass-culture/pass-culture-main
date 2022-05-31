from datetime import date
from datetime import datetime
from datetime import time

from dateutil.relativedelta import relativedelta
from flask import url_for
import pytest

from pcapi.core.auth.api import generate_token
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.fraud import factories as fraud_factories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers import factories as offers_factories
from pcapi.core.permissions.models import Permissions
from pcapi.core.subscription import models as subscription_models
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users.factories import DepositGrantFactory
from pcapi.models.beneficiary_import_status import ImportStatus


pytestmark = pytest.mark.usefixtures("db_session")


def create_bunch_of_accounts():
    underage = users_factories.UnderageBeneficiaryFactory(
        firstName="Gédéon", lastName="Groidanlabénoir", email="gg@example.com", phoneNumber="0123456789"
    )
    grant_18 = users_factories.BeneficiaryGrant18Factory(
        firstName="Abdel Yves Akhim", lastName="Flaille", email="ayaf@example.com", phoneNumber="0516273849"
    )
    pro = users_factories.ProFactory(
        firstName="Gérard", lastName="Mentor", email="gm@example.com", phoneNumber="0246813579"
    )
    random = users_factories.UserFactory(
        firstName="Anne", lastName="Algézic", email="aa@example.com", phoneNumber="0606060606"
    )

    return underage, grant_18, pro, random


class PublicAccountSearchTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_id(self, client):
        # given
        underage, _, _, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.get(
            url_for("backoffice_blueprint.search_public_account", q=underage.id),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        assert len(response.json["accounts"]) == 1
        found_user = response.json["accounts"][0]
        assert found_user["firstName"] == underage.firstName
        assert found_user["lastName"] == underage.lastName
        assert found_user["dateOfBirth"] == underage.dateOfBirth.isoformat()
        assert found_user["id"] == underage.id
        assert found_user["email"] == underage.email
        assert found_user["phoneNumber"] == underage.phoneNumber
        assert found_user["roles"] == ["UNDERAGE_BENEFICIARY"]
        assert found_user["isActive"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_name(self, client):
        # given
        _, grant_18, _, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.get(
            url_for("backoffice_blueprint.search_public_account", q=grant_18.firstName),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        assert len(response.json["accounts"]) == 1
        found_user = response.json["accounts"][0]
        assert found_user["firstName"] == grant_18.firstName
        assert found_user["lastName"] == grant_18.lastName
        assert found_user["dateOfBirth"] == grant_18.dateOfBirth.isoformat()
        assert found_user["id"] == grant_18.id
        assert found_user["email"] == grant_18.email
        assert found_user["phoneNumber"] == grant_18.phoneNumber
        assert found_user["roles"] == ["BENEFICIARY"]
        assert found_user["isActive"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_email(self, client):
        # given
        _, _, _, random = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.get(
            url_for("backoffice_blueprint.search_public_account", q=random.email),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        assert len(response.json["accounts"]) == 1
        found_user = response.json["accounts"][0]
        assert found_user["firstName"] == random.firstName
        assert found_user["lastName"] == random.lastName
        assert found_user["dateOfBirth"] == random.dateOfBirth.isoformat()
        assert found_user["id"] == random.id
        assert found_user["email"] == random.email
        assert found_user["phoneNumber"] == random.phoneNumber
        assert found_user["roles"] == []
        assert found_user["isActive"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_search_public_account_by_phone(self, client):
        # given
        _, _, _, random = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.get(
            url_for("backoffice_blueprint.search_public_account", q=random.phoneNumber),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        assert len(response.json["accounts"]) == 1
        found_user = response.json["accounts"][0]
        assert found_user["firstName"] == random.firstName
        assert found_user["lastName"] == random.lastName
        assert found_user["dateOfBirth"] == random.dateOfBirth.isoformat()
        assert found_user["id"] == random.id
        assert found_user["email"] == random.email
        assert found_user["phoneNumber"] == random.phoneNumber
        assert found_user["roles"] == []
        assert found_user["isActive"] is True

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_search_public_account_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.get(
            url_for("backoffice_blueprint.search_public_account", q="anything"),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_search_public_account_as_anonymous(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.get(
            url_for("backoffice_blueprint.search_public_account", q="anything"),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403


class GetPublicAccountTest:
    @pytest.mark.parametrize(
        "index,expected_roles",
        [(0, ["UNDERAGE_BENEFICIARY"]), (1, ["BENEFICIARY"]), (2, ["PRO"]), (3, [])],
    )
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_public_account(self, client, index, expected_roles):
        # given
        users = create_bunch_of_accounts()
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PUBLIC_ACCOUNT])

        user = users[index]

        # when
        response = client.get(
            url_for("backoffice_blueprint.get_public_account", user_id=user.id),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        assert response.json == {
            "dateOfBirth": user.dateOfBirth.isoformat() if user.dateOfBirth else None,
            "email": user.email,
            "firstName": user.firstName,
            "id": user.id,
            "isActive": True,
            "lastName": user.lastName,
            "phoneNumber": user.phoneNumber,
            "roles": expected_roles,
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_public_account_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_session_auth(user.email).get(
            url_for("backoffice_blueprint.get_public_account", user_id=user.id),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_public_account_as_anonymous(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.get(
            url_for("backoffice_blueprint.get_public_account", user_id=1),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403


class GetBeneficiaryCreditTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_beneficiary_credit(self, client):
        # given
        _, grant_18, _, _ = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.READ_PUBLIC_ACCOUNT])

        bookings_factories.IndividualBookingFactory(
            individualBooking__user=grant_18,
            stock__offer__product=offers_factories.DigitalProductFactory(),
            amount=12.5,
        )

        # when
        response = client.get(
            url_for("backoffice_blueprint.get_beneficiary_credit", user_id=grant_18.id),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        assert response.json == {
            "initialCredit": 300.0,
            "remainingCredit": 287.5,
            "remainingDigitalCredit": 87.5,
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_non_beneficiary_credit(self, client):
        # given
        _, _, pro, random = create_bunch_of_accounts()
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [Permissions.READ_PUBLIC_ACCOUNT])

        # when
        responses = [
            client.get(
                url_for("backoffice_blueprint.get_beneficiary_credit", user_id=user.id),
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            for user in (pro, random)
        ]

        # then
        for response in responses:
            assert response.status_code == 200
            assert response.json == {
                "initialCredit": 0.0,
                "remainingCredit": 0.0,
                "remainingDigitalCredit": 0.0,
            }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_beneficiary_credit_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.get(
            url_for("backoffice_blueprint.get_beneficiary_credit", user_id=1),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_beneficiary_credit_as_anonymous(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.get(
            url_for("backoffice_blueprint.get_beneficiary_credit", user_id=1),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403


class GetUserHistoryTest:
    def _test_user_history(self, client, user) -> dict:
        # given
        admin = users_factories.UserFactory()
        auth_token = generate_token(admin, [Permissions.READ_PUBLIC_ACCOUNT])

        # when
        response = client.with_session_auth(admin.email).get(
            url_for("backoffice_blueprint.get_user_subscription_history", user_id=user.id),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        return response.json["subscriptions"]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_user_history_16y_no_subscription(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.combine(date.today(), time(0, 0)) - relativedelta(years=16, days=5)
        )

        data = self._test_user_history(client, user)

        assert data == {
            "UNDERAGE": {
                "idCheckHistory": [],
                "subscriptionItems": [
                    {"status": "ok", "type": "email-validation"},
                    {"status": "not-applicable", "type": "phone-validation"},
                    {"status": "todo", "type": "profile-completion"},
                    {"status": "todo", "type": "identity-check"},
                    {"status": "todo", "type": "honor-statement"},
                ],
            },
            "AGE18": {
                "idCheckHistory": [],
                "subscriptionItems": [
                    {"status": "ok", "type": "email-validation"},
                    {"status": "void", "type": "phone-validation"},
                    {"status": "void", "type": "profile-completion"},
                    {"status": "void", "type": "identity-check"},
                    {"status": "void", "type": "honor-statement"},
                ],
            },
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_user_history_18y_no_subscription(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.combine(date.today(), time(0, 0)) - relativedelta(years=18, days=5)
        )

        data = self._test_user_history(client, user)

        assert data == {
            "UNDERAGE": {
                "idCheckHistory": [],
                "subscriptionItems": [
                    {"status": "ok", "type": "email-validation"},
                    {"status": "not-applicable", "type": "phone-validation"},
                    {"status": "void", "type": "profile-completion"},
                    {"status": "void", "type": "identity-check"},
                    {"status": "void", "type": "honor-statement"},
                ],
            },
            "AGE18": {
                "idCheckHistory": [],
                "subscriptionItems": [
                    {"status": "ok", "type": "email-validation"},
                    {"status": "todo", "type": "phone-validation"},
                    {"status": "todo", "type": "profile-completion"},
                    {"status": "todo", "type": "identity-check"},
                    {"status": "todo", "type": "honor-statement"},
                ],
            },
        }

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_user_subscription_history_ubble(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.combine(date.today(), time(0, 0)) - relativedelta(years=18, days=5),
            activity=users_models.ActivityEnum.STUDENT.value,
        )
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED],
            resultContent=fraud_factories.UbbleContentFactory(),
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
        )

        data = self._test_user_history(client, user)

        assert data["UNDERAGE"] == {
            "idCheckHistory": [],
            "subscriptionItems": [
                {"status": "ok", "type": "email-validation"},
                {"status": "not-applicable", "type": "phone-validation"},
                {"status": "ok", "type": "profile-completion"},
                {"status": "void", "type": "identity-check"},
                {"status": "void", "type": "honor-statement"},
            ],
        }

        assert data["AGE18"]["subscriptionItems"] == [
            {"status": "ok", "type": "email-validation"},
            {"status": "ok", "type": "phone-validation"},
            {"status": "ok", "type": "profile-completion"},
            {"status": "todo", "type": "identity-check"},
            {"status": "ok", "type": "honor-statement"},
        ]

        # "idCheckHistory" contains timestamped/random data generated by factories

        assert len(data["AGE18"]["idCheckHistory"]) == 2

        assert data["AGE18"]["idCheckHistory"][0]["type"] == "ubble"
        assert data["AGE18"]["idCheckHistory"][0]["dateCreated"]
        assert data["AGE18"]["idCheckHistory"][0]["thirdPartyId"]
        assert data["AGE18"]["idCheckHistory"][0]["status"] == "suspiscious"
        assert data["AGE18"]["idCheckHistory"][0]["reason"] is None
        assert data["AGE18"]["idCheckHistory"][0]["reasonCodes"] == ["id_check_not_supported"]
        assert isinstance(data["AGE18"]["idCheckHistory"][0]["technicalDetails"], dict)

        assert data["AGE18"]["idCheckHistory"][1]["type"] == "honor_statement"
        assert data["AGE18"]["idCheckHistory"][1]["dateCreated"]
        assert data["AGE18"]["idCheckHistory"][1]["status"] == "ok"
        assert data["AGE18"]["idCheckHistory"][1]["reason"] is None
        assert not data["AGE18"]["idCheckHistory"][1]["reasonCodes"]
        assert not data["AGE18"]["idCheckHistory"][1]["technicalDetails"]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_get_user_subscription_history_dms(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.combine(date.today(), time(0, 0)) - relativedelta(years=15, days=5),
            activity=users_models.ActivityEnum.HIGH_SCHOOL_STUDENT.value,
        )

        # 15-17: no phone validation

        beneficiary_import = users_factories.BeneficiaryImportFactory(
            applicationId=24680,
            beneficiary=user,
            source=users_factories.BeneficiaryImportSources.demarches_simplifiees.value,
            sourceId=13579,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        dms_author = users_factories.UserFactory(email="dms_author@exemple.com")
        beneficiary_import.setStatus(ImportStatus.CREATED, author=dms_author)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
            thirdPartyId="24680",
            resultContent=fraud_factories.DMSContentFactory(procedure_id=13579, application_id=24680),
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
        )

        data = self._test_user_history(client, user)

        assert data["AGE18"] == {
            "idCheckHistory": [],
            "subscriptionItems": [
                {"status": "ok", "type": "email-validation"},
                {"status": "void", "type": "phone-validation"},
                {"status": "ok", "type": "profile-completion"},
                {"status": "void", "type": "identity-check"},
                {"status": "void", "type": "honor-statement"},
            ],
        }

        assert data["UNDERAGE"]["subscriptionItems"] == [
            {"status": "ok", "type": "email-validation"},
            {"status": "not-applicable", "type": "phone-validation"},
            {"status": "ok", "type": "profile-completion"},
            {"status": "ok", "type": "identity-check"},
            {"status": "ok", "type": "honor-statement"},
        ]

        # "idCheckHistory" contains timestamped/random data generated by factories

        assert len(data["UNDERAGE"]["idCheckHistory"]) == 2

        assert data["UNDERAGE"]["idCheckHistory"][0]["type"] == "dms"
        assert data["UNDERAGE"]["idCheckHistory"][0]["dateCreated"]
        assert data["UNDERAGE"]["idCheckHistory"][0]["thirdPartyId"] == "24680"
        assert data["UNDERAGE"]["idCheckHistory"][0]["status"] == "ok"
        assert data["UNDERAGE"]["idCheckHistory"][0]["reason"] is None
        assert data["UNDERAGE"]["idCheckHistory"][0]["sourceId"] == "13579"

        assert data["UNDERAGE"]["idCheckHistory"][1]["type"] == "honor_statement"
        assert data["UNDERAGE"]["idCheckHistory"][1]["dateCreated"]
        assert data["UNDERAGE"]["idCheckHistory"][1]["status"] == "ok"
        assert data["UNDERAGE"]["idCheckHistory"][1]["reason"] is None
        assert not data["UNDERAGE"]["idCheckHistory"][1]["reasonCodes"]
        assert not data["UNDERAGE"]["idCheckHistory"][1]["technicalDetails"]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_user_subscription_history_without_permission(self, client):
        # given
        user = users_factories.UserFactory()
        auth_token = generate_token(user, [])

        # when
        response = client.with_session_auth(user.email).get(
            url_for("backoffice_blueprint.get_user_subscription_history", user_id=1),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_get_user_subscription_history_as_anonymous(self, client):
        # given
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.SEARCH_PUBLIC_ACCOUNT])

        # when
        response = client.get(
            url_for("backoffice_blueprint.get_user_subscription_history", user_id=1),
            headers={"Authorization": auth_token},
        )

        # then
        assert response.status_code == 403


class PostManualReviewTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_review_ko_application(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.KO
        )
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=reviewer).first()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role is True

        dms_content = fraud_models.DMSContent(**check.resultContent)
        assert user.firstName == dms_content.first_name
        assert user.lastName == dms_content.last_name
        assert user.idPieceNumber == dms_content.id_piece_number

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user).first()
        assert fraud_check.status == check.status

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_review_dms_application(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.DMS)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=reviewer).first()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role is True
        assert len(user.deposits) == 1

        dms_content = fraud_models.DMSContent(**check.resultContent)
        assert user.firstName == dms_content.first_name
        assert user.lastName == dms_content.last_name
        assert user.idPieceNumber == dms_content.id_piece_number

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_review_educonnect_application(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=15, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=reviewer).one()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_underage_beneficiary_role
        assert len(user.deposits) == 1

        educonnect_content = fraud_models.EduconnectContent(**check.resultContent)
        assert user.firstName == educonnect_content.get_first_name()
        assert user.lastName == educonnect_content.get_last_name()
        assert user.idPieceNumber == educonnect_content.get_id_piece_number()

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_review_ubble_application(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        check = fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=reviewer).one()
        assert review.review == fraud_models.FraudReviewStatus.OK
        assert review.reason == "User is granted"
        user = users_models.User.query.get(user.id)
        assert user.has_beneficiary_role
        assert len(user.deposits) == 1

        ubble_content = fraud_models.ubble_fraud_models.UbbleContent(**check.resultContent)
        assert user.firstName == ubble_content.get_first_name()
        assert user.lastName == ubble_content.get_last_name()
        assert user.idPieceNumber == ubble_content.get_id_piece_number()

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_ko_review_does_not_activate_beneficiary(self, client):
        # given
        user = users_factories.UserFactory()
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        reviewer = users_factories.AdminFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "KO", "eligibility": None},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 200
        review = fraud_models.BeneficiaryFraudReview.query.filter_by(user=user, author=reviewer).one_or_none()
        assert review is not None
        assert review.author == reviewer
        assert review.review == fraud_models.FraudReviewStatus.KO
        assert user.has_beneficiary_role is False

        assert subscription_models.SubscriptionMessage.query.count() == 1
        message = subscription_models.SubscriptionMessage.query.first()
        assert message.popOverIcon == subscription_models.PopOverIcon.ERROR
        assert message.userMessage == "Ton dossier a été rejeté. Tu n'es malheureusement pas éligible au pass culture."

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_with_unknown_data(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None, "pouet": "coin coin"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 400

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_with_missing_data(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"review": "OK", "eligibility": None},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 400

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_without_permission(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [])

        # when
        response = client.post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_as_anonymous(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        auth_token = generate_token(users_factories.UserFactory.build(), [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 403

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_when_no_age_is_found(self, client):
        # given
        birth_date_15_yo = datetime.utcnow() - relativedelta(years=15, months=2)
        user = users_factories.UserFactory(dateOfBirth=birth_date_15_yo)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            eligibilityType=None,
            resultContent=fraud_factories.UbbleContentFactory(birth_date=birth_date_15_yo.date().isoformat()),
        )
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 412

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_unknown_account(self, client):
        # given
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.post(
            # a user with this id should not exist
            url_for("backoffice_blueprint.review_public_account", user_id=15041980),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 412

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_review_ok_already_beneficiary_account(self, client):
        # given
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18, months=2))
        fraud_factories.BeneficiaryFraudCheckFactory(user=user, type=fraud_models.FraudCheckType.UBBLE)
        DepositGrantFactory(user=user)
        reviewer = users_factories.UserFactory()
        auth_token = generate_token(reviewer, [Permissions.REVIEW_PUBLIC_ACCOUNT])

        # when
        response = client.post(
            url_for("backoffice_blueprint.review_public_account", user_id=user.id),
            json={"reason": "User is granted", "review": "OK", "eligibility": None},
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 412


class ResendValidationEmailTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_resend_validation_email(self, client):
        # given
        user = users_factories.UserFactory(isEmailValidated=False)
        backoffice_user = users_factories.UserFactory()
        auth_token = generate_token(backoffice_user, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_session_auth(backoffice_user.email).post(
            url_for("backoffice_blueprint.resend_validation_email", user_id=user.id),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 204

        # check that validation is unchanged
        updated_user: users_models.User = users_models.User.query.get(user.id)
        assert updated_user.isEmailValidated is False

        # check that a new token has been generated
        token: users_models.Token = users_models.Token.query.filter(users_models.Token.userId == user.id).one()
        assert token.type == users_models.TokenType.EMAIL_VALIDATION

        # check that email is sent
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == user.email
        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.EMAIL_CONFIRMATION.value.__dict__
        assert token.value in mails_testing.outbox[0].sent_data["params"]["CONFIRMATION_LINK"]

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_resend_validation_email_already_validated(self, client):
        # given
        pro_user = users_factories.UserFactory(isEmailValidated=True)
        backoffice_user = users_factories.UserFactory()
        auth_token = generate_token(backoffice_user, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_session_auth(backoffice_user.email).post(
            url_for("backoffice_blueprint.resend_validation_email", user_id=pro_user.id),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 400
        assert response.json["user_id"] == "L'adresse email est déjà validée"
        assert len(mails_testing.outbox) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_resend_validation_email_pro(self, client):
        # given
        pro_user = users_factories.ProFactory(isEmailValidated=False)
        backoffice_user = users_factories.UserFactory()
        auth_token = generate_token(backoffice_user, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_session_auth(backoffice_user.email).post(
            url_for("backoffice_blueprint.resend_validation_email", user_id=pro_user.id),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 400
        assert response.json["user_id"] == "Cette action n'est pas supportée pour les utilisateurs admin ou pro"
        assert len(mails_testing.outbox) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_resend_validation_email_admin(self, client):
        # given
        admin_user = users_factories.AdminFactory(isEmailValidated=False)
        backoffice_user = users_factories.UserFactory()
        auth_token = generate_token(backoffice_user, [Permissions.MANAGE_PUBLIC_ACCOUNT])

        # when
        response = client.with_session_auth(backoffice_user.email).post(
            url_for("backoffice_blueprint.resend_validation_email", user_id=admin_user.id),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 400
        assert response.json["user_id"] == "Cette action n'est pas supportée pour les utilisateurs admin ou pro"
        assert len(mails_testing.outbox) == 0

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_resend_validation_email_without_permission(self, client):
        # given
        user = users_factories.UserFactory(isEmailValidated=False)
        backoffice_user = users_factories.UserFactory()
        auth_token = generate_token(backoffice_user, [Permissions.READ_PUBLIC_ACCOUNT])

        # when
        response = client.with_session_auth(backoffice_user.email).post(
            url_for("backoffice_blueprint.resend_validation_email", user_id=user.id),
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # then
        assert response.status_code == 403
        assert len(mails_testing.outbox) == 0
