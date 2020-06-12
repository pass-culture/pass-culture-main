from models import BeneficiaryImport, BeneficiaryImportSources
from utils.logger import logger


def populate_new_beneficiary_import_columns():
    logger.info("[SCRIPT] Started populating new beneficiary import columns")
    BeneficiaryImport.query.update({
        BeneficiaryImport.applicationId: BeneficiaryImport.demarcheSimplifieeApplicationId,
        BeneficiaryImport.sourceId: BeneficiaryImport.demarcheSimplifieeProcedureId,
        BeneficiaryImport.source: BeneficiaryImportSources.demarches_simplifiees.value,
    })
    logger.info("[SCRIPT] Finished populating new beneficiary import columns")
