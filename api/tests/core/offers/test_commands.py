import datetime

import pytest
import sqlalchemy

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

        assert db.session.query(offers_models.Offer).get(offer_id) is not None

    @pytest.mark.features(ENABLE_OFFERS_AUTO_CLEANUP=True)
    @pytest.mark.usefixtures("clean_database")
    def test_command_deletes_unbookable_unbooked_old_offers(self, app):
        a_year_ago = datetime.date.today() - timedelta(days=366)
        offer = offers_factories.OfferFactory(dateCreated=a_year_ago, dateUpdated=a_year_ago)

        run_command(app, "delete_unbookable_unbooked_old_offers")

        with pytest.raises(sqlalchemy.exc.InvalidRequestError, match="not persistent within this Session"):
            # Trying to refresh the offer should fail because it is deleted from the database
            db.session.refresh(offer)
