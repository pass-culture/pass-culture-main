import logging

import pytest

from pcapi.core.offers import factories as offer_factories
from pcapi.core.reminders import factories
from pcapi.core.reminders.external.reminders_notifications import notify_users_future_offer_activated
from pcapi.core.users import factories as users_factories
from pcapi.notifications.push import testing as push_testing


@pytest.mark.usefixtures("db_session")
class NotifyUsersFutureOfferActivatedTest:
    def test_notify_users_future_offer_activated(self):
        user_1 = users_factories.UserFactory()
        user_2 = users_factories.UserFactory()
        user_3 = users_factories.UserFactory()

        offer = offer_factories.EventOfferFactory(isDuo=True, name="Super Future Offer")
        future_offer = offer_factories.FutureOfferFactory(offer=offer)
        offer_2 = offer_factories.OfferFactory()
        future_offer_2 = offer_factories.FutureOfferFactory(offer=offer_2)

        factories.FutureOfferReminderFactory(futureOffer=future_offer, user=user_1)
        factories.FutureOfferReminderFactory(futureOffer=future_offer, user=user_2)
        factories.FutureOfferReminderFactory(futureOffer=future_offer_2, user=user_3)

        notify_users_future_offer_activated(offer)

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

    def test_notify_no_users_future_offer_activated(self, caplog):
        user_1 = users_factories.UserFactory()

        offer = offer_factories.OfferFactory()
        _ = offer_factories.FutureOfferFactory(offer=offer)
        offer_2 = offer_factories.OfferFactory()
        future_offer_2 = offer_factories.FutureOfferFactory(offer=offer_2)

        factories.FutureOfferReminderFactory(futureOffer=future_offer_2, user=user_1)

        with caplog.at_level(logging.WARNING):
            notify_users_future_offer_activated(offer)

        assert len(push_testing.requests) == 0
        assert caplog.records[0].message == "No users found"
