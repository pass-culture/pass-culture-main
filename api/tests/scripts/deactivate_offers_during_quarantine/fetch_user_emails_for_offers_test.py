from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.scripts.deactivate_offers_during_quarantine.fetch_user_emails_for_offers import (
    fetch_user_emails_for_offers_with_max_stock_date_between_today_and_end_of_quarantine,
)


class FetchUserEmailsForOffersTest:
    @patch(
        "pcapi.scripts.deactivate_offers_during_quarantine.fetch_user_emails_for_offers."
        "build_query_offers_with_max_stock_date_between_today_and_end_of_quarantine"
    )
    def test_should_call_build_offers_query(self, stub_build_query):
        # Given
        first_day_after_quarantine = datetime(2020, 4, 16)
        today = datetime(2020, 4, 10)

        # When
        fetch_user_emails_for_offers_with_max_stock_date_between_today_and_end_of_quarantine(
            first_day_after_quarantine, today
        )

        # Then
        stub_build_query.assert_called_once_with(first_day_after_quarantine, today)

    @pytest.mark.usefixtures("db_session")
    def test_should_return_all_user_emails(self, app):
        # Given
        first_day_after_quarantine = datetime(2020, 4, 16)
        today = datetime(2020, 4, 10)
        tomorrow = today + timedelta(days=1)

        pro = users_factories.ProFactory(email="john.doe@example.com")
        pro1 = users_factories.ProFactory(email="john.rambo@example.com")

        stock = offers_factories.StockFactory(beginningDatetime=tomorrow)
        offerer = stock.offer.venue.managingOfferer
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        stock1 = offers_factories.StockFactory(beginningDatetime=tomorrow)
        offerer1 = stock1.offer.venue.managingOfferer
        offerers_factories.UserOffererFactory(user=pro1, offerer=offerer1)

        # When
        pro_emails = fetch_user_emails_for_offers_with_max_stock_date_between_today_and_end_of_quarantine(
            first_day_after_quarantine, today
        )

        # Then
        assert len(pro_emails) == 2
        assert set(pro_emails) == {"john.doe@example.com", "john.rambo@example.com"}

    @pytest.mark.usefixtures("db_session")
    def test_should_return_only_pro_user_emails(self, app):
        # Given
        first_day_after_quarantine = datetime(2020, 4, 16)
        today = datetime(2020, 4, 10)
        tomorrow = today + timedelta(days=1)

        users_factories.UserFactory(email="jean.dupont@example.com")
        pro = users_factories.ProFactory(email="john.doe@example.com")
        stock = offers_factories.StockFactory(beginningDatetime=tomorrow)
        offerer = stock.offer.venue.managingOfferer
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # When
        pro_emails = fetch_user_emails_for_offers_with_max_stock_date_between_today_and_end_of_quarantine(
            first_day_after_quarantine, today
        )

        # Then
        assert len(pro_emails) == 1
        assert set(pro_emails) == {"john.doe@example.com"}
