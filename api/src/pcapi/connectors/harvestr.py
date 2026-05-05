import enum

from pydantic import BaseModel
from pydantic import EmailStr

from pcapi import settings
from pcapi.utils import requests


_HARVESTR_REST_API_URL = "https://rest.harvestr.io"


class HaverstrMessageOriginEnum(str, enum.Enum):
    PRO = "PRO"
    NATIVE_APP = "NATIVE_APP"


class HaverstrRequester(BaseModel):
    type: str = "USER"
    name: str
    externalUid: str
    email: EmailStr
    origin: HaverstrMessageOriginEnum = HaverstrMessageOriginEnum.PRO


# Doc: https://developers.harvestr.io/api/create-a-message/
def create_message(title: str, content: str, requester: HaverstrRequester, *, labels: list[str] | None = None) -> None:
    integration_url = (
        settings.WEBAPP_V2_URL if requester.origin == HaverstrMessageOriginEnum.NATIVE_APP else settings.PRO_URL
    )
    response = requests.post(
        f"{_HARVESTR_REST_API_URL}/v1/message",
        json={
            "integrationId": settings.ENV,
            "integrationUrl": integration_url,
            "channel": "FORM",
            "title": title,
            "content": content,
            "labels": labels,
            "requester": requester.model_dump(),
        },
        headers={"X-Harvestr-Private-App-Token": settings.HARVESTR_API_KEY},
    )
    response.raise_for_status()
