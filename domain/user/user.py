class User(object):
    def __init__(self,
                 identifier: int,
                 can_book_free_offers: bool,
                 email: str,
                 first_name: str,
                 last_name: str,
                 department_code: str,
                 wallet_balance: float,
                 ):
        self.identifier = identifier
        self.can_book_free_offers = can_book_free_offers
        self.email = email
        self.firstName = first_name
        self.lastName = last_name
        self.departmentCode = department_code
        self.wallet_balance = wallet_balance
