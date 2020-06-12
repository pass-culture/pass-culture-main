from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_beneficiary_import, \
    create_user
from scripts.populate_new_beneficiary_import_columns import populate_new_beneficiary_import_columns
from models import BeneficiaryImport, ImportStatus
from repository import repository
from models.db import Model, db


class PopulateNewBeneficiaryImportColumnsTest:
    @clean_database
    def test_should_fill_all_columns(self, app):
        # Given
        beneficiary = create_user(email="first@example.com")
        beneficiary_import = create_beneficiary_import(user=beneficiary, status=ImportStatus.CREATED,
                                                       application_id=123, source_id=12, source="dms")
        beneficiary_import.applicationId = None
        beneficiary_import.sourceId = None
        beneficiary_import.source = None
        db.session.add(beneficiary_import)

        beneficiary2 = create_user(email="second@example.com")
        beneficiary_import2 = create_beneficiary_import(user=beneficiary2, status=ImportStatus.CREATED,
                                                        application_id=456, source_id=42, source="jouve")
        beneficiary_import2.applicationId = None
        beneficiary_import2.sourceId = None
        beneficiary_import2.source = None
        db.session.add(beneficiary_import2)

        db.session.commit()

        # When
        populate_new_beneficiary_import_columns()

        # Then
        beneficiary_imports = BeneficiaryImport.query.order_by(BeneficiaryImport.demarcheSimplifieeApplicationId).all()
        assert beneficiary_imports[0].applicationId == 123
        assert beneficiary_imports[0].sourceId == 12
        assert beneficiary_imports[0].source == "demarches_simplifiees"
        assert beneficiary_imports[1].applicationId == 456
        assert beneficiary_imports[1].sourceId == 42
        assert beneficiary_imports[1].source == "demarches_simplifiees"
