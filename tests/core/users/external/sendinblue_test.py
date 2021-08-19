from datetime import datetime

import pytest

from pcapi.core.users.external.sendinblue import format_user_attributes

from . import common_user_attributes


pytestmark = pytest.mark.usefixtures("db_session")


class FormatUserAttributesTest:
    def test_format_attributes(self):
        formatted_attributes = format_user_attributes(common_user_attributes)

        assert formatted_attributes == {
            "BOOKED_OFFER_CATEGORIES": "CINEMA,LIVRE",
            "BOOKED_OFFER_SUBCATEGORIES": "ABO_LIVRE_NUMERIQUE,CARTE_CINE_ILLIMITE,CINE_PLEIN_AIR",
            "BOOKING_COUNT": 4,
            "DATE_CREATED": datetime(2021, 2, 6),
            "DATE_OF_BIRTH": datetime(2003, 5, 6),
            "DEPARTMENT_CODE": "12",
            "DEPOSIT_ACTIVATION_DATE": None,
            "DEPOSIT_EXPIRATION_DATE": None,
            "FIRSTNAME": "First name",
            "HAS_COMPLETED_ID_CHECK": True,
            "INITIAL_CREDIT": 500,
            "CREDIT": 480,
            "IS_BENEFICIARY": True,
            "IS_ELIGIBLE": True,
            "IS_EMAIL_VALIDATED": True,
            "IS_PRO": False,
            "LAST_BOOKING_DATE": datetime(2021, 5, 6),
            "LAST_FAVORITE_CREATION_DATE": None,
            "LAST_VISIT_DATE": None,
            "LASTNAME": "Last name",
            "MARKETING_EMAIL_SUBSCRIPTION": True,
            "POSTAL_CODE": None,
            "USER_ID": 1,
        }
