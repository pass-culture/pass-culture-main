import datetime

import dateutil
import pytest

from pcapi.utils.date import CUSTOM_TIMEZONES
from pcapi.utils.date import FrenchParserInfo
from pcapi.utils.date import format_time_in_second_to_human_readable
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
        assert get_department_timezone(None) == "Europe/Paris"

    def test_should_return_custom_timezone(self):
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


class FormatTimeInSecondToHumanReadableTest:
    def test_format_single_second(self):
        time_in_second = 1
        assert format_time_in_second_to_human_readable(time_in_second) == "1 seconde"

    @pytest.mark.parametrize(
        "time_in_second",
        [
            2,
            59,
        ],
    )
    def test_format_many_seconds(self, time_in_second):
        assert format_time_in_second_to_human_readable(time_in_second) == f"{time_in_second} secondes"

    def test_format_single_minute(self):
        time_in_second = 60
        assert format_time_in_second_to_human_readable(time_in_second) == "1 minute"

    @pytest.mark.parametrize(
        "time_in_second,time_in_unit",
        [
            (60 * 2, 2),
            (60 * 59, 59),
        ],
    )
    def test_format_many_minutes(self, time_in_second, time_in_unit):
        assert format_time_in_second_to_human_readable(time_in_second) == f"{time_in_unit} minutes"

    def test_format_single_hour(self):
        time_in_second = 60 * 60
        assert format_time_in_second_to_human_readable(time_in_second) == "1 heure"

    @pytest.mark.parametrize(
        "time_in_second,time_in_unit",
        [
            (60 * 60 * 2, 2),
            (60 * 60 * 23, 23),
        ],
    )
    def test_format_many_hours(self, time_in_second, time_in_unit):
        assert format_time_in_second_to_human_readable(time_in_second) == f"{time_in_unit} heures"

    def test_format_single_day(self):
        time_in_second = 60 * 60 * 24
        assert format_time_in_second_to_human_readable(time_in_second) == "1 jour"

    @pytest.mark.parametrize(
        "time_in_second,time_in_unit",
        [
            (60 * 60 * 24 * 2, 2),
            (60 * 60 * 24 * 6, 6),
        ],
    )
    def test_format_many_days(self, time_in_second, time_in_unit):
        assert format_time_in_second_to_human_readable(time_in_second) == f"{time_in_unit} jours"

    def test_format_single_week(self):
        time_in_second = 60 * 60 * 24 * 7
        assert format_time_in_second_to_human_readable(time_in_second) == "1 semaine"

    def test_format_many_weeks(self):
        time_in_second = 60 * 60 * 24 * 7 * 2
        assert format_time_in_second_to_human_readable(time_in_second) == "2 semaines"
