import dataclasses
from unittest.mock import patch

import pytest

from pcapi import settings
import pcapi.core.events.api as events_api
import pcapi.core.events.backend as events_backend
import pcapi.core.events.config as events_config
import pcapi.core.mails.models as mails_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as user_factories


@pytest.mark.usefixtures("db_session")
class DispatchTest:
    @patch.dict(
        "pcapi.core.events.config.EVENTS_DISPATCHING",
        {
            events_config.EventName.USER_DEPOSIT_ACTIVATED: [
                settings.EMAIL_BACKEND,
                settings.AMPLITUDE_BACKEND,
                settings.PUSH_NOTIFICATION_BACKEND,
            ],
            events_config.EventName.USER_IDENTITY_CHECK_STARTED: [
                settings.EMAIL_BACKEND,
            ],
        },
    )
    def test_dispatch_to_services_targeted_in_config(self):
        user = user_factories.UserFactory()
        template = mails_models.Template(id_prod=1, id_not_prod=1)
        transactional_email_data = mails_models.TransactionalEmailData(template=template, params={"param": "value"})
        event = events_backend.Event(
            name=events_config.EventName.USER_DEPOSIT_ACTIVATED,
            payload={"email": user.email, "data": transactional_email_data},
            user_ids=[user.id],
        )
        events_api.dispatch(event)

        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(template)
        assert mails_testing.outbox[0].sent_data["To"] == user.email
