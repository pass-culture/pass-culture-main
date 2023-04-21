import dataclasses
from unittest.mock import patch

import pytest

from pcapi import settings
import pcapi.analytics.amplitude.testing as analytics_testing
import pcapi.core.events.api as events_api
import pcapi.core.events.backend as events_backend
import pcapi.core.events.config as events_config
import pcapi.core.mails.models as mails_models
import pcapi.core.mails.testing as mails_testing
import pcapi.notifications.push.testing as push_testing
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
            payload={
                "email": user.email,
                "data": transactional_email_data,
                "fraud_check_type": fraud_models.FraudCheckType.UBBLE,
            },
            user_ids=[user.id],
        )
        events_api.dispatch(event)

        # Email Backend
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(template)
        assert mails_testing.outbox[0].sent_data["To"] == user.email

        # Analytics Backend
        assert analytics_testing.requests[0] == {
            "user_id": user.id,
            "event_name": event.name.value,
            "event_properties": event.payload,
        }

        # Push Notification Backend
        assert push_testing.requests[0] == {
            "user_id": user.id,
            "event_name": event.name.value,
            "event_payload": event.payload,
            "can_be_asynchronously_retried": False,
        }

    @patch.dict("pcapi.core.events.config.EVENTS_DISPATCHING", {})
    @patch.dict(
        "pcapi.core.events.config.LEGACY_EVENTS_DISPATCHING",
        {
            events_config.EventName.USER_DEPOSIT_ACTIVATED: [
                {"backend": settings.AMPLITUDE_BACKEND, "event": events_config.AmplitudeEventType.DEPOSIT_GRANTED},
                {
                    "backend": settings.PUSH_NOTIFICATION_BACKEND,
                    "event": events_config.BatchEvent.USER_DEPOSIT_ACTIVATED,
                },
            ],
        },
    )
    def test_dispatch_to_services_targeted_in_legacy_config(self):
        user = user_factories.UserFactory()
        template = mails_models.Template(id_prod=1, id_not_prod=1)
        transactional_email_data = mails_models.TransactionalEmailData(template=template, params={"param": "value"})
        event = events_backend.Event(
            name=events_config.EventName.USER_DEPOSIT_ACTIVATED,
            payload={"email": user.email, "data": transactional_email_data},
            user_ids=[user.id],
        )
        events_api.dispatch(event)

        # Analytics Backend
        assert analytics_testing.requests[0] == {
            "user_id": user.id,
            "event_name": events_config.AmplitudeEventType.DEPOSIT_GRANTED.value,
            "event_properties": event.payload,
        }

        # Push Notification Backend
        assert push_testing.requests[0] == {
            "user_id": user.id,
            "event_name": events_config.BatchEvent.USER_DEPOSIT_ACTIVATED.value,
            "event_payload": event.payload,
            "can_be_asynchronously_retried": False,
        }
