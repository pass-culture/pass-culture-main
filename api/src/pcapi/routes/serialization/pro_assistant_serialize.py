import pydantic as pydantic_v2

from pcapi.routes.serialization import HttpBodyModel


MAX_MESSAGE_LENGTH = 500


class PostProAssistantMessageBodyModel(HttpBodyModel):
    message: str = pydantic_v2.Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)
    conversation_id: str | None = pydantic_v2.Field(default=None, pattern=r"^[0-9a-f]{32}$")
    offerer_id: int | None = None
    current_path: str | None = pydantic_v2.Field(default=None, max_length=200)


class ProAssistantLinkResponseModel(HttpBodyModel):
    label: str
    path: str


class ProAssistantHelpArticleResponseModel(HttpBodyModel):
    title: str
    url: str


class PostProAssistantMessageResponseModel(HttpBodyModel):
    conversation_id: str
    answer: str
    links: list[ProAssistantLinkResponseModel]
    help_articles: list[ProAssistantHelpArticleResponseModel]
    out_of_scope: bool
