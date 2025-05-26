import decimal

import pytest

from pcapi.core.mails.transactional.utils import format_price
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class FormatPriceTest:
    @pytest.mark.parametrize(
        "factory", [users_factories.UserFactory, offerers_factories.OffererFactory, offerers_factories.VenueFactory]
    )
    @pytest.mark.parametrize(
        "price,expected",
        [
            (12, "12 €"),
            (decimal.Decimal(300), "300 €"),
            (decimal.Decimal("99.5"), "99,50 €"),
            (150.0, "150 €"),
            (100.0 / 3.0, "33,33 €"),
        ],
    )
    def test_format_price_in_euros(self, price, expected, factory):
        target = factory()
        assert format_price(price, target) == expected

    @pytest.mark.parametrize(
        "factory",
        [
            users_factories.CaledonianUserFactory,
            offerers_factories.CaledonianOffererFactory,
            offerers_factories.CaledonianVenueFactory,
        ],
    )
    @pytest.mark.parametrize(
        "price,expected",
        [
            (decimal.Decimal("8.38"), "1000 F"),
            (decimal.Decimal("99.5"), "11874 F"),
            (150, "17900 F"),
            (100.0 / 3.0, "3978 F"),
        ],
    )
    def test_format_price_in_xpf(self, price, expected, factory):
        target = factory()
        assert format_price(price, target) == expected
