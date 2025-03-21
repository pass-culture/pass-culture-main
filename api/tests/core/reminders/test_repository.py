import pytest

from pcapi.core.offers import factories as offer_factories
from pcapi.core.reminders import factories
from pcapi.core.reminders import repository
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class GetUsersWithRemindersTest:
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

        offer_id = offer.id
        user_ids = repository.get_users_with_reminders(offer_id)

        assert len(user_ids) == 2
        assert user_ids == [user_1.id, user_2.id]
