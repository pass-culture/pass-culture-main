from pydantic.v1 import BaseModel
from pydantic.v1 import EmailStr

from pcapi import settings
from pcapi.utils import requests


_HARVESTR_REST_API_URL = "https://rest.harvestr.io"


class HaverstrRequester(BaseModel):
    type: str = "USER"
    name: str
    externalUid: str | None
    email: EmailStr | None


# Doc: https://developers.harvestr.io/api/create-a-message/
def create_message(title: str, content: str, requester: HaverstrRequester, *, labels: list[str] | None = None) -> None:
    response = requests.post(
        f"{_HARVESTR_REST_API_URL}/v1/message",
        json={
            "integrationId": settings.ENV,
            "integrationUrl": settings.PRO_URL,
            "channel": "FORM",
            "title": title,
            "content": content,
            "labels": labels,
            "requester": requester.dict(),
        },
        headers={"X-Harvestr-Private-App-Token": settings.HARVESTR_API_KEY},
    )
    response.raise_for_status()
