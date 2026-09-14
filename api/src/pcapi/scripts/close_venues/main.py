"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-43116-script-fermeture-des-venues \
  -f NAMESPACE=close_venues \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.repository as offerers_repository
import pcapi.core.users.repository as users_repository
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

CLOSING_COMMENT = "(PC-43116) Script de fermeture des venues notées comme fermées"


def main(venue_ids: list[int], apply: bool, email: str) -> None:
    author = users_repository.find_user_by_email(email=email)
    assert author
    for venue_id in venue_ids:
        with atomic():
            venue = offerers_repository.find_venue_by_id(venue_id)
            assert venue, venue_id
            offerers_api.close_venue(venue=venue, author=author, comment=CLOSING_COMMENT)
            if not apply:
                mark_transaction_as_invalid()


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--venue-ids",
        type=int,
        required=True,
        nargs="+",
    )
    parser.add_argument("--email", required=True)
    args = parser.parse_args()

    main(venue_ids=args.venue_ids, apply=args.apply, email=args.email)

    if args.apply:
        logger.info("Finished")
    else:
        logger.info("Finished dry run, rollback")
