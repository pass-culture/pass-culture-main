import datetime
import logging
from unittest import mock

import pytest
from sqlalchemy import exc as sa_exc

import pcapi.core.chronicles.factories as chronicles_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.reminders.factories as reminders_factories
import pcapi.core.reminders.models as reminders_models
import pcapi.core.users.factories as users_factories
from pcapi.connectors.big_query.importer.offer_quality import OfferQualityImporter
from pcapi.connectors.big_query.queries.offer_quality import OfferQualityModel
from pcapi.models import db
from pcapi.utils.date import timedelta

from tests.test_utils import run_command


pytestmark = pytest.mark.usefixtures("db_session")


class OfferCommandsTest:
    @pytest.mark.features(ENABLE_OFFERS_AUTO_CLEANUP=False)
    @pytest.mark.usefixtures("clean_database")
    def test_feature_flag_stops_deletion(self, app):
        a_year_ago = datetime.datetime.now(datetime.UTC) - timedelta(days=366)
        offer_id = offers_factories.OfferFactory(dateCreated=a_year_ago, dateUpdated=a_year_ago).id

        run_command(app, "delete_unbookable_unbooked_old_offers", "0", f"{offer_id * 2}")

        assert db.session.get(offers_models.Offer, offer_id) is not None

    @pytest.mark.features(ENABLE_OFFERS_AUTO_CLEANUP=True)
    @pytest.mark.usefixtures("clean_database")
    def test_command_deletes_unbookable_unbooked_old_offers(self, app):
        a_year_ago = datetime.datetime.now(datetime.UTC) - timedelta(days=366)
        offer = offers_factories.OfferFactory(dateCreated=a_year_ago, dateUpdated=a_year_ago)
        offer_id = offer.id

        run_command(app, "delete_unbookable_unbooked_old_offers", "0", f"{offer_id * 2}")

        assert db.session.query(offers_models.Offer).filter_by(id=offer_id).count() == 0

    @pytest.mark.usefixtures("clean_database")
    def test_command_check_product_counts_consistency(self, app, caplog):
        product_1 = offers_factories.ProductFactory()
        product_2 = offers_factories.ProductFactory()
        chronicles_factories.ChronicleFactory.create(products=[product_1, product_2], isSocialMediaDiffusible=True)

        product_1.chroniclesCount = 0
        product_2.chroniclesCount = 0
        product_1_id = product_1.id
        product_2_id = product_2.id
        db.session.commit()

        with caplog.at_level(logging.ERROR):
            run_command(app, "check_product_counts_consistency")

        assert caplog.records[0].extra["product_ids"] == {product_1_id, product_2_id}

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    @pytest.mark.usefixtures("clean_database")
    def test_reindex_recently_published_offers_command(self, mock_reindex_offers, app):
        offer = offers_factories.OfferFactory(publicationDatetime=datetime.datetime.now(datetime.UTC))
        user = users_factories.BeneficiaryFactory()
        reminders_factories.OfferReminderFactory(user=user, offer=offer)

        run_command(app, "reindex_recently_published_offers")

        mock_reindex_offers.assert_called_once()

    @mock.patch("pcapi.core.reminders.external.reminders_notifications.send_users_reminders_for_offer")
    @pytest.mark.usefixtures("clean_database")
    def test_future_offer_command(self, mock_notify_users, app):
        offer = offers_factories.OfferFactory(bookingAllowedDatetime=datetime.datetime.now(datetime.UTC))
        user = users_factories.BeneficiaryFactory()
        reminders_factories.OfferReminderFactory(user=user, offer=offer)

        run_command(app, "send_future_offer_reminders")

        mock_notify_users.assert_called_once()

        remiders = db.session.query(reminders_models.OfferReminder).all()
        assert len(remiders) == 0


class UpdateOfferQualityTest:
    @mock.patch("pcapi.connectors.big_query.queries.offer_quality.OfferQualityQuery.execute")
    def test_run_scores_update_updates_existing_and_ignores_missing(self, mock_query, caplog):
        offer_no_score = offers_factories.OfferFactory()
        offer_with_score = offers_factories.OfferFactory()
        offers_factories.OfferQualityFactory(offer=offer_with_score, completionScore=5.0)

        fake_bq_data = [
            OfferQualityModel(
                offer_id=987654321,  # offer that does not exist
                completion_score=8.5,
            ),
            OfferQualityModel(offer_id=offer_no_score.id, completion_score=8.5),
            OfferQualityModel(offer_id=offer_with_score.id, completion_score=4.0),
        ]
        mock_query.return_value = fake_bq_data

        with caplog.at_level(logging.INFO):
            importer = OfferQualityImporter()
            importer.run_offer_quality_update(batch_size=1)

        assert offer_no_score.quality.completionScore == 8.5
        assert offer_with_score.quality.completionScore == 4.0
        assert db.session.query(offers_models.OfferQuality).count() == 2
        assert "Skipping scores update for missing offer" in caplog.text
        assert "Finished offer quality scores update" in caplog.text

    @mock.patch("pcapi.connectors.big_query.queries.offer_quality.OfferQualityQuery.execute")
    def test_run_offer_quality_update_batch_failure_retries_individually(self, mock_bq_execute, caplog):
        offer_1 = offers_factories.OfferFactory()
        offers_factories.OfferQualityFactory(offer=offer_1, completionScore=2.0)
        offer_2 = offers_factories.OfferFactory()

        bq_item1 = OfferQualityModel(offer_id=offer_1.id, completion_score=10.0)
        bq_item2 = OfferQualityModel(offer_id=offer_2.id, completion_score=8.5)
        mock_bq_execute.return_value = iter([bq_item1, bq_item2])
        with mock.patch("pcapi.models.db.session.commit") as mock_commit:
            mock_commit.side_effect = [
                sa_exc.SQLAlchemyError("Simulated Batch Commit Failure"),
                None,
                None,
            ]
            importer = OfferQualityImporter()
            importer.run_offer_quality_update(batch_size=2)

        assert mock_commit.call_count == 3
        assert "Batch update failed. Retrying one by one" in caplog.text
        assert "Successfully updated offer quality batch scores" not in caplog.text
        assert offer_1.quality.completionScore == 10.0
        assert offer_2.quality.completionScore == 8.5
