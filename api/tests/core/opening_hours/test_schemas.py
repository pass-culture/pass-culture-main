from datetime import time

import pydantic
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
            ([[]], "ensure this value has at least 2 items"),
            ([], "ensure this value has at least 1 item"),
        ],
    )
    def test_invalid_opening_hour_timespans_lengths_is_not_ok(self, timespans, expected_error_message):
        with pytest.raises(pydantic.ValidationError, match=expected_error_message):
            schemas.WeekdayOpeningHoursTimespans(MONDAY=timespans)

    @pytest.mark.parametrize(
        "timespans,message",
        [
            pytest.param(
                [["1:", "10:00"]],
                "String should match pattern",
                id="should be 01:00 (minutes missing)",
            ),
            pytest.param(
                [["1:00", "10:00"]],
                "String should match pattern",
                id="should be 01:00",
            ),
            pytest.param(
                [["29:00", "10:00"]],
                "String should match pattern",
                id="hour error",
            ),
            pytest.param(
                [["24:00", "10:00"]],
                "String should match pattern",
                id="hour error (should be 00:00)",
            ),
            pytest.param(
                [["12:99", "10:00"]],
                "String should match pattern",
                id="minutes error",
            ),
            pytest.param(
                [["1200", "10:00"]],
                "String should match pattern",
                id="missing time separator",
            ),
            pytest.param(
                [["12T01", "10:00"]],
                "String should match pattern",
                id="unexpected time separator",
            ),
            pytest.param(
                [["12 02", "10:00"]],
                "String should match pattern",
                id="another unexpected time separator",
            ),
            pytest.param([["10:00:00:00:00", "18:00"]], "String should match pattern", id="not a valid iso time"),
            pytest.param([["10:00:00", "18:00"]], "String should match pattern", id="HH:MM expected, not HH:MM:SS"),
        ],
    )
    def test_malformed_timespan_is_not_ok(self, timespans, message):
        with pytest.raises(ValueError, match=message):
            schemas.WeekdayOpeningHoursTimespans(MONDAY=timespans)

    @pytest.mark.parametrize(
        "timespans",
        [
            pytest.param([[time(10), "18:00"]], id="time objects are not valid (only str)"),
            pytest.param([[10 * 60, "18:00"]], id="int is not a valid data type"),
            pytest.param([[None, "18:00"]], id="none is not an allowed value"),
        ],
    )
    def test_invalid_timespan_data_type_is_not_ok(self, timespans):
        with pytest.raises(ValueError, match="Input should be a valid string"):
            schemas.WeekdayOpeningHoursTimespans(MONDAY=timespans)

    @pytest.mark.parametrize(
        "timespans",
        [
            pytest.param([["10:00", "18:00"], ["12:00", "15:00"]], id="overlap: inside"),
            pytest.param([["10:00", "16:00"], ["12:00", "19:00"]], id="overlap: inside/outside"),
        ],
    )
    def test_overlapping_timespans_is_not_ok(self, timespans):
        with pytest.raises(ValueError, match="overlapping"):
            schemas.WeekdayOpeningHoursTimespans(MONDAY=timespans)

    @pytest.mark.parametrize(
        "weekday, expected_error_message, expected_error_class",
        [
            ("MNDAY", "Extra inputs are not permitted", ValueError),
            ("monday", "Extra inputs are not permitted", ValueError),
            (1, "keywords must be strings", TypeError),
            (None, "keywords must be strings", TypeError),
        ],
    )
    def test_unknown_weekday_is_not_valid(self, weekday, expected_error_message, expected_error_class):
        with pytest.raises(expected_error_class, match=expected_error_message):
            schemas.WeekdayOpeningHoursTimespans(**{weekday: [["10:00", "18:00"]]})
