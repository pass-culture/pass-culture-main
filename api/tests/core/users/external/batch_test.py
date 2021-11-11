from copy import deepcopy

import pytest

from pcapi.core.users.external.batch import format_user_attributes

from . import common_user_attributes


pytestmark = pytest.mark.usefixtures("db_session")

MAX_BATCH_PARAMETER_SIZE = 30


class FormatUserAttributesTest:
    def test_format_attributes(self):
        formatted_attributes = format_user_attributes(common_user_attributes)

        assert formatted_attributes == {
            "date(u.date_of_birth)": "2003-05-06T00:00:00",
            "date(u.date_created)": "2021-02-06T00:00:00",
            "date(u.deposit_expiration_date)": None,
            "date(u.last_booking_date)": "2021-05-06T00:00:00",
            "date(u.product_brut_x_use)": "2021-05-06T00:00:00",
            "u.credit": 48000,
            "u.departement_code": "12",
            "u.is_beneficiary": True,
            "ut.booking_categories": ["CINEMA", "LIVRE"],
            "u.marketing_push_subscription": True,
            "u.postal_code": None,
        }

        # ensure attributes keys are shorter than MAX_BATCH_PARAMETER_SIZE
        for attribute in formatted_attributes:
            if attribute.startswith("date"):
                attribute = attribute[5:-1]

            parameter_name = attribute.split(".")[1]
            assert len(parameter_name) <= MAX_BATCH_PARAMETER_SIZE

    def test_format_attributes_without_bookings(self):
        attributes = deepcopy(common_user_attributes)
        attributes.booking_categories = []
        attributes.last_booking_date = None

        formatted_attributes = format_user_attributes(attributes)

        assert formatted_attributes["date(u.last_booking_date)"] == None
        assert "ut.booking_categories" not in formatted_attributes
