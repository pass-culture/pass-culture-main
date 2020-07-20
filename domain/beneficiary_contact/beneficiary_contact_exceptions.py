class AddNewBeneficiaryContactException(Exception):
    def __init__(self, field: str, error: str):
        self.errors = {field: [error]}
