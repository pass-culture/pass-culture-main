class EduconnectAuthenticationException(Exception):
    pass


class ResponseTooOld(EduconnectAuthenticationException):
    pass


class ParsingError(EduconnectAuthenticationException):
    pass
