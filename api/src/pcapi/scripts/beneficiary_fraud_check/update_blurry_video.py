import time

import pcapi.core.fraud.models as fraud_models
from pcapi.models import db
from pcapi.repository import repository


def update_blurry_video(dry_run: bool = True) -> None:
    # With executing:
    # SELECT id, "reasonCodes" FROM beneficiary_fraud_check WHERE "reasonCodes" @> ARRAY['BLURRY_VIDEO'] ORDER BY id LIMIT 1
    # 11087811 appears to be the first id of beneficiary_fraud_check containing BLURRY_VIDEO in reasonCodes
    raw_query = 'SELECT id, "reasonCodes" FROM beneficiary_fraud_check WHERE id > 11087810 AND "reasonCodes" @> ARRAY[\'BLURRY_VIDEO\'];'
    before = time.time()
    query_result = db.engine.execute(raw_query)
    after = time.time()
    print(f"Query to get ids to update took {after - before:.2f}s")
    ids = [row[0] for row in query_result]
    query = fraud_models.BeneficiaryFraudCheck.query.filter(fraud_models.BeneficiaryFraudCheck.id.in_(ids))

    before = time.time()
    bfcs: list[fraud_models.BeneficiaryFraudCheck] = query.all()
    after = time.time()
    print(f"Initial query took {after - before:.2f}s")

    for bfc in bfcs:
        if not bfc.reasonCodes:
            continue
        for rc_idx, value in enumerate(bfc.reasonCodes):
            if value == fraud_models.FraudReasonCode.BLURRY_VIDEO:
                bfc.reasonCodes[rc_idx] = fraud_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO

    if dry_run:
        db.session.rollback()
    else:
        repository.save(*bfcs)
        assert all(
            fraud_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO in bfc.reasonCodes for bfc in bfcs if bfc.reasonCodes
        )
