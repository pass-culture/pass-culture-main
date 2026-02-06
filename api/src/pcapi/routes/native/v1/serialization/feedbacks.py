from typing import Annotated

from pydantic import Field

from pcapi.routes.serialization import HttpBodyModel


class PostFeedbackBody(HttpBodyModel):
    feedback: Annotated[str, Field(min_length=1, max_length=800, strip_whitespace=True)]
