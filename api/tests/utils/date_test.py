import datetime

import dateutil

from pcapi.utils.date import CUSTOM_TIMEZONES
from pcapi.utils.date import FrenchParserInfo
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_department_timezone
from pcapi.utils.date import get_postal_code_timezone
from pcapi.utils.date import get_time_formatted_for_email


class GetDateFormattedForEmailTest:
    def test_should_return_day_followed_by_month_written_in_words(self):
        # Given
        december_23 = datetime.date(2019, 12, 23)

        # When
        date_formatted_for_email = get_date_formatted_for_email(december_23)

        # Then
        assert date_formatted_for_email == "23 décembre 2019"

    def test_should_return_1_digit_day_when_day_is_less_than_10(self):
        # Given
        december_09 = datetime.date(2019, 12, 9)

        # When
        date_formatted_for_email = get_date_formatted_for_email(december_09)

        # Then
        assert date_formatted_for_email == "9 décembre 2019"


class GetTimeFormattedForEmailTest:
    def test_should_return_hour_followed_by_two_digits_minutes(self):
        # Given
        twelve_o_clock = datetime.time(12, 0, 0, 0)

        # When
        time_formatted_for_email = get_time_formatted_for_email(twelve_o_clock)

        # Then
        assert time_formatted_for_email == "12h00"


class GetDepartmentTimezoneTest:
    def test_should_return_paris_as_default_timezone(self):
        assert get_department_timezone("1") == "Europe/Paris"

    def test_should_return_custom_timezones(self):
        assert get_department_timezone("973") == "America/Cayenne"

    def test_all_custom_timezones_are_valid(self):
        for timezone in CUSTOM_TIMEZONES.values():
            assert dateutil.tz.gettz(timezone) is not None, f"{timezone} is not a valid timezone"


class GetPostalCodeTimezoneTest:
    def test_should_return_paris_as_default_timezone(self):
        assert get_postal_code_timezone("75000") == "Europe/Paris"

    def test_should_return_custom_timezones(self):
        assert get_postal_code_timezone("97300") == "America/Cayenne"


class FrenchParserInfoTest:
    def test_parse_french_date(self):
        assert dateutil.parser.parse("12 mai 2021", FrenchParserInfo()) == datetime.datetime(2021, 5, 12)
