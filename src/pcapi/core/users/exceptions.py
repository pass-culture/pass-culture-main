class CredentialsException(Exception):
    pass


class InvalidIdentifier(CredentialsException):
    pass


class InvalidPassword(CredentialsException):
    pass


class UnvalidatedAccount(CredentialsException):
    pass
