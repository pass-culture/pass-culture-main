import datetime

from utils.date import english_to_french_month, get_date_formatted_for_email, get_time_formatted_for_email


def test_english_to_french_month(app):
    # Given
    whatever_it_is_year = 2030
    month_numbers = range(1, 13)

    # When
    french_months = [
        english_to_french_month(whatever_it_is_year, month_number)
        for month_number in month_numbers
    ]

    # Then
    assert french_months == [
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre"
    ]


class GetDateFormattedForEmail:
    def test_should_return_day_followed_by_month_written_in_words(self):
        # Given
        december_23 = datetime.date(2019, 12, 23)

        # When
        date_formatted_for_email = get_date_formatted_for_email(december_23)

        # Then
        assert date_formatted_for_email == '23 décembre'

    def test_should_return_1_digit_day_when_day_is_less_than_10(self):
        # Given
        december_09 = datetime.date(2019, 12, 9)

        # When
        date_formatted_for_email = get_date_formatted_for_email(december_09)

        # Then
        assert date_formatted_for_email == '9 décembre'


class GetTimeFormattedForEmail:
    def test_should_return_hour_followed_by_two_digits_minutes(self):
        # Given
        twelve_o_clock = datetime.time(12, 0, 0, 0)

        # When
        time_formatted_for_email = get_time_formatted_for_email(twelve_o_clock)

        # Then
        assert time_formatted_for_email == '12h00'
