"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-39484-rpa-script-validate-collecive-offers \
  -f NAMESPACE=validate_collective_offer \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
from traceback import print_exc

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def validate_offer(author_id: int, offer_id: int) -> None:
    collective_offer = (
        db.session.query(educational_models.CollectiveOffer)
        .filter(
            educational_models.CollectiveOffer.id == offer_id,
            educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.PENDING,
        )
        .one()
    )

    old_validation_status = collective_offer.validation
    new_validation_status = offer_mixin.OfferValidationStatus.APPROVED
    collective_offer.validation = new_validation_status
    collective_offer.lastValidationDate = date_utils.get_naive_utc_now()
    collective_offer.lastValidationType = offer_mixin.OfferValidationType.MANUAL
    collective_offer.lastValidationAuthorUserId = author_id
    collective_offer.isActive = True
    collective_offer.rejectionReason = None

    db.session.flush()

    recipients = (
        [collective_offer.venue.bookingEmail]
        if collective_offer.venue.bookingEmail
        else [recipient.user.email for recipient in collective_offer.venue.managingOfferer.UserOfferers]
    )

    offer_data = transactional_mails.get_email_data_from_offer(
        collective_offer, old_validation_status, new_validation_status
    )
    transactional_mails.send_offer_validation_status_update_email(offer_data, recipients)


def main(author_id: int, offers_ids: str) -> None:
    for offer_id in offers_ids.split(","):
        try:
            validate_offer(
                author_id=author_id,
                offer_id=int(offer_id),
            )
        except Exception:
            print_exc()
            db.session.rollback()
        else:
            db.session.commit()
            logger.info(f"Collective offer {offer_id} validated by user {author_id} using a script.")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--author", type=int)
    parser.add_argument("--offers")
    args = parser.parse_args()

    main(author_id=args.author, offers_ids=args.offers)

    logger.info("Finished")
    db.session.commit()
