class CantRegisterBeneficiary(Exception):
    pass


class BeneficiaryIsADuplicate(CantRegisterBeneficiary):
    pass


class BeneficiaryIsNotEligible(CantRegisterBeneficiary):
    pass


class FraudDetected(CantRegisterBeneficiary):
    pass


class SuspiciousFraudDetected(CantRegisterBeneficiary):
    pass
