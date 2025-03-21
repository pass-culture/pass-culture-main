from datetime import datetime
from datetime import timedelta
import logging
from unittest import mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from pcapi.core.offers import factories as offer_factories
from pcapi.core.reminders import factories
from pcapi.core.reminders.external.reminders_notifications import notify_users_for_future_offers_activations
from pcapi.core.reminders.external.reminders_notifications import notify_users_future_offer_activated
from pcapi.core.users import factories as users_factories
from pcapi.notifications.push import testing


@pytest.mark.usefixtures("db_session")
class NotifyUsersFutureOffersActivationsTest:
    def test_notify_users_for_future_offers_activations(self):

        offer = offer_factories.OfferFactory(isActive=False)
        publication_date = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        offer_factories.FutureOfferFactory(offer=offer, publicationDate=publication_date)

        offer_2 = offer_factories.OfferFactory(isActive=False)
        publication_date_2 = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        offer_factories.FutureOfferFactory(offer=offer_2, publicationDate=publication_date_2)

        with patch(
            "pcapi.core.reminders.external.reminders_notifications.notify_users_future_offer_activated"
        ) as notify_users_future_offer_activated_mock:
            notify_users_for_future_offers_activations()
            notify_users_future_offer_activated_mock.assert_has_calls([call(offer=offer), call(offer=offer_2)])


@pytest.mark.usefixtures("db_session")
class NotifyUsersFutureOfferActivatedTest:
    def test_notify_users_future_offer_activated(self):

        user_1 = users_factories.UserFactory()
        user_2 = users_factories.UserFactory()
        user_3 = users_factories.UserFactory()

        offer = offer_factories.OfferFactory()
        future_offer = offer_factories.FutureOfferFactory(offer=offer)
        offer_2 = offer_factories.OfferFactory()
        future_offer_2 = offer_factories.FutureOfferFactory(offer=offer_2)

        factories.FutureOfferReminderFactory(futureOffer=future_offer, user=user_1)
        factories.FutureOfferReminderFactory(futureOffer=future_offer, user=user_2)
        factories.FutureOfferReminderFactory(futureOffer=future_offer_2, user=user_3)

        notify_users_future_offer_activated(offer)

        assert len(testing.requests) == 1
        assert all(data["message"]["title"] == "Ton offre est réservable" for data in testing.requests)

        user_ids = {user_id for data in testing.requests for user_id in data["user_ids"]}
        assert user_ids == {user_1.id, user_2.id}

    def test_notify_no_users_future_offer_activated(self, caplog):

        user_1 = users_factories.UserFactory()

        offer = offer_factories.OfferFactory()
        future_offer = offer_factories.FutureOfferFactory(offer=offer)
        offer_2 = offer_factories.OfferFactory()
        future_offer_2 = offer_factories.FutureOfferFactory(offer=offer_2)

        factories.FutureOfferReminderFactory(futureOffer=future_offer_2, user=user_1)

        with caplog.at_level(logging.WARNING):
            notify_users_future_offer_activated(offer)

        assert len(testing.requests) == 0
        assert caplog.records[0].message == "No users found"

    def test_notify_users_future_offer_activate_exception_in_send(self, caplog):

        user = users_factories.UserFactory()
        offer = offer_factories.OfferFactory()
        future_offer = offer_factories.FutureOfferFactory(offer=offer)

        factories.FutureOfferReminderFactory(futureOffer=future_offer, user=user)

        with patch("pcapi.tasks.batch_tasks.send_transactional_notification_task.delay", side_effect=Exception):
            with caplog.at_level(logging.ERROR):
                notify_users_future_offer_activated(offer)

        assert len(testing.requests) == 0
        assert (
            caplog.records[0].message == f"Failed to register send_transactional_notification_task for offer {offer.id}"
        )
