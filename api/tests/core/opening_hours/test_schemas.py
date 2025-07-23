from datetime import time

import pytest

from pcapi.core.opening_hours import schemas


pytestmark = pytest.mark.usefixtures("db_session")


class WeekdayOpeningHoursTimespansTest:
    def test_many_days_with_some_timespans_or_not_is_ok(self):
        oh = schemas.WeekdayOpeningHoursTimespans(
            MONDAY=[["10:00", "13:00"], ["14:00", "17:00"]],
            FRIDAY=[["12:00", "19:00"]],
            SUNDAY=None,
        )

        assert oh.MONDAY == [["10:00", "13:00"], ["14:00", "17:00"]]
        assert oh.FRIDAY == [["12:00", "19:00"]]

    @pytest.mark.parametrize(
        "timespans, expected_error_message",
        [
            ([["10:00", "13:00", "19:00"]], "ensure this value has at most 2 items"),
            ([["10:00"]], "ensure this value has at least 2 items"),
            ([["10:00"]], "ensure this value has at least 2 items"),
            ([[]], "ensure this value has at least 2 items"),
            ([], "ensure this value has at least 1 items"),
        ],
    )
    def test_invalid_opening_hour_timespans_lengths_is_not_ok(self, timespans, expected_error_message):
        with pytest.raises(ValueError, match=expected_error_message):
            schemas.WeekdayOpeningHoursTimespans(MONDAY=timespans)

    @pytest.mark.parametrize(
        "timespans",
        [
            [["1:", "10:00"]],  # should be 01:00 (minutes missing)
            [["1:00", "10:00"]],  # should be 01:00
            [["29:00", "10:00"]],  # hour error
            [["24:00", "10:00"]],  # hour error (should be 00:00)
            [["12:99", "10:00"]],  # minutes error
            [["1200", "10:00"]],  # missing time separator
            [["12T01", "10:00"]],  # unexpected time separator
            [["12 02", "10:00"]],  # another unexpected time separator
            [["10:00:00:00:00", "18:00"]],  # not a valid iso time
            [["10:00:00", "18:00"]],  # HH:MM expected, not HH:MM:SS
        ],
    )
    def test_malformed_timespan_is_not_ok(self, timespans):
        with pytest.raises(ValueError, match="string does not match regex"):
            schemas.WeekdayOpeningHoursTimespans(MONDAY=timespans)

    @pytest.mark.parametrize(
        "timespans",
        [
            [[time(10), "18:00"]],  # time objects are not valid (only str)
            [[10 * 60, "18:00"]],  # int is not a valid data type
        ],
    )
    def test_invalid_timespan_data_type_is_not_ok(self, timespans):
        with pytest.raises(ValueError, match="str type expected"):
            schemas.WeekdayOpeningHoursTimespans(MONDAY=timespans)

    def test_null_timespan_is_not_ok(self):
        with pytest.raises(ValueError, match="none is not an allowed value"):
            schemas.WeekdayOpeningHoursTimespans(MONDAY=[[None, "18:00"]])

    @pytest.mark.parametrize(
        "timespans",
        [
            [["10:00", "18:00"], ["12:00", "15:00"]],  # overlap: inside
            [["10:00", "16:00"], ["12:00", "19:00"]],  # overlap: inside/outside
        ],
    )
    def test_overlapping_timespans_is_not_ok(self, timespans):
        with pytest.raises(ValueError, match="overlapping"):
            schemas.WeekdayOpeningHoursTimespans(MONDAY=timespans)

    @pytest.mark.parametrize(
        "weekday, expected_error_message, expected_error_class",
        [
            ("MNDAY", "extra fields not permitted", ValueError),
            ("monday", "extra fields not permitted", ValueError),
            (1, "keywords must be strings", TypeError),
            (None, "keywords must be strings", TypeError),
        ],
    )
    def test_unknown_weekday_is_not_valid(self, weekday, expected_error_message, expected_error_class):
        with pytest.raises(expected_error_class, match=expected_error_message):
            schemas.WeekdayOpeningHoursTimespans(**{weekday: [["10:00", "18:00"]]})
