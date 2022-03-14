import logging

from pcapi.connectors.beneficiaries import ubble
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import requests


logger = logging.getLogger(__name__)
BATCH_SIZE = 1000


def update_gender_and_married_name_from_ubble(dry_run: bool = True) -> None:
    users_to_update: list[users_models.User] = users_models.User.query.filter(
        users_models.User.civility.is_(None),
        users_models.User.married_name.is_(None),
        users_models.User.roles.contains([users_models.UserRole.BENEFICIARY]),
        # Ubble did not send gender and married_name before January 1st 2022
        users_models.User.dateCreated > "2022-01-01",
    ).yield_per(BATCH_SIZE)

    nb_users_updated = 0

    for user in users_to_update:
        user_ubble_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.UBBLE
        ]
        if not user_ubble_fraud_checks:
            continue
        user_ubble_fraud_checks.sort(key=lambda fc: fc.dateCreated)

        latest_ubble_fraud_check = user_ubble_fraud_checks[0]
        try:
            content = ubble.get_content(latest_ubble_fraud_check.thirdPartyId)
        except requests.exceptions.HTTPError:
            logger.warning("Could not retrieve Ubble data for user %s from Ubble.", user.id)
            continue

        if content.gender is not None or content.married_name is not None:
            nb_users_updated += 1
            if not dry_run:
                user.civility = content.gender
                user.married_name = content.married_name

                if nb_users_updated % BATCH_SIZE == 0:
                    db.session.commit()

    if dry_run:
        logger.info("Would have updated %d users", nb_users_updated)
    else:
        db.session.commit()  # Commit the last batch
        logger.info("Updated %d users", nb_users_updated)
