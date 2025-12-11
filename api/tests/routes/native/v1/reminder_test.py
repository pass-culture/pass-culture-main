import datetime

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.reminders import factories as reminders_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils import date as date_utils

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class GetRemindersTest:
    num_queries_success = 1  # select user
    num_queries_success += 1  # select future_offer_reminders

    def test_should_be_logged_in_to_get_reminders(self, client):
        with assert_num_queries(0):
            response = client.get("/native/v1/me/reminders")
            assert response.status_code == 401

    def test_get_reminders(self, app):
        user_1 = users_factories.BeneficiaryFactory()
        user_2 = users_factories.BeneficiaryFactory()

        future_publication_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=30)
        offer_1 = offers_factories.OfferFactory(isActive=False, publicationDatetime=future_publication_date)
        offer_2 = offers_factories.OfferFactory(isActive=False, publicationDatetime=future_publication_date)

        reminder_1 = reminders_factories.OfferReminderFactory(offer=offer_1, user=user_1)
        reminder_2 = reminders_factories.OfferReminderFactory(offer=offer_2, user=user_1)
        reminder_3 = reminders_factories.OfferReminderFactory(offer=offer_2, user=user_2)

        expected_reminders_1 = {
            "reminders": [
                {"id": reminder_1.id, "offer": {"id": offer_1.id}},
                {"id": reminder_2.id, "offer": {"id": offer_2.id}},
            ]
        }
        expected_reminders_2 = {
            "reminders": [
                {"id": reminder_3.id, "offer": {"id": offer_2.id}},
            ]
        }

        for user, expected_reminders in [(user_1, expected_reminders_1), (user_2, expected_reminders_2)]:
            client = TestClient(app.test_client()).with_token(user)
            with assert_num_queries(self.num_queries_success):
                response = client.get("/native/v1/me/reminders")
                assert response.status_code == 200

            assert response.json == expected_reminders


class PostReminderTest:
    num_queries_success = 1  # select user
    num_queries_success += 1  # select offer
    num_queries_success += 1  # select offer_reminder
    num_queries_success += 1  # insert offer_reminder

    def test_should_be_logged_in_to_post_reminder(self, client):
        with assert_num_queries(0):
            response = client.post("/native/v1/me/reminders", json={})
            assert response.status_code == 400

    def test_future_offer_not_found(self, client):
        user = users_factories.BeneficiaryFactory()
        client.with_token(user)

        num_queries = 1  # select user
        num_queries += 1  # select future_offer
        num_queries += 1  # rollback
        num_queries += 1  # rollback
        with assert_num_queries(num_queries):
            response = client.post("/native/v1/me/reminders", json={"offerId": 1})
            assert response.status_code == 404

    def test_create_reminder(self, app):
        user_1 = users_factories.BeneficiaryFactory()
        user_2 = users_factories.BeneficiaryFactory()

        future_publication_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=30)
        offer = offers_factories.OfferFactory(isActive=False, publicationDatetime=future_publication_date)

        for user in [user_1, user_2]:
            offer_id = offer.id
            client = TestClient(app.test_client()).with_token(user)
            with assert_num_queries(self.num_queries_success):
                response = client.post("/native/v1/me/reminders", json={"offerId": offer_id})
                assert response.status_code == 201
            reminder = user.offer_reminders[0]
            assert reminder.offerId == offer.id
            assert response.json == {"id": reminder.id, "offer": {"id": offer_id}}
            assert len(user.offer_reminders) == 1

    def test_already_existing_reminder(self, client):
        user = users_factories.BeneficiaryFactory()

        future_publication_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=30)
        offer_1 = offers_factories.OfferFactory(isActive=False, publicationDatetime=future_publication_date)
        offer_2 = offers_factories.OfferFactory(isActive=False, publicationDatetime=future_publication_date)

        _ = reminders_factories.OfferReminderFactory(offer=offer_1, user=user)
        reminder_2 = reminders_factories.OfferReminderFactory(offer=offer_2, user=user)

        client.with_token(user)

        num_queries = 1  # select user
        num_queries += 1  # select future_offer
        num_queries += 1  # select reminder
        offer_id = offer_2.id

        assert len(user.offer_reminders) == 2

        with assert_num_queries(num_queries):
            response = client.post("/native/v1/me/reminders", json={"offerId": offer_id})
            assert response.status_code == 201

        assert len(user.offer_reminders) == 2
        assert response.json == {"id": reminder_2.id, "offer": {"id": offer_id}}


class DeleteReminderTest:
    num_queries_success = 1  # select user
    num_queries_success += 1  # select offer_reminder
    num_queries_success += 1  # delete reminder

    def test_should_be_logged_in_to_delete_reminder(self, client):
        with assert_num_queries(0):
            response = client.delete("/native/v1/me/reminders/0")
            assert response.status_code == 401

    def test_reminder_does_not_exist(self, client):
        user = users_factories.BeneficiaryFactory()

        num_queries = 1  # select user
        num_queries += 1  # select future_offer_reminder
        num_queries += 1  # rollback
        num_queries += 1  # rollback

        reminder_id = 0
        client.with_token(user)
        with assert_num_queries(num_queries):
            response = client.delete(f"/native/v1/me/reminders/{reminder_id}")
            assert response.status_code == 404

    def test_reminder_is_not_users(self, client):
        user_1 = users_factories.BeneficiaryFactory()
        user_2 = users_factories.BeneficiaryFactory()

        future_publication_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=30)
        offer_1 = offers_factories.OfferFactory(isActive=False, publicationDatetime=future_publication_date)
        offer_2 = offers_factories.OfferFactory(isActive=False, publicationDatetime=future_publication_date)

        _ = reminders_factories.OfferReminderFactory(offer=offer_1, user=user_1)
        reminder_2 = reminders_factories.OfferReminderFactory(offer=offer_2, user=user_2)

        assert len(user_1.offer_reminders) == 1
        assert len(user_2.offer_reminders) == 1

        num_queries = 1  # select user
        num_queries += 1  # select future_offer_reminder
        num_queries += 1  # rollback
        num_queries += 1  # rollback

        reminder_id = reminder_2.id
        client.with_token(user_1)
        with assert_num_queries(num_queries):
            response = client.delete(f"/native/v1/me/reminders/{reminder_id}")
            assert response.status_code == 404

        assert len(user_1.offer_reminders) == 1
        assert len(user_2.offer_reminders) == 1

    def test_delete_reminder(self, client):
        user = users_factories.BeneficiaryFactory()

        future_publication_date = date_utils.get_naive_utc_now() + datetime.timedelta(days=30)
        offer_1 = offers_factories.OfferFactory(isActive=False, publicationDatetime=future_publication_date)
        offer_2 = offers_factories.OfferFactory(isActive=False, publicationDatetime=future_publication_date)

        offer_reminder_1 = reminders_factories.OfferReminderFactory(offer=offer_1, user=user)
        offer_reminder_2 = reminders_factories.OfferReminderFactory(offer=offer_2, user=user)

        assert len(user.offer_reminders) == 2

        reminder_id = offer_reminder_1.id
        client.with_token(user)
        with assert_num_queries(self.num_queries_success):
            response = client.delete(f"/native/v1/me/reminders/{reminder_id}")
            assert response.status_code == 204

        assert len(user.offer_reminders) == 1
        assert user.offer_reminders[0].id == offer_reminder_2.id
