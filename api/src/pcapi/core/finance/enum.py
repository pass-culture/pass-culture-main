import enum


class DepositType(enum.Enum):
    GRANT_17_18 = "GRANT_17_18"
    # legacy deposit types that are present in the database
    GRANT_15_17 = "GRANT_15_17"
    GRANT_18 = "GRANT_18"
