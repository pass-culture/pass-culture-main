"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-script-drop-offer-report \
  -f NAMESPACE=drop-offer-report \
  -f SCRIPT_ARGUMENTS="";

"""

import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    # The below statement can't run inside a transaction
    db.session.execute(sa.text("COMMIT;"))
    db.session.execute(sa.text(""" DROP TABLE IF EXISTS "offer_report"; """))
