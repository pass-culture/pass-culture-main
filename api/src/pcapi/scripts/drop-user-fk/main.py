"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=BSR-drop-user-offer-report-fk \
  -f NAMESPACE=drop-user-fk \
  -f SCRIPT_ARGUMENTS="";

"""

import logging

import sqlalchemy as sa

from pcapi import settings
from pcapi.app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    db.session.execute(sa.text("SET lock_timeout = 10000;"))

    # The below statement can't run inside a transaction
    db.session.execute(sa.text("COMMIT;"))
    db.session.execute(
        sa.text(""" ALTER TABLE "offer_report" DROP CONSTRAINT IF EXISTS "offer_report_userId_fkey"; """)
    )

    # According to PostgreSQL, setting such values this way is affecting only the current session
    # but let's be defensive by setting back to the original values
    db.session.execute(sa.text(f"SET lock_timeout = {settings.DATABASE_LOCK_TIMEOUT}"))
