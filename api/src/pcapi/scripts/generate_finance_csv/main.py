"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-generate-finance-csv \
  -f NAMESPACE=generate_finance_csv \
  -f SCRIPT_ARGUMENTS="";

"""

import logging

import sqlalchemy.orm as sa_orm

import pcapi.core.finance.api as finance_api
import pcapi.core.finance.models as finance_models
import pcapi.core.users.models as users_models
from pcapi import settings
from pcapi.app import app
from pcapi.core.mails.transactional.pro.provider_reimbursement_csv import send_provider_reimbursement_email
from pcapi.models import db


logger = logging.getLogger(__name__)

OFFERER_INFORMATION = [
    {
        "email": settings.KINEPOLIS_EMAIL,
        "parent_folder_id": settings.KINEPOLIS_GOOGLE_DRIVE_CSV_REIMBURSEMENT_ID,
        "offerer_name": "KINEPOLIS",
    },
]

if __name__ == "__main__":
    app.app_context().push()

    batch = db.session.query(finance_models.CashflowBatch).filter(finance_models.CashflowBatch.id == 2105).one()

    for info in OFFERER_INFORMATION:
        try:
            user = db.session.query(users_models.User).filter_by(email=info["email"]).one()
        except sa_orm.exc.NoResultFound:
            logger.exception("Email is not linked to any user", extra={"email": info["email"]})
        link_to_csv = finance_api._create_and_get_provider_reimbursement_csv(user.id, batch, info)
        if link_to_csv is not None:
            send_provider_reimbursement_email(user.email, link_to_csv)
