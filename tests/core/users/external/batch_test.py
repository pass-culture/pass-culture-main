from copy import deepcopy
from datetime import datetime
from decimal import Decimal

import pytest

from pcapi.core.users.external.batch import format_user_attributes
from pcapi.core.users.external.models import UserAttributes
from pcapi.core.users.models import Credit
from pcapi.core.users.models import DomainsCredit


pytestmark = pytest.mark.usefixtures("db_session")

MAX_BATCH_PARAMETER_SIZE = 30


class FormatUserAttributesTest:
    attributes = UserAttributes(
        domains_credit=DomainsCredit(
            all=Credit(initial=Decimal("500"), remaining=Decimal("480.00")),
            digital=Credit(initial=Decimal("200"), remaining=Decimal("200")),
            physical=Credit(initial=200, remaining=Decimal("180.00")),
        ),
        last_booking_date=datetime(2021, 5, 6),
        booking_categories=["ThingType.CINEMA", "ThingType.LIVRE"],
        date_created=datetime(2021, 2, 6),
        date_of_birth=datetime(2003, 5, 6),
        departement_code="12",
        deposit_expiration_date=None,
        first_name="First name",
        is_beneficiary=True,
        marketing_push_subscription=True,
        last_name="Last name",
        postal_code=None,
        products_use_date={"product_brut_x_use": datetime(2021, 5, 6)},
    )

    def test_format_attributes(self):
        formatted_attributes = format_user_attributes(self.attributes)

        assert formatted_attributes == {
            "date(u.date_of_birth)": "2003-05-06T00:00:00",
            "date(u.date_created)": "2021-02-06T00:00:00",
            "date(u.deposit_expiration_date)": None,
            "date(u.last_booking_date)": "2021-05-06T00:00:00",
            "date(u.product_brut_x_use)": "2021-05-06T00:00:00",
            "u.credit": 48000,
            "u.departement_code": "12",
            "u.is_beneficiary": True,
            "ut.booking_categories": ["ThingType.CINEMA", "ThingType.LIVRE"],
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
        attributes = deepcopy(self.attributes)
        attributes.booking_categories = []
        attributes.last_booking_date = None

        formatted_attributes = format_user_attributes(attributes)

        assert formatted_attributes["date(u.last_booking_date)"] == None
        assert "ut.booking_categories" not in formatted_attributes
