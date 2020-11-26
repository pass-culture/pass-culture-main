class Beneficiary:
    def __init__(
        self,
        identifier: int,
        is_beneficiary: bool,
        email: str,
        first_name: str,
        last_name: str,
        department_code: str,
        reset_password_token: str,
        wallet_balance: float,
    ):
        self.identifier = identifier
        self.is_beneficiary = is_beneficiary
        self.departmentCode = department_code
        self.email = email
        self.firstName = first_name
        self.lastName = last_name
        self.resetPasswordToken = reset_password_token
        self.wallet_balance = wallet_balance
