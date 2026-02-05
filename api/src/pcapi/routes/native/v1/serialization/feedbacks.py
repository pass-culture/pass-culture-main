from typing import Annotated

from pydantic import Field

from pcapi.routes.serialization import ConfiguredBaseModel


Feedback = Annotated[str, Field(min_length=1, max_length=800, strip_whitespace=True)]


class PostFeedbackBody(ConfiguredBaseModel):
    feedback: Feedback
