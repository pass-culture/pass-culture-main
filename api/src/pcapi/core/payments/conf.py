from decimal import Decimal

from pcapi.core.payments.models import DepositType
from pcapi.core.payments.models import RecreditType


GRANT_18_VALIDITY_IN_YEARS = 2

GRANTED_DEPOSIT_AMOUNT_15 = Decimal(20)
GRANTED_DEPOSIT_AMOUNT_16 = Decimal(30)
GRANTED_DEPOSIT_AMOUNT_17 = Decimal(30)
GRANTED_DEPOSIT_AMOUNT_18_v1 = Decimal(500)
GRANTED_DEPOSIT_AMOUNT_18_v2 = Decimal(300)


GRANTED_DEPOSIT_AMOUNTS_FOR_UNDERAGE_BY_AGE = {
    15: GRANTED_DEPOSIT_AMOUNT_15,
    16: GRANTED_DEPOSIT_AMOUNT_16,
    17: GRANTED_DEPOSIT_AMOUNT_17,
}

GRANTED_DEPOSIT_AMOUNTS_FOR_18_BY_VERSION = {
    1: GRANTED_DEPOSIT_AMOUNT_18_v1,  # not used anymore, still present in database
    2: GRANTED_DEPOSIT_AMOUNT_18_v2,
}


RECREDIT_TYPE_AGE_MAPPING = {
    16: RecreditType.RECREDIT_16,
    17: RecreditType.RECREDIT_17,
}

RECREDIT_TYPE_AMOUNT_MAPPING = {
    RecreditType.RECREDIT_16: GRANTED_DEPOSIT_AMOUNT_16,
    RecreditType.RECREDIT_17: GRANTED_DEPOSIT_AMOUNT_17,
}


class BaseSpecificCaps:
    DIGITAL_CAP = None
    PHYSICAL_CAP = None

    # fmt: off
    def digital_cap_applies(self, offer): # type: ignore [no-untyped-def]
        return (
            offer.isDigital
            and bool(self.DIGITAL_CAP)
            and offer.subcategory.is_digital_deposit
        )

    def physical_cap_applies(self, offer): # type: ignore [no-untyped-def]
        return (
            not offer.isDigital
            and bool(self.PHYSICAL_CAP)
            and offer.subcategory.is_physical_deposit
        )
    # fmt: on


class GrantUnderageSpecificCaps(BaseSpecificCaps):
    DIGITAL_CAP = None
    PHYSICAL_CAP = None


class Grant18SpecificCapsV1(BaseSpecificCaps):
    DIGITAL_CAP = Decimal(200)  # type: ignore [assignment]
    PHYSICAL_CAP = Decimal(200)  # type: ignore [assignment]


class Grant18SpecificCapsV2(BaseSpecificCaps):
    DIGITAL_CAP = Decimal(100)  # type: ignore [assignment]
    PHYSICAL_CAP = None


SPECIFIC_CAPS = {
    DepositType.GRANT_15_17: {
        1: GrantUnderageSpecificCaps(),
    },
    DepositType.GRANT_18: {
        1: Grant18SpecificCapsV1(),
        2: Grant18SpecificCapsV2(),
    },
}
