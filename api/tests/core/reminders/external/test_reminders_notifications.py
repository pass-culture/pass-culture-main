import logging

import pytest

from pcapi.core.offers import factories as offer_factories
from pcapi.core.reminders import factories
from pcapi.core.reminders import models
from pcapi.core.reminders.external.reminders_notifications import notify_users_offer_is_bookable
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.notifications.push import testing as push_testing


@pytest.mark.usefixtures("db_session")
class NotifyUsersOfferIsBookableTest:
    def test_notify_users_offer_is_bookable(self):
        user_1 = users_factories.UserFactory()
        user_2 = users_factories.UserFactory()
        user_3 = users_factories.UserFactory()

        offer = offer_factories.EventOfferFactory(isDuo=True, name="Super Future Offer")
        offer_2 = offer_factories.OfferFactory()

        factories.OfferReminderFactory(offer=offer, user=user_1)
        factories.OfferReminderFactory(offer=offer, user=user_2)
        factories.OfferReminderFactory(offer=offer_2, user=user_3)

        notify_users_offer_is_bookable(offer)

        expected_push_counts = 1  # for trigger event future offer activated
        assert len(push_testing.requests) == expected_push_counts

        offer_attributes = {
            "offer_id": offer.id,
            "offer_name": "Super Future Offer",
            "offer_category": "CINEMA",
            "offer_subcategory": "SEANCE_CINE",
            "offer_type": "duo",
        }
        expected_payload = [
            {
                "id": str(user_1.id),
                "events": [
                    {
                        "name": "ue.future_offer_activated",
                        "attributes": offer_attributes,
                    }
                ],
            },
            {
                "id": str(user_2.id),
                "events": [
                    {
                        "name": "ue.future_offer_activated",
                        "attributes": offer_attributes,
                    }
                ],
            },
        ]

        future_offer_activated_event = next(event for event in push_testing.requests)
        event_payload = future_offer_activated_event["payload"]
        assert event_payload == expected_payload

        offer_reminders = db.session.query(models.OfferReminder).filter(models.OfferReminder.offerId == offer.id).all()
        assert offer_reminders == []

    def test_notify_no_users_future_offer_activated(self, caplog):
        user_1 = users_factories.UserFactory()

        offer = offer_factories.OfferFactory()
        offer_2 = offer_factories.OfferFactory()

        factories.OfferReminderFactory(offer=offer_2, user=user_1)

        with caplog.at_level(logging.INFO):
            notify_users_offer_is_bookable(offer)

        assert len(push_testing.requests) == 0
        assert caplog.records[0].message == "[Offer bookable] No users to notify"
        assert caplog.records[0].extra == {"offerId": offer.id}
