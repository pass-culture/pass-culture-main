import itertools

import pytest

from pcapi import settings
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import utils
from pcapi.models import db


class OffersUtilsTest:
    @pytest.mark.usefixtures("db_session")
    def test_offer_app_link(self):
        offer = offerers_factories.OffererFactory()
        link = utils.offer_app_link(offer)
        assert link == f"{settings.WEBAPP_V2_URL}/offre/{offer.id}"


class YieldOfferIdFromQueryTest:
    @pytest.mark.usefixtures("db_session")
    def test_less_results_than_chunk_size(self):
        offers_factories.OfferFactory()
        query = db.session.query(offers_models.Offer.id)

        for offer_ids, loop in zip(utils.yield_field_batch_from_query(query, chunk_size=2), itertools.count()):
            assert loop == 0
            assert len(offer_ids) == 1

    @pytest.mark.usefixtures("db_session")
    def test_exact_chunk_size(self):
        offers_factories.OfferFactory.create_batch(2)
        query = db.session.query(offers_models.Offer.id)

        for offer_ids, loop in zip(utils.yield_field_batch_from_query(query, chunk_size=2), itertools.count()):
            assert loop == 0
            assert len(offer_ids) == 2

    @pytest.mark.usefixtures("db_session")
    def test_more_results_than_chunk_size(self):
        offers_factories.OfferFactory.create_batch(5)

        query = db.session.query(offers_models.Offer.id)

        for offer_ids, loop in zip(utils.yield_field_batch_from_query(query, chunk_size=2), itertools.count()):
            if loop <= 1:
                assert len(offer_ids) == 2
            else:
                assert loop == 2
                assert len(offer_ids) == 1
