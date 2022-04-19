from contextlib import suppress
import logging

import click
from sqlalchemy.orm import contains_eager

from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.models import db
from pcapi.utils.blueprint import Blueprint


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
        .filter(
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
            fraud_models.BeneficiaryFraudCheck.status == FraudCheckStatus.KO,
        )
        .options(contains_eager(users_models.User.beneficiaryFraudChecks))
    )
    to_activate = []
    for user in users:
        if user.has_beneficiary_role:
            continue
        user_dms_fraud_checks = [fc for fc in user.beneficiaryFraudChecks if fc.type == fraud_models.FraudCheckType.DMS]
        if (
            user.dateOfBirth
            and user.age == 19
            and users_utils.get_age_at_date(user.dateOfBirth, user.dateCreated) == 18
            and len(user_dms_fraud_checks) == 1
        ):
            fraud_check = user_dms_fraud_checks[0]
            reasons = fraud_check.reasonCodes
            valid_reasons = (
                fraud_models.FraudReasonCode.ALREADY_BENEFICIARY,
                fraud_models.FraudReasonCode.NOT_ELIGIBLE,
            )
            with suppress(TypeError, KeyError):
                if len(reasons) == 1 and reasons[0] in valid_reasons:
                    to_activate.append(user)
    logger.info("Needs to reactivate %d users", len(to_activate))
    if dry_run:
        print("Needs to reactivate users: %s" % to_activate)
        return
    activated = []
    not_activated = []
    for user in to_activate:
        if user.has_beneficiary_role:
            continue
        fraud_check = [fc for fc in user.beneficiaryFraudChecks if fc.type == fraud_models.FraudCheckType.DMS][0]
        fraud_check.reason = ""
        if fraud_check.reasonCodes:
            fraud_check.reasonCodes = None
        fraud_check.status = FraudCheckStatus.OK
        eligibility_type = users_models.EligibilityType.AGE18
        fraud_check.eligibilityType = eligibility_type
        fraud_api.create_honor_statement_fraud_check(
            user, "honor statement contained in DMS application", eligibility_type
        )
        content = fraud_check.source_data()
        fraud_items = fraud_api.dms_fraud_checks(user, content)
        fraud_items.append(
            fraud_api._duplicate_user_fraud_item(
                content.get_first_name(), content.get_last_name(), content.get_married_name(), user.dateOfBirth, user.id
            )
        )
        if all(fraud_item.status == fraud_models.FraudStatus.OK for fraud_item in fraud_items):
            try:
                subscription_api.on_successful_application(user, content)
            except Exception:  # pylint: disable=broad-except
                logger.warning("Cannot activate user %d", user.id, exc_info=True)
                continue
            user.comment = "Inscription forcée : Utilisateur ayant 18 ans lors de son inscription et 19 ans lors de la validation DMS"
            db.session.add(fraud_check)
            db.session.add(user)
            db.session.commit()
            logger.info("User %s is now activated", user.id)
            activated.append(user.id)
        else:
            logger.info("Cannot activate user %d", user.id)
            not_activated.append(user.id)

    logger.info("Users activated : %d", len(activated))
    logger.info("Users not activated : %d", len(not_activated))

    print("UserIds activated : %s" % activated)
    print("UserIds not activated : %s" % not_activated)
