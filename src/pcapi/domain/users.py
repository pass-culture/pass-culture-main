class ClientError(Exception):
    def __init__(self, field: str, error: str):
        super().__init__()
        self.errors = {field: [error]}


class UnauthorizedForAdminUser(ClientError):
    def __init__(self):
        super().__init__("global", "Le statut d'administrateur ne permet pas d'accéder au suivi des réservations")
