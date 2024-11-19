from datetime import datetime

from dateutil.relativedelta import relativedelta

from . import constants
from . import models


def anonymize_unlinked_chronicles() -> None:
    models.Chronicle.query.filter(
        models.Chronicle.userId.is_(None),
        models.Chronicle.email != constants.ANONYMIZED_EMAIL,
        models.Chronicle.dateCreated < datetime.utcnow() - relativedelta(years=2),
    ).update({"email": constants.ANONYMIZED_EMAIL}, synchronize_session=False)
