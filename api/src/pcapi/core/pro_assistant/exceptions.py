class ProAssistantException(Exception):
    pass


class ProAssistantRateLimited(ProAssistantException):
    pass


class ProAssistantUnavailable(ProAssistantException):
    pass


class ConversationTooLong(ProAssistantException):
    pass
