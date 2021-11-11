class CantRegisterBeneficiary(Exception):
    pass


class BeneficiaryIsADuplicate(CantRegisterBeneficiary):
    pass


class BeneficiaryIsNotEligible(CantRegisterBeneficiary):
    pass


class SubscriptionJourneyOnHold(CantRegisterBeneficiary):
    pass


class FraudDetected(CantRegisterBeneficiary):
    pass


class IdPieceNumberDuplicate(FraudDetected):
    pass


class SuspiciousFraudDetected(CantRegisterBeneficiary):
    pass
