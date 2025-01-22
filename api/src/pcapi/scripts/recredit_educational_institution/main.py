import argparse
import logging

from pcapi.core.educational import models as eudcational_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def recredit_institution(do_update: bool) -> None:
    institution_credit = eudcational_models.EducationalDeposit.query.filter(
        eudcational_models.EducationalDeposit.educationalInstitutionId == 9670,
        eudcational_models.EducationalDeposit.educationalYearId == "10",  # 2024-2025
    ).one_or_none()

    logger.info("The amount of the deposit is %s", institution_credit.amount)

    institution_credit.amount += 2000
    db.session.add(institution_credit)

    if do_update:
        db.session.commit()
    else:
        db.session.rollback()

    logger.info("The amount of the deposit is now %s", institution_credit.amount)


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Recredit EducationalInstitution after partial overpayment incident")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    args = parser.parse_args()

    recredit_institution(do_update=args.not_dry)
