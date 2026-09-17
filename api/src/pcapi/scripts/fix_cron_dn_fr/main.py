"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-43727-fix-cron-dn-et \
  -f NAMESPACE=fix_cron_dn_fr \
  -f SCRIPT_ARGUMENTS="";

"""

import logging

from pcapi import settings
from pcapi.connectors.dms import models as dms_models
from pcapi.models import db


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    count = (
        db.session.query(dms_models.LatestDmsImport)
        .filter(dms_models.LatestDmsImport.procedureId == settings.DMS_ENROLLMENT_PROCEDURE_ID_FR)
        .filter(dms_models.LatestDmsImport.isProcessing.is_(True))
        .update({dms_models.LatestDmsImport.isProcessing: False}, synchronize_session=False)
    )

    logger.info("%d rows updated", count)
    db.session.commit()
