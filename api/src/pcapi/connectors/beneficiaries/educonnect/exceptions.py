class EduconnectAuthenticationException(Exception):
    pass


class ResponseTooOld(EduconnectAuthenticationException):
    pass


class ParsingError(EduconnectAuthenticationException):
    parsed_dict: dict
    logout_url: str | None

    def __init__(self, parsed_dict: dict, logout_url: str, *args: object) -> None:
        super().__init__(*args)
        self.parsed_dict = parsed_dict
        self.logout_url = logout_url


class UserTypeNotStudent(EduconnectAuthenticationException):
    request_id: str
    user_type: str | None
    logout_url: str

    def __init__(self, request_id: str, user_type: str | None, logout_url: str, *args: object) -> None:
        super().__init__(*args)
        self.request_id = request_id
        self.user_type = user_type
        self.logout_url = logout_url
