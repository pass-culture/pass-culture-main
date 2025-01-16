from dataclasses import dataclass

import pytest

import pcapi.core.offers.models as offers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.scripts.clean_offers_ean_title import utils


pytestmark = pytest.mark.usefixtures("db_session")


@dataclass
class UtilsRandomRow:
    id: int
    ean: str
    name: str


class RetryAndLogTest:
    def test_no_error_no_retry(self):
        func = utils.retry_and_log(self.nop)
        assert func([1, 2])

    def test_error_means_retry(self):
        func = utils.retry_and_log(self.error_call)
        rows = [self.build_random_offer_ean_query_row(1)]
        assert not func(rows)

    def test_one_error_other_items_are_updated_during_retry(self):
        self.offers = offers_factories.OfferFactory.create_batch(12)
        self.failing_offer_ids = {self.offers[2].id, self.offers[3].id, self.offers[9].id}

        ids = [offer.id for offer in self.offers]
        rows = [self.build_random_offer_ean_query_row(row_id) for row_id in ids]

        func = utils.retry_and_log(self.update_offer)
        assert not func(rows)

        for offer in self.offers:
            if offer.id not in self.failing_offer_ids:
                assert offer.name.endswith("+ updated")
            else:
                assert not offer.name.endswith("+ updated")

    def build_random_offer_ean_query_row(self, row_id):
        return UtilsRandomRow(
            id=row_id,
            ean="0000000000001",
            name="name",
        )

    def nop(self, *args, **kwargs):
        pass

    def error_call(self, rows):
        raise RuntimeError("test")

    def update_offer(self, rows):
        for row in rows:
            if row.id in self.failing_offer_ids:
                raise RuntimeError("test")
            else:
                offer = offers_models.Offer.query.get(row.id)
                offer.name = f"{offer.name} + updated"

