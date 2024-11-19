import datetime

import pytest

from pcapi.core.chronicles import api
from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class AnonymizeUnlinkedChronicleTest:
    def test_anonymize_old_chronicle(self):
        chronicle = chronicles_factories.ChronicleFactory(
            email="personalemail@example.com",
            dateCreated=datetime.date.today() - datetime.timedelta(days=750),
        )

        api.anonymize_unlinked_chronicles()
        db.session.refresh(chronicle)

        assert chronicle.email == "anonymized_email@anonymized.passculture"

    def test_do_not_anonymize_new_chronicle(self):
        email = "personalemail@example.com"
        chronicle = chronicles_factories.ChronicleFactory(
            email=email,
            dateCreated=datetime.date.today() - datetime.timedelta(days=700),
        )

        api.anonymize_unlinked_chronicles()
        db.session.refresh(chronicle)

        assert chronicle.email == email

    def test_do_not_anonymize_chronicle_linked_to_user(self):
        email = "personalemail@example.com"
        chronicle = chronicles_factories.ChronicleFactory(
            user=users_factories.BeneficiaryFactory(),
            email=email,
            dateCreated=datetime.date.today() - datetime.timedelta(days=750),
        )

        api.anonymize_unlinked_chronicles()
        db.session.refresh(chronicle)

        assert chronicle.email == email
