"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-41020-script-dn-birth-place \
  -f NAMESPACE=import_dn_birth_places \
  -f SCRIPT_ARGUMENTS="--min-id ... --max-id ... --apply";

"""

import argparse
import logging

import gql.transport.exceptions as gql_exceptions
import sqlalchemy.orm as sa_orm

from pcapi.app import app
from pcapi.connectors.dms import api as dms_connector_api
from pcapi.connectors.dms import serializer as dms_serializer
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.dms import schemas as dms_schemas
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

CHUNK_SIZE = 10_000


def _process_one(fraud_check: subscription_models.BeneficiaryFraudCheck) -> None:
    application_number = int(fraud_check.thirdPartyId)
    user = fraud_check.user

    try:
        dms_application = dms_connector_api.DMSGraphQLClient().get_single_application_details(application_number)
    except gql_exceptions.TransportQueryError as exc:
        logger.warning(
            "Error when getting DN application; skip",
            extra={"application_number": application_number, "errors": exc.errors},
        )
        return

    application_content = dms_serializer.parse_beneficiary_information_graphql(dms_application)
    if application_content.field_errors:
        logger.error(
            "Unexpected field error in DN application; skip",
            extra={"application_number": application_number, "errors": application_content.field_errors},
        )
        return

    birth_place = application_content.get_birth_place()
    if not birth_place:
        return

    logger.info(
        "Updating birth place from DS application",
        extra={
            "application_number": application_number,
            "user_id": user.id,
            "birth_place": birth_place,
            "user_birth_place": user.birthPlace,
        },
    )

    fraud_check_content = fraud_check.source_data()
    assert isinstance(fraud_check_content, dms_schemas.DMSContent)
    assert fraud_check_content.birth_place is None
    fraud_check_content.birth_place = birth_place.strip()
    fraud_check.resultContent = fraud_check_content.dict()
    db.session.add(fraud_check)

    # check already saved birth date to ensure that data is consistent
    birth_date = application_content.get_birth_date()
    if birth_date != user.validatedBirthDate:
        logger.warning(
            "Unconsistent birth date; skip",
            extra={
                "application_number": application_number,
                "user_id": user.id,
                "birth_date": birth_date.isoformat() if birth_date else None,
                "user_validated_birth_date": user.validatedBirthDate.isoformat() if user.validatedBirthDate else None,
            },
        )
        return

    # birth place may have been set from another id check (maybe later with Ubble when OK, do not overwrite)
    if user.birthPlace:
        if birth_place.lower() != user.birthPlace.lower():
            logger.warning(
                "Unconsistent birth place; skip",
                extra={
                    "application_number": application_number,
                    "user_id": user.id,
                    "birth_place": birth_place,
                    "user_birth_place": user.birthPlace,
                },
            )
    else:
        user.birthPlace = birth_place.strip()
        db.session.add(user)

        history_api.add_action(
            history_models.ActionType.INFO_MODIFIED,
            author=None,
            user=user,
            comment="PC-41020 - Rattrapage du lieu de naissance depuis le dossier DN",
            ds_dossier_id=application_number,
        )


@atomic()
def _process_chunk(min_id: int, max_id: int, apply: bool) -> None:
    if not apply:
        mark_transaction_as_invalid()

    logger.info("Processing beneficiary fraud checks from %d to %d", min_id, max_id)

    fraud_checks = (
        db.session.query(subscription_models.BeneficiaryFraudCheck)
        .join(subscription_models.BeneficiaryFraudCheck.user)
        .filter(
            subscription_models.BeneficiaryFraudCheck.id.between(min_id, max_id),
            subscription_models.BeneficiaryFraudCheck.type == subscription_models.FraudCheckType.DMS,
            subscription_models.BeneficiaryFraudCheck.status == subscription_models.FraudCheckStatus.OK,
            subscription_models.BeneficiaryFraudCheck.resultContent["birth_place"].astext.is_(None),
            users_models.User.is_beneficiary,
        )
        .options(
            sa_orm.load_only(
                subscription_models.BeneficiaryFraudCheck.thirdPartyId,
                subscription_models.BeneficiaryFraudCheck.userId,
                subscription_models.BeneficiaryFraudCheck.resultContent,
            ),
            sa_orm.contains_eager(subscription_models.BeneficiaryFraudCheck.user).load_only(
                users_models.User.id,
                users_models.User.birthPlace,
                users_models.User.validatedBirthDate,
            ),
        )
        .all()
    )

    logger.info("Found %d fraud checks to process", len(fraud_checks))

    for fraud_check in fraud_checks:
        _process_one(fraud_check)


def main(min_id: int, max_id: int, apply: bool) -> None:
    for current_max_id in range(max_id, min_id, -CHUNK_SIZE):
        _process_chunk(current_max_id - CHUNK_SIZE + 1, current_max_id, apply)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--min-id", type=int, help="Min fraud check ID", required=True)
    parser.add_argument("--max-id", type=int, help="Max fraud check ID", required=True)
    args = parser.parse_args()

    main(args.min_id, args.max_id, args.apply)

    if args.apply:
        logger.info("Finished")
    else:
        logger.info("Finished dry run, rollback")
