class DmsGraphQLApiException(Exception):
    pass


class DmsGraphQLApiError(DmsGraphQLApiException):
    def __init__(self, errors: list[dict] | None):
        self.errors = errors
        super().__init__()

    @property
    def message(self) -> str | None:
        if not self.errors:
            return None
        return " ; ".join(item["message"] for item in self.errors)

    @property
    def code(self) -> str | None:
        if not self.errors:
            return None
        return ";".join(item.get("extensions", {}).get("code", "unknown") for item in self.errors)

    @property
    def is_not_found(self) -> bool:
        return self.code == "not_found"


class DmsGraphQLAPIConnectError(DmsGraphQLApiError):
    def __init__(self, message: str | None) -> None:
        self._message = message
        super().__init__(None)

    @property
    def message(self) -> str | None:
        return f"La connexion à Démarches-Simplifiées a échoué : {self._message}"
