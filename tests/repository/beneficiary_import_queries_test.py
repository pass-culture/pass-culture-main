from datetime import datetime, timedelta

from freezegun import freeze_time

from models import BeneficiaryImport, ImportStatus, BeneficiaryImportSources
from repository import repository
from repository.beneficiary_import_queries import \
    find_applications_ids_to_retry, is_already_imported, \
    save_beneficiary_import_with_status
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_beneficiary_import, \
    create_user


class IsAlreadyImportedTest:
    @clean_database
    def test_returns_true_when_a_beneficiary_import_exist_with_status_created(self, app):
        # given
        now = datetime.utcnow()
        beneficiary = create_user(date_created=now)
        beneficiary_import = create_beneficiary_import(user=beneficiary, status=ImportStatus.CREATED,
                                                       application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(123)

        # then
        assert result is True

    @clean_database
    def test_returns_true_when_a_beneficiary_import_exist_with_status_duplicate(self, app):
        # given
        now = datetime.utcnow()
        beneficiary = create_user(date_created=now)
        beneficiary_import = create_beneficiary_import(user=beneficiary,
                                                       status=ImportStatus.DUPLICATE,
                                                       application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(123)

        # then
        assert result is True

    @clean_database
    def test_returns_true_when_a_beneficiary_import_exist_with_status_rejected(self, app):
        # given
        now = datetime.utcnow()
        beneficiary = create_user(date_created=now)
        beneficiary_import = create_beneficiary_import(user=beneficiary,
                                                       status=ImportStatus.REJECTED,
                                                       application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(123)

        # then
        assert result is True

    @clean_database
    def test_returns_true_when_a_beneficiary_import_exist_with_status_error(self, app):
        # given
        now = datetime.utcnow()
        beneficiary = create_user(date_created=now)
        beneficiary_import = create_beneficiary_import(user=beneficiary,
                                                       status=ImportStatus.ERROR,
                                                       application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(123)

        # then
        assert result is True

    @clean_database
    def test_returns_false_when_a_beneficiary_import_exist_with_status_retry(self, app):
        # given
        now = datetime.utcnow()
        beneficiary = create_user(date_created=now)
        beneficiary_import = create_beneficiary_import(user=beneficiary,
                                                       status=ImportStatus.RETRY,
                                                       application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(123)

        # then
        assert result is False

    @clean_database
    def test_returns_false_when_no_beneficiary_import_exist_for_this_id(self, app):
        # given
        now = datetime.utcnow()
        beneficiary = create_user(date_created=now)
        beneficiary_import = create_beneficiary_import(user=beneficiary,
                                                       status=ImportStatus.CREATED,
                                                       application_id=123)

        repository.save(beneficiary_import)

        # when
        result = is_already_imported(456)

        # then
        assert result is False


class SaveBeneficiaryImportWithStatusTest:
    @clean_database
    def test_a_status_is_set_on_a_new_import(self, app):
        # when
        save_beneficiary_import_with_status(ImportStatus.DUPLICATE, 123, source=BeneficiaryImportSources.demarches_simplifiees, source_id=14562,
                                            user=None)

        # then
        beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=123).first()
        assert beneficiary_import.currentStatus == ImportStatus.DUPLICATE

    @clean_database
    def test_a_beneficiary_import_is_saved_with_all_fields(self, app):
        # when
        save_beneficiary_import_with_status(ImportStatus.DUPLICATE, 123, source=BeneficiaryImportSources.demarches_simplifiees, source_id=145236,
                                            user=None)

        # then
        beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=123).first()
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.sourceId == 145236
        assert beneficiary_import.source == "demarches_simplifiees"

    @clean_database
    def test_a_status_is_set_on_an_existing_import(self, app):
        # given
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        with freeze_time(two_days_ago):
            save_beneficiary_import_with_status(ImportStatus.DUPLICATE, 123, source=BeneficiaryImportSources.demarches_simplifiees, source_id=14562,
                                                user=None)
        beneficiary = create_user()

        # when
        save_beneficiary_import_with_status(ImportStatus.CREATED, 123, source=BeneficiaryImportSources.demarches_simplifiees, source_id=14562,
                                            user=beneficiary)

        # then
        beneficiary_imports = BeneficiaryImport.query.filter_by(applicationId=123).all()
        assert len(beneficiary_imports) == 1
        assert beneficiary_imports[0].currentStatus == ImportStatus.CREATED
        assert beneficiary_imports[0].beneficiary == beneficiary

    @clean_database
    def test_should_not_delete_beneficiary_when_import_already_exists(self, app):
        # Given
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        beneficiary = create_user()
        with freeze_time(two_days_ago):
            save_beneficiary_import_with_status(ImportStatus.CREATED, 123, source=BeneficiaryImportSources.demarches_simplifiees, source_id=14562,
                                                user=beneficiary)

        # When
        save_beneficiary_import_with_status(ImportStatus.REJECTED, 123, source=BeneficiaryImportSources.demarches_simplifiees, source_id=14562,
                                            user=None)

        # Then
        beneficiary_imports = BeneficiaryImport.query.filter_by(applicationId=123).first()
        assert beneficiary_imports.beneficiary == beneficiary


class FindApplicationsIdsToRetryTest:
    @clean_database
    def test_returns_applications_ids_with_current_status_retry(self, app):
        # given
        beneficiary = create_user()
        imports = [
            create_beneficiary_import(status=ImportStatus.RETRY, application_id=456),
            create_beneficiary_import(status=ImportStatus.RETRY, application_id=123),
            create_beneficiary_import(user=beneficiary, status=ImportStatus.CREATED, application_id=789)
        ]

        repository.save(*imports)

        # when
        ids = find_applications_ids_to_retry()

        # then
        assert ids == [123, 456]

    @clean_database
    def test_returns_an_empty_list_if_no_retry_imports_exist(self, app):
        # given
        beneficiary = create_user()
        imports = [
            create_beneficiary_import(status=ImportStatus.DUPLICATE, application_id=456),
            create_beneficiary_import(status=ImportStatus.ERROR, application_id=123),
            create_beneficiary_import(user=beneficiary, status=ImportStatus.CREATED, application_id=789)
        ]

        repository.save(*imports)

        # when
        ids = find_applications_ids_to_retry()

        # then
        assert not ids
