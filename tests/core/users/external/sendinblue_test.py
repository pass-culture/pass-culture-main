from datetime import datetime
from decimal import Decimal

import pytest

from pcapi.core.users.external.models import UserAttributes
from pcapi.core.users.external.sendinblue import format_user_attributes
from pcapi.core.users.models import Credit
from pcapi.core.users.models import DomainsCredit


pytestmark = pytest.mark.usefixtures("db_session")


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
            "FIRSTNAME": "First name",
            "LASTNAME": "Last name",
            "IS_BENEFICIARY": True,
        }
