import argparse
import logging

from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus


logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> None:
    user = users_models.User.query.filter(users_models.User.id == args.user_id).one()
    if not (user.has_beneficiary_role or user.has_underage_beneficiary_role):
        logger.error("Cannot remove pro roles from beneficiary %s. They have no BENEFICIARY roles", args.user_id)
        return
    if not (user.has_pro_role or user.has_non_attached_pro_role):
        logger.error("Cannot remove pro roles from beneficiary %s. They have no PRO roles", args.user_id)
        return
    user_offerer_count = offerers_models.UserOfferer.query.filter(
        offerers_models.UserOfferer.userId == args.user_id,
        offerers_models.UserOfferer.validationStatus != ValidationStatus.REJECTED,
    ).count()
    if user_offerer_count:
        logger.error(
            "Cannot remove pro roles from beneficiary %s. They still have %s active link to offeres",
            args.user_id,
            user_offerer_count,
        )
        return
    logger.info("Remove PRO and UNATTACHED_PRO from beneficiary %s", args.user_id)
    offerers_models.UserOfferer.query.filter(offerers_models.UserOfferer.userId == args.user_id).delete()
    user.remove_pro_role()
    user.remove_non_attached_pro_role()
    db.session.commit()
    logger.info("Beneficiary %s cleaned", args.user_id)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("user_id", type=int, help="Id of the beneficiary to clean")
    with app.app_context():
        main(parser.parse_args())
