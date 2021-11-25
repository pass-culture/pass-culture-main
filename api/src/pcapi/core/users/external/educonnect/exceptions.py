from typing import Optional


class EduconnectAuthenticationException(Exception):
    pass


class ResponseTooOld(EduconnectAuthenticationException):
    pass


class ParsingError(EduconnectAuthenticationException):
    pass


class UserTypeNotStudent(EduconnectAuthenticationException):
    request_id: str
    user_type: Optional[str]

    def __init__(self, request_id, user_type, *args: object) -> None:
        super().__init__(*args)
        self.request_id = request_id
        self.user_type = user_type
