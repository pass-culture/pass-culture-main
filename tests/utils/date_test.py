from utils.date import english_to_french_month

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
