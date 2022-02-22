from pcapi.flask_app import app


app.app_context().push()

import logging

from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus


TYPE_ASSO = {
    BeneficiaryImportSources.demarches_simplifiees.value: fraud_models.FraudCheckType.DMS,
    BeneficiaryImportSources.jouve.value: fraud_models.FraudCheckType.JOUVE,
    BeneficiaryImportSources.educonnect.value: fraud_models.FraudCheckType.EDUCONNECT,
    BeneficiaryImportSources.ubble.value: fraud_models.FraudCheckType.UBBLE,
}


logger = logging.getLogger(__name__)


def migrate_bene_import():
    import_ids = [
        columns[0]
        for columns in BeneficiaryImport.query.filter(BeneficiaryImport.source != BeneficiaryImportSources.ubble.value)
        .with_entities(BeneficiaryImport.id)
        .order_by(BeneficiaryImport.id.asc())
        .all()
    ]
    index = 0
    batch_size = 1000
    created = []
    updated = []
    already_fraud_check = []
    jouve_no_third_party_id = []
    no_bene_id = []
    while index < len(import_ids):
        if index % 1000 == 0:
            logger.info("Migration script: %s/%s", index, len(import_ids))
            logger.info("Migration script: created %s", len(created))
            logger.info("Migration script: updated %s", len(updated))
            logger.info("Migration script: already_fraud_check %s", len(already_fraud_check))
            logger.info("Migration script: jouve_no_third_party_id %s", len(jouve_no_third_party_id))
            logger.info("Migration script: no_bene_id %s", len(no_bene_id))

        imports: list[BeneficiaryImport] = BeneficiaryImport.query.filter(
            BeneficiaryImport.id.in_(import_ids[index : index + batch_size])
        ).all()
        for bene_import in imports:
            if not bene_import.beneficiaryId:
                no_bene_id.append(bene_import.id)
                continue

            if not bene_import.thirdPartyId and not bene_import.applicationId:
                # some jouve cases
                fraud_checks = fraud_models.BeneficiaryFraudCheck.query.filter_by(
                    userId=bene_import.beneficiaryId, type=fraud_models.FraudCheckType.JOUVE
                ).all()
                if not fraud_checks:
                    # only 2 cases in db
                    jouve_no_third_party_id.append(bene_import.id)
                    continue
                third_party_id = f"jouve-beneficiary-import_id_{bene_import.id}"
            else:
                third_party_id = bene_import.thirdPartyId or str(bene_import.applicationId)
                fraud_checks = fraud_models.BeneficiaryFraudCheck.query.filter_by(
                    userId=bene_import.beneficiaryId, thirdPartyId=third_party_id
                ).all()

            if any([fraud_check.status for fraud_check in fraud_checks]):
                already_fraud_check.append(bene_import.id)
                continue

            fraud_check = fraud_checks[0] if fraud_checks else None

            last_status = bene_import._last_status()

            if last_status.status in (
                ImportStatus.CREATED,
                ImportStatus.REJECTED,
                ImportStatus.ERROR,
                ImportStatus.DUPLICATE,
            ):
                if bene_import.source == BeneficiaryImportSources.educonnect:
                    eligibility = users_models.EligibilityType.UNDERAGE
                else:
                    eligibility = bene_import.eligibilityType or users_models.EligibilityType.AGE18

                new_status = (
                    fraud_models.FraudCheckStatus.OK
                    if last_status.status == ImportStatus.CREATED
                    else fraud_models.FraudCheckStatus.KO
                )

                if not fraud_check:
                    created.append(bene_import.id)
                    new_check = fraud_models.BeneficiaryFraudCheck(
                        dateCreated=last_status.date,
                        userId=bene_import.beneficiaryId,
                        type=TYPE_ASSO[bene_import.source],
                        thirdPartyId=third_party_id,
                        resultContent=None,
                        status=new_status,
                        eligibilityType=eligibility,
                        reason=f"Created after migration of BeneficiaryImport id={bene_import.id} status={last_status.status}",
                    )

                elif not fraud_check.status:
                    updated.append(bene_import.id)
                    new_check = fraud_check
                    new_check.status = new_status
                    new_check.eligibilityType = eligibility
                    new_check.reason = (
                        f"Updated after migration of BeneficiaryImport id={bene_import.id} status={last_status.status}"
                    )

                if last_status.status == ImportStatus.DUPLICATE:
                    reason_codes = new_check.reasonCodes or []
                    reason_codes.append(fraud_models.FraudReasonCode.DUPLICATE_USER)
                    fraud_check.reasonCodes = reason_codes

                db.session.add(new_check)
                db.session.commit()

        index += batch_size

    logger.info("Migration script: over")
    with open("/tmp/beneficiary_import_migration_report.txt", "w+") as fp:
        fp.write("created \n")
        fp.write(str(created))
        fp.write("\n")
        fp.write("updated \n")
        fp.write(str(updated))
        fp.write("\n")
        fp.write("already_fraud_check \n")
        fp.write(str(already_fraud_check))
        fp.write("\n")
        fp.write("jouve_no_third_party_id \n")
        fp.write(str(jouve_no_third_party_id))
        fp.write("\n")
        fp.write("no_bene_id \n")
        fp.write(str(no_bene_id))
        fp.write("\n")


if __name__ == "__main__":
    migrate_bene_import()
