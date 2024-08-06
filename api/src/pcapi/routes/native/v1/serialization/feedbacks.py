from pcapi.core.offerers.schemas import RequiredStrippedString
from pcapi.routes.serialization import ConfiguredBaseModel


class Feedback(RequiredStrippedString):
    max_length = 800


class PostFeedbackBody(ConfiguredBaseModel):
    feedback: Feedback
