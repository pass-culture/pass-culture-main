from domain.client_exceptions import ClientError


class BeneficiaryDoesntExist(ClientError):
    def __init__(self):
        super().__init__('userId', 'userId ne correspond à aucun bénéficiaire')
