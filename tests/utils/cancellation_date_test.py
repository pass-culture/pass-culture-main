from freezegun.api import freeze_time

from pcapi.utils.cancellation_date import get_cancellation_limit_date


class WhenItsAThing:
    def should_have_not_a_cancellation_limit_date(self):
        # given
        beginning_datetime = None

        # when
        cancellation_limit_date = get_cancellation_limit_date(beginning_datetime)

        # then
        assert cancellation_limit_date is None


@freeze_time("2020-09-01 00:00:00")
class WhenItsAnEvent:
    # It go through twice in spectree
    def should_have_a_cancellation_limit_date_when_cancellation_limit_date_already_exist(self):
        # given
        beginning_datetime = "2020-09-01T00:00:00Z"
        old_cancellation_limit_date = "2020-09-03T00:00:00Z"

        # when
        cancellation_limit_date = get_cancellation_limit_date(beginning_datetime, old_cancellation_limit_date)

        # then
        assert cancellation_limit_date == old_cancellation_limit_date

    def should_have_a_cancellation_limit_date_when_no_cancellation_limit_date_given_and_there_is_not_milliseconds(self):
        # given
        beginning_datetime = "2020-10-01T00:00:00Z"

        # when
        cancellation_limit_date = get_cancellation_limit_date(beginning_datetime, None)

        # then
        assert cancellation_limit_date == "2020-09-03T00:00:00Z"

    def should_have_a_cancellation_limit_date_when_no_cancellation_limit_date_given_and_there_is_milliseconds(self):
        # given
        beginning_datetime = "2020-10-01T00:00:00.000000Z"

        # when
        cancellation_limit_date = get_cancellation_limit_date(beginning_datetime, None)

        # then
        assert cancellation_limit_date == "2020-09-03T00:00:00Z"
