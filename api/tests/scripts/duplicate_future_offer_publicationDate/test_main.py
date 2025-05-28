import datetime
import logging

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.scripts.duplicate_future_offer_publicationDate.main import main


now = datetime.datetime.now(datetime.timezone.utc)
in_two_days = now + datetime.timedelta(days=2)
two_days_ago = now - datetime.timedelta(days=2)


@pytest.mark.usefixtures("db_session")
class DuplicateFutureOfferPublicationDateMainTest:
    @pytest.mark.parametrize(
        "offer_input,future_offer_input,expected_publicationDatetime",
        [
            # offer already has a publicationDatetime
            (
                {"publicationDatetime": now, "isActive": False},
                {"publicationDate": in_two_days},
                now.replace(tzinfo=None),
            ),
            # is active but should be published in the future
            ({"isActive": True}, {"publicationDate": in_two_days}, None),
            # is not active but should already have been published
            ({"isActive": False}, {"publicationDate": two_days_ago}, None),
            ({"isActive": False}, {"publicationDate": two_days_ago, "isSoftDeleted": True}, None),
        ],
    )
    def test_should_not_duplicate(
        self,
        offer_input,
        future_offer_input,
        expected_publicationDatetime,
        caplog,
    ):
        offer = offers_factories.OfferFactory(**offer_input)
        future_offer = offers_factories.FutureOfferFactory(offer=offer, **future_offer_input)

        with caplog.at_level(logging.WARNING):
            main()

        assert offer.publicationDatetime == expected_publicationDatetime
        assert offer.bookingAllowedDatetime == None
        assert caplog.records[0].message == "publicationDate was not duplicated"
        assert caplog.records[0].extra == {
            "future_offer": {
                "id": future_offer.id,
                "publicationDate": future_offer.publicationDate,
                "isSoftDeleted": future_offer.isSoftDeleted,
            },
            "offer": {"id": offer.id},
        }

    @pytest.mark.parametrize(
        "offer_input,future_offer_input",
        [
            # offer has been published by the CRON job
            ({"isActive": True}, {"publicationDate": two_days_ago, "isSoftDeleted": True}),
            # offer is waiting to be published
            ({"isActive": False}, {"publicationDate": in_two_days}),
        ],
    )
    def test_should_duplicate(
        self,
        offer_input,
        future_offer_input,
        caplog,
    ):
        offer = offers_factories.OfferFactory(**offer_input)
        future_offer = offers_factories.FutureOfferFactory(offer=offer, **future_offer_input)

        with caplog.at_level(logging.INFO):
            main()

        assert caplog.records[0].message == "publicationDate was duplicated"
        assert caplog.records[0].extra == {
            "future_offer": {
                "id": future_offer.id,
                "publicationDate": future_offer.publicationDate,
                "isSoftDeleted": future_offer.isSoftDeleted,
            },
            "offer": {"id": offer.id},
        }
        assert offer.publicationDatetime == future_offer.publicationDate
        assert offer.bookingAllowedDatetime == future_offer.publicationDate
