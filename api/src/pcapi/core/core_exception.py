# generic core exception, inherited by all business errors raised in core modules


class ClientError(Exception):
    def __init__(self, field: str, error: str):
        super().__init__()
        self.errors = {field: [error]}


class CoreException(Exception):
    def __init__(self, errors: dict | None = None):
        self.errors = errors or {self.__class__.__name__: [str(self)]}
        super().__init__()

    def add_error(self, field: str, error: str) -> None:
        if len(self.errors) == 1 and self.__class__.__name__ in self.errors:
            self.errors.pop(self.__class__.__name__, "")

        if field in self.errors:
            self.errors[field].append(error)
        else:
            self.errors[field] = [error]
