from dataclasses import asdict
from typing import Iterable

from pcapi.core.users import testing as users_testing
from pcapi.tasks.serialization import sendinblue_tasks

from .. import models
from .. import testing
from .base import BaseBackend


class TestingBackend(BaseBackend):
    """A backend that stores email in a global Python list that is
    accessible from tests.
    """

    def send_mail(
        self,
        recipients: Iterable[str],
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: Iterable[str] = (),
    ) -> None:
        sent_data = asdict(data)
        sent_data["To"] = ", ".join(recipients)
        if bcc_recipients:
            sent_data["Bcc"] = ", ".join(bcc_recipients)
        testing.outbox.append(sent_data)

    def create_contact(self, payload: sendinblue_tasks.UpdateSendinblueContactRequest) -> None:
        users_testing.sendinblue_requests.append(
            {"email": payload.email, "attributes": payload.attributes, "emailBlacklisted": payload.emailBlacklisted}
        )

    def delete_contact(self, contact_email: str) -> None:
        users_testing.sendinblue_requests.append({"email": contact_email, "action": "delete"})

    def get_contact_url(self, contact_email: str) -> str | None:
        users_testing.sendinblue_requests.append({"email": contact_email, "action": "get_contact_url"})
        return None

    def get_raw_contact_data(self, contact_email: str) -> dict:
        users_testing.sendinblue_requests.append({"email": contact_email, "action": "get_raw_contact_data"})
        if contact_email == "valid_email@example.com":
            # dict from brevo documentation
            return {
                "email": "valid_email@example.com",
                "id": 42,
                "emailBlacklisted": False,
                "smsBlacklisted": False,
                "createdAt": "2017-05-02T16:40:31Z",
                "modifiedAt": "2017-05-02T16:40:31Z",
                "attributes": {
                    "FIRST_NAME": "valid",
                    "LAST_NAME": "email",
                    "SMS": "3087433387669",
                    "CIV": "1",
                    "DOB": "1986-04-13",
                    "ADDRESS": "987 5th avenue",
                    "ZIP_CODE": "87544",
                    "CITY": "New-York",
                    "AREA": "NY",
                },
                "listIds": [40],
                "statistics": {
                    "messagesSent": [
                        {"campaignId": 21, "eventTime": "2016-05-03T20:15:13Z"},
                        {"campaignId": 42, "eventTime": "2016-10-17T10:30:01Z"},
                    ],
                    "opened": [
                        {"campaignId": 21, "count": 2, "eventTime": "2016-05-03T21:24:56Z", "ip": "66.249.93.118"},
                        {"campaignId": 68, "count": 1, "eventTime": "2017-01-30T13:56:40Z", "ip": "66.249.93.217"},
                    ],
                    "clicked": [
                        {
                            "campaignId": 21,
                            "links": [
                                {
                                    "count": 2,
                                    "eventTime": "2016-05-03T21:25:01Z",
                                    "ip": "66.249.93.118",
                                    "url": "https://url.domain.com/fbe5387ec717e333628380454f68670010b205ff/1/go?uid={EMAIL}&utm_source=brevo&utm_campaign=test_camp&utm_medium=email",
                                }
                            ],
                        }
                    ],
                    "delivered": [
                        {"campaignId": 21, "count": 2, "eventTime": "2016-05-03T21:24:56Z", "ip": "66.249.93.118"}
                    ],
                },
            }
        return {}
