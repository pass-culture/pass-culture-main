# Values in SettlementBatch when missing in RefLot and DescLot.
# Any Settlement must be associated with a SettlementBatch, so this fallback is used.
# Hopefully this should not happen, but data may be incorrect in database and we don't want to ignore a settlement.
MISSING_BATCH_NAME_VALUE = "UNKNOWN"
MISSING_BATCH_LABEL_VALUE = "UNKNOWN"
