from domain.beneficiary.beneficiary import Beneficiary


def create_domain_beneficiary(identifier: int = None,
                              email: str = 'john.doe@example.com',
                              first_name: str = None,
                              last_name: str = None,
                              department_code: str = '93',
                              can_book_free_offers: bool = True,
                              wallet_balance: int = None) -> Beneficiary:
    user = Beneficiary(identifier=identifier,
                can_book_free_offers=can_book_free_offers,
                email=email,
                first_name=first_name,
                last_name=last_name,
                department_code=department_code,
                wallet_balance=wallet_balance)

    return user
