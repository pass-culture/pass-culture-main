import datetime

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.reminders import factories as reminders_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class PostReminderTest:
    num_queries_success = 1  # select user
    num_queries_success += 1  # select future_offer
    num_queries_success += 1  # select future_offer_reminder
    num_queries_success += 1  # Insert reminder

    def test_should_be_logged_in_to_post_reminder(self, client):
        with assert_num_queries(0):
            response = client.post("/native/v1/reminder", json={})
            assert response.status_code == 400

    def test_future_offer_not_found(self, client):
        user = users_factories.BeneficiaryFactory()
        client.with_token(user.email)

        num_queries = 1  # select user
        num_queries += 1  # select future_offer
        num_queries += 1  # rollback
        with assert_num_queries(num_queries):
            response = client.post("/native/v1/reminder", json={"offerId": 1})
            assert response.status_code == 404

    def test_create_reminder(self, client):
        user = users_factories.BeneficiaryFactory()
        offer = offers_factories.OfferFactory(isActive=False)
        future_publication_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        future_offer = offers_factories.FutureOfferFactory(offer=offer, publicationDate=future_publication_date)

        client.with_token(user.email)

        offer_id = offer.id
        with assert_num_queries(self.num_queries_success):
            response = client.post("/native/v1/reminder", json={"offerId": offer_id})
            assert response.status_code == 201

        reminder = user.future_offer_reminders[0]

        assert reminder.futureOffer.id == future_offer.id
        assert response.json == {"id": reminder.id, "offer": {"id": offer_id}}

    def test_already_existing_reminder(self, client):
        user = users_factories.BeneficiaryFactory()

        offer_1 = offers_factories.OfferFactory(isActive=False)
        offer_2 = offers_factories.OfferFactory(isActive=False)

        future_publication_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)

        future_offer_1 = offers_factories.FutureOfferFactory(offer=offer_1, publicationDate=future_publication_date)
        future_offer_2 = offers_factories.FutureOfferFactory(offer=offer_2, publicationDate=future_publication_date)

        _ = reminders_factories.FutureOfferReminderFactory(futureOffer=future_offer_1, user=user)
        reminder_2 = reminders_factories.FutureOfferReminderFactory(futureOffer=future_offer_2, user=user)

        client.with_token(user.email)

        num_queries = 1  # select user
        num_queries += 1  # select future_offer
        num_queries += 1  # select reminder
        offer_id = offer_2.id

        assert len(user.future_offer_reminders) == 2

        with assert_num_queries(num_queries):
            response = client.post("/native/v1/reminder", json={"offerId": offer_id})
            assert response.status_code == 201

        assert len(user.future_offer_reminders) == 2
        assert response.json == {"id": reminder_2.id, "offer": {"id": offer_id}}
