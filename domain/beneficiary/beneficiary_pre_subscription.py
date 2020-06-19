class BeneficiaryPreSubscription(object):
    def __init__(self,
                 address: str,
                 birth_date: str,
                 city: str,
                 department_code: str,
                 email: str,
                 first_name: str,
                 gender: str,
                 last_name: str,
                 phone_number: str,
                 status: str
                 ):
        self.address = address
        self.birth_date = birth_date
        self.city = city
        self.department_code = department_code
        self.email = email
        self.first_name = first_name
        self.gender = gender
        self.last_name = last_name
        self.phone_number = phone_number
        self.status = status
