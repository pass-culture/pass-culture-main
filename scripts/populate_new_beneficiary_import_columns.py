from models import BeneficiaryImport, BeneficiaryImportSources, db
from utils.logger import logger


def populate_new_beneficiary_import_columns() -> None:
    logger.info("[SCRIPT] Started populating new beneficiary import columns")
    BeneficiaryImport.query.update({
        BeneficiaryImport.applicationId: BeneficiaryImport.demarcheSimplifieeApplicationId,
        BeneficiaryImport.sourceId: BeneficiaryImport.demarcheSimplifieeProcedureId,
        BeneficiaryImport.source: BeneficiaryImportSources.demarches_simplifiees.value,
    })
    db.db.session.commit()
    logger.info("[SCRIPT] Finished populating new beneficiary import columns")
