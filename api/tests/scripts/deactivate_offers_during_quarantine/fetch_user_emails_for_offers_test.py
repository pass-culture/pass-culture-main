from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.repository import repository
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

        offerer = create_offerer(siren="123456789")
        user_offerer = create_user_offerer(user=pro, offerer=offerer)
        venue = create_venue(offerer, siret="1234567899876")
        offer = create_offer_with_event_product(venue)
        stock = create_stock(beginning_datetime=tomorrow, offer=offer)

        offerer1 = create_offerer(siren="987654321")
        user_offerer1 = create_user_offerer(user=pro1, offerer=offerer1)
        venue1 = create_venue(offerer1, siret="9876543216543")
        offer1 = create_offer_with_event_product(venue1)
        stock1 = create_stock(beginning_datetime=tomorrow, offer=offer1)

        repository.save(stock1, stock, user_offerer, user_offerer1)

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
        offerer = create_offerer()
        user_offerer = create_user_offerer(user=pro, offerer=offerer)
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue)
        stock = create_stock(beginning_datetime=tomorrow, offer=offer)

        repository.save(stock, user_offerer)

        # When
        pro_emails = fetch_user_emails_for_offers_with_max_stock_date_between_today_and_end_of_quarantine(
            first_day_after_quarantine, today
        )

        # Then
        assert len(pro_emails) == 1
        assert set(pro_emails) == {"john.doe@example.com"}
