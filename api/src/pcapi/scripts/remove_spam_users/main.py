"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-43065-nettoyage-des-utilisateurs-crees-frauduleusement-spam-en-aout-2023 \
  -f NAMESPACE=remove_spam_users \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy.exc as sa_exc

import pcapi.core.users.models as users_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)

BATCH_SIZE = 200
USER_QUERY = db.session.query(users_models.User).filter(
    users_models.User.firstName == "gsqgsqg", users_models.User.lastName == "gqsgqs"
)


def main(batch_size: int) -> None:
    nb_user_to_delete = USER_QUERY.count()
    logger.info(
        "remove_spam_users: %s users to be deleted, starting the deletion. batch_size=%s", nb_user_to_delete, batch_size
    )
    for i in range((nb_user_to_delete // batch_size) + 1):
        try:
            with atomic():
                user_ids = [uid for (uid,) in USER_QUERY.limit(batch_size).with_entities(users_models.User.id).all()]
                USER_QUERY.filter(users_models.User.id.in_(user_ids)).delete()
        except sa_exc.OperationalError as exc:
            logger.info("Exception %s - trying to update users one by one", str(exc))
            for user_id in user_ids:
                try:
                    with atomic():
                        USER_QUERY.filter(users_models.User.id == user_id).delete()
                except sa_exc.OperationalError as exc:
                    logger.info("Exception %s - while updating user #%s", str(exc), user_id)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    args = parser.parse_args()

    main(batch_size=args.batch_size)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
