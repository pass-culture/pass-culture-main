from datetime import datetime

import pytest

from utils.date import ENGLISH_TO_FRENCH_MONTH

@pytest.mark.standalone
def test_english_to_french_month(app):
    # Given
    french_months = [
        ENGLISH_TO_FRENCH_MONTH[datetime(2030, month_number, 1).strftime("%B")]
        for month_number in range(1, 13)
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
