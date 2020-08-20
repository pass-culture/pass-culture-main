class CantRegisterBeneficiary(Exception):
    pass


class BeneficiaryIsADupplicate(CantRegisterBeneficiary):
    pass


class BeneficiaryIsNotEligible(CantRegisterBeneficiary):
    pass
