import datetime

import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.subscription.dms import repository


@pytest.mark.usefixtures("db_session")
class RepositoryUnitTest:
    def test_get_orphan_dms_application_by_application_id(self):
        fraud_factories.OrphanDmsApplicationFactory(application_id=88)
        assert repository.get_orphan_dms_application_by_application_id(88) is not None
        assert repository.get_orphan_dms_application_by_application_id(99) is None

    def test_create_orphan_dms_application(self):
        repository.create_orphan_dms_application(
            application_number=88,
            procedure_number=99,
            latest_modification_datetime=datetime.datetime.utcnow(),
            email="john.stiles@example.com",
        )
        assert repository.get_orphan_dms_application_by_application_id(88) is not None
