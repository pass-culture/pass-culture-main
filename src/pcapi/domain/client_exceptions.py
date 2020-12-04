class ClientError(Exception):
    def __init__(self, field: str, error: str):
        super().__init__()
        self.errors = {field: [error]}
