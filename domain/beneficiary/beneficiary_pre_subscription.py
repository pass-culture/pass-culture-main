from datetime import datetime

from domain.postal_code.postal_code import PostalCode


class BeneficiaryPreSubscription(object):
    def __init__(self,
                 activity: str,
                 civility: str,
                 date_of_birth: datetime,
                 email: str,
                 first_name: str,
                 last_name: str,
                 phone_number: str,
                 postal_code: str
                 ):
        self.activity = activity
        self.civility = civility
        self.date_of_birth = date_of_birth
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.postal_code = postal_code

    @property
    def public_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @property
    def department_code(self) -> str:
        return PostalCode(self.postal_code).get_departement_code()
