# generic core exception, inherited by all business errors raised in core modules


class ClientError(Exception):
    def __init__(self, field: str, error: str):
        super().__init__()
        self.errors = {field: [error]}


class CoreException(Exception):
    def __init__(self, errors: dict | None = None):
        self.errors = errors or {}
        super().__init__()

    def add_error(self, field: str, error: str) -> None:
        if field in self.errors:
            self.errors[field].append(error)
        else:
            self.errors[field] = [error]
