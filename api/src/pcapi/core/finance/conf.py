import decimal
from enum import Enum

from . import models


GRANT_18_VALIDITY_IN_YEARS = 2

GRANTED_DEPOSIT_AMOUNT_15 = decimal.Decimal(20)
GRANTED_DEPOSIT_AMOUNT_16 = decimal.Decimal(30)
GRANTED_DEPOSIT_AMOUNT_17 = decimal.Decimal(30)
GRANTED_DEPOSIT_AMOUNT_18_v1 = decimal.Decimal(500)
GRANTED_DEPOSIT_AMOUNT_18_v2 = decimal.Decimal(300)


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
    16: models.RecreditType.RECREDIT_16,
    17: models.RecreditType.RECREDIT_17,
}

RECREDIT_TYPE_AMOUNT_MAPPING = {
    models.RecreditType.RECREDIT_16: GRANTED_DEPOSIT_AMOUNT_16,
    models.RecreditType.RECREDIT_17: GRANTED_DEPOSIT_AMOUNT_17,
}


class BaseSpecificCaps:
    DIGITAL_CAP = None
    PHYSICAL_CAP = None

    def __init__(self, digital_cap: decimal.Decimal | None, physical_cap: decimal.Decimal | None) -> None:
        self.DIGITAL_CAP = digital_cap
        self.PHYSICAL_CAP = physical_cap

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
    def __init__(self) -> None:
        super().__init__(digital_cap=None, physical_cap=None)


class Grant18SpecificCapsV1(BaseSpecificCaps):
    def __init__(self) -> None:
        super().__init__(digital_cap=decimal.Decimal(200), physical_cap=decimal.Decimal(200))


class Grant18SpecificCapsV2(BaseSpecificCaps):
    def __init__(self) -> None:
        super().__init__(digital_cap=decimal.Decimal(100), physical_cap=None)


SPECIFIC_CAPS = {
    models.DepositType.GRANT_15_17: {
        1: GrantUnderageSpecificCaps(),
    },
    models.DepositType.GRANT_18: {
        1: Grant18SpecificCapsV1(),
        2: Grant18SpecificCapsV2(),
    },
}


# TODO(fseguin|dbaty, 2022-01-11): maybe merge with core.categories.subcategories.ReimbursementRuleChoices ?
class RuleGroups(Enum):
    STANDARD = dict(
        label="Barème général",
        position=1,
    )
    BOOK = dict(
        label="Barème livres",
        position=2,
    )
    NOT_REIMBURSED = dict(
        label="Barème non remboursé",
        position=3,
    )
    CUSTOM = dict(
        label="Barème dérogatoire",
        position=4,
    )
    DEPRECATED = dict(
        label="Barème désuet",
        position=5,
    )
