from datetime import datetime, timedelta

from freezegun import freeze_time

from models import ImportStatus, BeneficiaryImport
from repository import repository
from repository.beneficiary_import_queries import is_already_imported, save_beneficiary_import_with_status, \
    find_applications_ids_to_retry
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_beneficiary_import


class IsAlreadyImportedTest:
    @clean_database
    def test_returns_true_when_a_beneficiary_import_exist_with_status_created(self, app):
        # given
        now = datetime.utcnow()
        user1 = create_user(date_created=now, email='user1@test.com')
        beneficiary_import = create_beneficiary_import(user=user1, status=ImportStatus.CREATED,
                                                       demarche_simplifiee_application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(123)

        # then
        assert result is True

    @clean_database
    def test_returns_true_when_a_beneficiary_import_exist_with_status_duplicate(self, app):
        # given
        now = datetime.utcnow()
        user1 = create_user(date_created=now, email='user1@test.com')
        beneficiary_import = create_beneficiary_import(user=user1, status=ImportStatus.DUPLICATE,
                                                       demarche_simplifiee_application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(123)

        # then
        assert result is True

    @clean_database
    def test_returns_true_when_a_beneficiary_import_exist_with_status_rejected(self, app):
        # given
        now = datetime.utcnow()
        user1 = create_user(date_created=now, email='user1@test.com')
        beneficiary_import = create_beneficiary_import(user=user1, status=ImportStatus.REJECTED,
                                                       demarche_simplifiee_application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(123)

        # then
        assert result is True

    @clean_database
    def test_returns_true_when_a_beneficiary_import_exist_with_status_error(self, app):
        # given
        now = datetime.utcnow()
        user1 = create_user(date_created=now, email='user1@test.com')
        beneficiary_import = create_beneficiary_import(user=user1, status=ImportStatus.ERROR,
                                                       demarche_simplifiee_application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(123)

        # then
        assert result is True

    @clean_database
    def test_returns_false_when_a_beneficiary_import_exist_with_status_retry(self, app):
        # given
        now = datetime.utcnow()
        user1 = create_user(date_created=now, email='user1@test.com')
        beneficiary_import = create_beneficiary_import(user=user1, status=ImportStatus.RETRY,
                                                       demarche_simplifiee_application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(123)

        # then
        assert result is False

    @clean_database
    def test_returns_false_when_no_beneficiary_import_exist_for_this_id(self, app):
        # given
        now = datetime.utcnow()
        user1 = create_user(date_created=now, email='user1@test.com')
        beneficiary_import = create_beneficiary_import(user=user1, status=ImportStatus.CREATED,
                                                       demarche_simplifiee_application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(456)

        # then
        assert result is False


class SaveBeneficiaryImportWithStatusTest:
    @clean_database
    def test_a_status_is_set_on_a_new_import(self, app):
        # when
        save_beneficiary_import_with_status(ImportStatus.DUPLICATE, 123, user=None)

        # then
        beneficiary_import = BeneficiaryImport.query.filter_by(demarcheSimplifieeApplicationId=123).first()
        assert beneficiary_import.currentStatus == ImportStatus.DUPLICATE

    @clean_database
    def test_a_status_is_set_on_an_existing_import(self, app):
        # given
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        with freeze_time(two_days_ago):
            save_beneficiary_import_with_status(ImportStatus.DUPLICATE, 123, user=None)
        user = create_user()

        # when
        save_beneficiary_import_with_status(ImportStatus.CREATED, 123, user=user)

        # then
        beneficiary_imports = BeneficiaryImport.query.filter_by(demarcheSimplifieeApplicationId=123).all()
        assert len(beneficiary_imports) == 1
        assert beneficiary_imports[0].currentStatus == ImportStatus.CREATED
        assert beneficiary_imports[0].beneficiary == user

    @clean_database
    def test_should_not_delete_beneficiary_when_import_already_exists(self, app):
        # Given
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        beneficiary = create_user()
        with freeze_time(two_days_ago):
            save_beneficiary_import_with_status(ImportStatus.CREATED, 123, user=beneficiary)

        # When
        save_beneficiary_import_with_status(ImportStatus.REJECTED, 123, user=None)

        # Then
        beneficiary_imports = BeneficiaryImport.query.filter_by(demarcheSimplifieeApplicationId=123).first()
        assert beneficiary_imports.beneficiary == beneficiary


class FindApplicationsIdsToRetryTest:
    @clean_database
    def test_returns_applications_ids_with_current_status_retry(self, app):
        # given
        import1 = create_beneficiary_import(status=ImportStatus.RETRY, demarche_simplifiee_application_id=456)
        import2 = create_beneficiary_import(status=ImportStatus.RETRY, demarche_simplifiee_application_id=123)
        user = create_user(email='user1@test.com')
        import3 = create_beneficiary_import(user=user, status=ImportStatus.CREATED, demarche_simplifiee_application_id=789)

        repository.save(import1, import2, import3)

        # when
        ids = find_applications_ids_to_retry()

        # then
        assert ids == [123, 456]

    @clean_database
    def test_returns_an_empty_list_if_no_retry_imports_exist(self, app):
        # given
        import1 = create_beneficiary_import(status=ImportStatus.DUPLICATE, demarche_simplifiee_application_id=456)
        import2 = create_beneficiary_import(status=ImportStatus.ERROR, demarche_simplifiee_application_id=123)
        user = create_user(email='user1@test.com')
        import3 = create_beneficiary_import(user=user, status=ImportStatus.CREATED, demarche_simplifiee_application_id=789)

        repository.save(import1, import2, import3)

        # when
        ids = find_applications_ids_to_retry()

        # then
        assert not ids
