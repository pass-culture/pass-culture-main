import typing

from pcapi.core.fraud import models as fraud_models
from pcapi.models import db


def create_orphan_dms_application(
    application_id: int, procedure_id: int, email: typing.Optional[str] = None
) -> fraud_models.OrphanDmsApplication:
    orphan_dms_application = fraud_models.OrphanDmsApplication(
        application_id=application_id, process_id=procedure_id, email=email
    )
    db.session.add(orphan_dms_application)
    db.session.commit()
    return orphan_dms_application
