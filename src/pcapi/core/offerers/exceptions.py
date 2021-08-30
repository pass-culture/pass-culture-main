class ApiKeyCountMaxReached(Exception):
    pass


class ApiKeyPrefixGenerationError(Exception):
    pass


class ApiKeyDeletionDenied(Exception):
    pass


class ValidationTokenNotFoundError(Exception):
    pass
