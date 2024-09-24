import pytest
from sqlalchemy.exc import IntegrityError

from pcapi.core.operations import factories as operations_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SpecialEventTest:
    def test_unique_external_id(self):
        operations_factories.SpecialEventFactory(externalId="should_be_unique")
        with pytest.raises(IntegrityError):
            operations_factories.SpecialEventFactory(externalId="should_be_unique")
