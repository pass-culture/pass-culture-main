import datetime
import logging

import pytest

import pcapi.core.chronicles.factories as chronicles_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.models import db
from pcapi.utils.date import timedelta

from tests.test_utils import run_command


class OfferCommandsTest:
    @pytest.mark.features(ENABLE_OFFERS_AUTO_CLEANUP=False)
    @pytest.mark.usefixtures("clean_database")
    def test_feature_flag_stops_deletion(self, app):
        a_year_ago = datetime.date.today() - timedelta(days=366)
        offer_id = offers_factories.OfferFactory(dateCreated=a_year_ago, dateUpdated=a_year_ago).id

        run_command(app, "delete_unbookable_unbooked_old_offers")

        assert db.session.get(offers_models.Offer, offer_id) is not None

    @pytest.mark.features(ENABLE_OFFERS_AUTO_CLEANUP=True)
    @pytest.mark.usefixtures("clean_database")
    def test_command_deletes_unbookable_unbooked_old_offers(self, app):
        a_year_ago = datetime.date.today() - timedelta(days=366)
        offer = offers_factories.OfferFactory(dateCreated=a_year_ago, dateUpdated=a_year_ago)
        offer_id = offer.id

        run_command(app, "delete_unbookable_unbooked_old_offers")

        assert db.session.query(offers_models.Offer).filter_by(id=offer_id).count() == 0

    @pytest.mark.usefixtures("clean_database")
    def test_command_check_product_counts_consistency(self, app, caplog):
        product_1 = offers_factories.ProductFactory()
        product_2 = offers_factories.ProductFactory()
        chronicles_factories.ChronicleFactory.create(products=[product_1, product_2])

        product_1.chroniclesCount = 0
        product_2.chroniclesCount = 0
        product_1_id = product_1.id
        product_2_id = product_2.id
        db.session.commit()

        with caplog.at_level(logging.ERROR):
            run_command(app, "check_product_counts_consistency")

        assert caplog.records[0].extra["product_ids"] == {product_1_id, product_2_id}
