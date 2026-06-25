import pytest

from pcapi.core.users.utils import format_login_location


class FormatLoginLocationTest:
    @pytest.mark.parametrize("country_name", ["France", None])
    def should_return_country_name_when_no_city_name(self, country_name):
        assert format_login_location(country_name, city_name=None) == country_name

    @pytest.mark.parametrize("city_name", ["Paris", None])
    def should_return_city_name_when_no_country_name(self, city_name):
        assert format_login_location(country_name=None, city_name=city_name) == city_name

    def should_return_country_and_city_separated_by_comma_when_both_are_available(self):
        assert format_login_location(country_name="France", city_name="Paris") == "Paris, France"
