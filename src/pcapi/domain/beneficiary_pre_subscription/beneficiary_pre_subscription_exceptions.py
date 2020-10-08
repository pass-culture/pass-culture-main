class CantRegisterBeneficiary(Exception):
    pass


class BeneficiaryIsADuplicate(CantRegisterBeneficiary):
    pass


class BeneficiaryIsNotEligible(CantRegisterBeneficiary):
    pass
