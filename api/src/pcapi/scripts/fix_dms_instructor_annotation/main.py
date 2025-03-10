import argparse
import datetime
import logging

from pcapi.app import app
from pcapi.core.fraud import models as fraud_models
from pcapi.models import db


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    fraud_checks_query = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
        fraud_models.BeneficiaryFraudCheck.dateCreated > datetime.datetime(2025, 2, 24),
        fraud_models.BeneficiaryFraudCheck.resultContent["instructor_annotation"].is_not(None),
    ).order_by(fraud_models.BeneficiaryFraudCheck.id)

    for fraud_check in fraud_checks_query:
        logger.info("fraud check %s: %s", fraud_check.id, fraud_check.resultContent["instructor_annotation"])
        instructor_annotation = fraud_check.resultContent["instructor_annotation"]
        if instructor_annotation:
            if isinstance(instructor_annotation, str):
                fraud_check.resultContent["instructor_annotation"] = {"value": instructor_annotation}
                logger.info("==============> %s", fraud_check.resultContent["instructor_annotation"])
            elif isinstance(instructor_annotation, dict):
                if instructor_annotation["value"] is None:
                    fraud_check.resultContent["instructor_annotation"] = None
                    logger.info("==============> %s", fraud_check.resultContent["instructor_annotation"])
                elif isinstance(instructor_annotation["value"], dict):
                    fraud_check.resultContent["instructor_annotation"] = instructor_annotation["value"]
                    logger.info("==============> %s", fraud_check.resultContent["instructor_annotation"])
        db.session.add(fraud_check)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
