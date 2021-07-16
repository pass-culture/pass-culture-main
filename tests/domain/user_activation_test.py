import datetime

import pytest

from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import api as users_api
from pcapi.core.users import models as users_models
from pcapi.domain.user_activation import create_beneficiary_from_application
from pcapi.domain.user_activation import is_import_status_change_allowed
from pcapi.models import ImportStatus
from pcapi.models.db import db


class IsImportStatusChangeAllowedTest:
    @pytest.mark.parametrize(
        ["new_status", "allowed"],
        [
            (ImportStatus.REJECTED, True),
            (ImportStatus.RETRY, True),
            (ImportStatus.ERROR, False),
            (ImportStatus.CREATED, False),
        ],
    )
    def test_duplicate_can_be_rejected_or_retried(self, new_status, allowed):
        assert is_import_status_change_allowed(ImportStatus.DUPLICATE, new_status) is allowed

    @pytest.mark.parametrize(
        "new_status", [ImportStatus.DUPLICATE, ImportStatus.REJECTED, ImportStatus.CREATED, ImportStatus.RETRY]
    )
    def test_error_cannot_be_changed(self, new_status):
        assert is_import_status_change_allowed(ImportStatus.ERROR, new_status) is False

    @pytest.mark.parametrize(
        "new_status", [ImportStatus.DUPLICATE, ImportStatus.REJECTED, ImportStatus.ERROR, ImportStatus.RETRY]
    )
    def test_created_cannot_be_changed(self, new_status):
        assert is_import_status_change_allowed(ImportStatus.CREATED, new_status) is False

    @pytest.mark.parametrize(
        "new_status", [ImportStatus.DUPLICATE, ImportStatus.CREATED, ImportStatus.ERROR, ImportStatus.RETRY]
    )
    def test_rejected_cannot_be_changed(self, new_status):
        assert is_import_status_change_allowed(ImportStatus.REJECTED, new_status) is False

    @pytest.mark.parametrize(
        "new_status", [ImportStatus.DUPLICATE, ImportStatus.CREATED, ImportStatus.ERROR, ImportStatus.REJECTED]
    )
    def test_retry_cannot_be_changed(self, new_status):
        assert is_import_status_change_allowed(ImportStatus.RETRY, new_status) is False


@pytest.mark.usefixtures("db_session")
class CreateBeneficiaryFromApplicationTest:
    def test_return_newly_created_user(self):
        # given
        beneficiary_information = fraud_models.DMSContent(
            department="67",
            last_name="Doe",
            first_name="Jane",
            activity="Lycéen",
            civility="Mme",
            birth_date=datetime.date(2000, 5, 1),
            email="jane.doe@test.com",
            phone="0612345678",
            postal_code="67200",
            address="11 Rue du Test",
            application_id=123,
        )

        # when
        beneficiary = create_beneficiary_from_application(beneficiary_information, user=None)

        # Then
        assert beneficiary.lastName == "Doe"
        assert beneficiary.firstName == "Jane"
        assert beneficiary.publicName == "Jane Doe"
        assert beneficiary.email == "jane.doe@test.com"
        assert beneficiary.phoneNumber == "0612345678"
        assert beneficiary.departementCode == "67"
        assert beneficiary.postalCode == "67200"
        assert beneficiary.address == "11 Rue du Test"
        assert beneficiary.dateOfBirth == datetime.date(2000, 5, 1)
        assert not beneficiary.isBeneficiary
        assert not beneficiary.isAdmin
        assert beneficiary.password is not None
        assert beneficiary.activity == "Lycéen"
        assert beneficiary.civility == "Mme"
        assert beneficiary.hasSeenTutorials == False
        assert not beneficiary.deposits

    def test_updates_existing_user(self):
        # given
        beneficiary_information = fraud_models.DMSContent(
            department="67",
            last_name="Doe",
            first_name="Jane",
            activity="Lycéen",
            civility="Mme",
            birth_date=datetime.date(2000, 5, 1),
            email="jane.doe@test.com",
            phone="0612345678",
            postal_code="67200",
            address="11 Rue du Test",
            application_id=123,
        )

        user = users_api.create_account(
            email=beneficiary_information.email,
            password="123azerty@56",
            birthdate=beneficiary_information.birth_date,
            send_activation_mail=False,
        )
        db.session.add(user)
        db.session.flush()

        # when
        beneficiary = create_beneficiary_from_application(beneficiary_information, user=user)
        db.session.add(beneficiary)
        db.session.flush()

        # Then
        assert users_models.User.query.count() == 1
        assert beneficiary.lastName == "Doe"
        assert beneficiary.firstName == "Jane"
        assert beneficiary.publicName == "Jane Doe"
        assert beneficiary.email == "jane.doe@test.com"
        assert beneficiary.phoneNumber == "0612345678"
        assert beneficiary.departementCode == "67"
        assert beneficiary.postalCode == "67200"
        assert beneficiary.address == "11 Rue du Test"
        assert beneficiary.dateOfBirth == datetime.datetime(2000, 5, 1)
        assert not beneficiary.isBeneficiary
        assert not beneficiary.isAdmin
        assert beneficiary.password is not None
        assert beneficiary.activity == "Lycéen"
        assert beneficiary.civility == "Mme"
        assert not beneficiary.hasSeenTutorials
        assert not beneficiary.deposits
