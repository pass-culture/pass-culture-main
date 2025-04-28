import pytest

from pcapi.core.offers import factories as offer_factories
from pcapi.core.reminders import factories
from pcapi.core.reminders import repository
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class GetUserIdsWithRemindersTest:
    def test_get_users_with_reminders(self):
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

        user_ids = repository.get_user_ids_with_reminders(offer.id)

        assert len(user_ids) == 2
        assert sorted(user_ids) == [user_1.id, user_2.id]


@pytest.mark.usefixtures("db_session")
class DeleteRemindersOnOfferTest:
    def test_delete_reminders_on_offer(self):
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

        repository.delete_reminders_on_offer(offer.id)

        user_ids = repository.get_user_ids_with_reminders(offer.id)

        assert len(user_ids) == 0
