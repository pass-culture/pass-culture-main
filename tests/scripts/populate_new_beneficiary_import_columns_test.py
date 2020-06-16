from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_beneficiary_import, \
    create_user
from scripts.populate_new_beneficiary_import_columns import populate_new_beneficiary_import_columns
from models import BeneficiaryImport, ImportStatus
from repository import repository
from models.db import Model, db
from typing import List


def create_former_beneficiary_import(*args, **kargs):
    beneficiary_import = create_beneficiary_import(*args, **kargs)

    beneficiary_import.applicationId = None
    beneficiary_import.sourceId = None
    beneficiary_import.source = None

    return beneficiary_import


def save_in_repository_without_validations(*models: List[Model]) -> None:
    for model in models:
        db.session.add(model)
    db.session.commit()


class PopulateNewBeneficiaryImportColumnsTest:
    @clean_database
    def test_should_not_change_renamed_attributes_for_valid_records(self, app):
        # Given
        beneficiary = create_user(email="first@example.com")
        beneficiary_import = create_beneficiary_import(user=beneficiary, status=ImportStatus.CREATED,
                                                       application_id=123, source_id=12, source="dms")

        beneficiary2 = create_user(email="second@example.com")
        beneficiary_import2 = create_beneficiary_import(user=beneficiary2, status=ImportStatus.CREATED,
                                                        application_id=456, source_id=42, source="jouve")

        repository.save(beneficiary_import, beneficiary_import2)

        # When
        populate_new_beneficiary_import_columns()

        # Then
        beneficiary_imports = BeneficiaryImport.query.order_by(BeneficiaryImport.demarcheSimplifieeApplicationId).all()
        assert beneficiary_imports[0].applicationId == 123
        assert beneficiary_imports[0].sourceId == 12
        assert beneficiary_imports[1].applicationId == 456
        assert beneficiary_imports[1].sourceId == 42

    @clean_database
    def test_should_fill_renamed_attributes_for_former_records(self, app):
        # Given
        beneficiary = create_user(email="first@example.com")
        former_beneficiary_import = create_former_beneficiary_import(user=beneficiary, status=ImportStatus.CREATED,
                                                                     application_id=123, source_id=12, source="dms")

        beneficiary2 = create_user(email="second@example.com")
        former_beneficiary_import2 = create_former_beneficiary_import(user=beneficiary2, status=ImportStatus.CREATED,
                                                                      application_id=456, source_id=42, source="jouve")

        save_in_repository_without_validations(former_beneficiary_import, former_beneficiary_import2)

        # When
        populate_new_beneficiary_import_columns()

        # Then
        beneficiary_imports = BeneficiaryImport.query.order_by(BeneficiaryImport.demarcheSimplifieeApplicationId).all()
        assert beneficiary_imports[0].applicationId == 123
        assert beneficiary_imports[0].sourceId == 12
        assert beneficiary_imports[1].applicationId == 456
        assert beneficiary_imports[1].sourceId == 42

    @clean_database
    def test_should_force_source_value(self, app):
        # Given
        beneficiary = create_user(email="first@example.com")
        beneficiary_import = create_beneficiary_import(user=beneficiary, status=ImportStatus.CREATED,
                                                       application_id=123, source_id=12, source="dms")

        beneficiary2 = create_user(email="second@example.com")
        former_beneficiary_import = create_former_beneficiary_import(user=beneficiary2, status=ImportStatus.CREATED,
                                                                     application_id=456, source_id=42, source="jouve")

        repository.save(beneficiary_import)
        save_in_repository_without_validations(former_beneficiary_import)

        # When
        populate_new_beneficiary_import_columns()

        # Then
        beneficiary_imports = BeneficiaryImport.query.all()
        assert beneficiary_imports[0].source == "demarches_simplifiees"
        assert beneficiary_imports[1].source == "demarches_simplifiees"
