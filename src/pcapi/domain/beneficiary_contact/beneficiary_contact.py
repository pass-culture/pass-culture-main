class BeneficiaryContact(object):
    def __init__(self, email: str, date_of_birth: str, department_code: str):
        self.department_code = department_code
        self.date_of_birth = date_of_birth
        self.email = email
