from pcapi.routes.serialization import ConfiguredBaseModel
from pcapi.routes.serialization.base import RequiredStrippedString


class Feedback(RequiredStrippedString):
    max_length = 800


class PostFeedbackBody(ConfiguredBaseModel):
    feedback: Feedback
