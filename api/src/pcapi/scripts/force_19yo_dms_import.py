import logging

import click
from flask import Blueprint

from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.models import db


blueprint = Blueprint(__name__, __name__)

logger = logging.getLogger(__name__)


@blueprint.cli.command("force_19yo_dms_import")
@click.option("--dry-run/--no-dry-run", help="Dry run", default=True, type=bool)
def force_19yo_dms_import_cli(dry_run: bool = True) -> None:
    """Force the import of a user who had 18 yo at subscription time"""

    force_19yo_dms_import(dry_run=dry_run)


def force_19yo_dms_import(dry_run: bool = True) -> None:
    users = (
        users_models.User.query.join(fraud_models.BeneficiaryFraudCheck)
        .join(fraud_models.BeneficiaryFraudResult)
        .filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudResult.status == fraud_models.FraudStatus.KO,
        )
    )
    to_activate = []
    for user in users:
        if user.has_beneficiary_role:
            continue
        if (
            user.dateOfBirth
            and user.age == 19
            and users_utils.get_age_at_date(user.dateOfBirth, user.dateCreated) == 18
            and len(user.beneficiaryFraudResults) == 1
        ):
            fraud_result = user.beneficiaryFraudResults[0]
            reasons = fraud_result.reason_codes
            if len(reasons) == 1 and reasons[0] in (
                fraud_models.FraudReasonCode.ALREADY_BENEFICIARY,
                fraud_models.FraudReasonCode.NOT_ELIGIBLE,
            ):
                to_activate.append(user)
    logger.info("Needs to reactivate %d users", len(to_activate))
    if dry_run:
        return
    activated = []
    for user in to_activate:
        if user.has_beneficiary_role:
            continue
        fraud_check = (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user, type=fraud_models.FraudCheckType.DMS)
            .order_by(fraud_models.BeneficiaryFraudCheck.id.desc())
            .first()
        )
        fraud_result = user.beneficiaryFraudResults[0]
        fraud_result.reason = ""
        if fraud_result.reason_codes:
            fraud_result.reason_codes.clear()
        fraud_check.status = fraud_models.FraudCheckStatus.OK
        if fraud_check.reasonCodes:
            fraud_check.reasonCodes.clear()
        eligibility_type = users_models.EligibilityType.AGE18
        fraud_api.create_honor_statement_fraud_check(
            user, "honor statement contained in DMS application", eligibility_type
        )
        fraud_items = fraud_api.dms_fraud_checks(user, fraud_check)
        if all(fraud_item.status == fraud_models.FraudStatus.OK for fraud_item in fraud_items):
            try:
                subscription_api.on_successful_application(user, fraud_check.source_data())
            except Exception:  # pylint: disable=broad-except
                logger.warning("Cannot activate user %d", user.id, exc_info=True)
                continue
            user.comment = "Inscription forcée : Utilisateur ayant 18 ans lors de son inscription et 19 ans lors de la validation DMS"
            db.session.add(fraud_result)
            db.session.add(fraud_check)
            db.session.add(user)
            db.session.commit()
            logger.info("User %s is now activated", user.id)
            activated.append(user)
    logger.info("Users activated : %d", len(activated))
