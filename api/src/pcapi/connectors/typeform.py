"""
A client for Typeform API.
API Documentation: https://www.typeform.com/developers/
"""

import hashlib
import json
import logging
import typing
from datetime import datetime

import pydantic.v1 as pydantic_v1

from pcapi import settings
from pcapi.utils import email as email_utils
from pcapi.utils import module_loading
from pcapi.utils import requests


logger = logging.getLogger(__name__)


class TypeformException(Exception):
    pass  # base class, never raised directly


class TypeformApiException(TypeformException):
    pass  # error from the API itself


class NotFoundException(TypeformException):
    pass


class TypeformQuestion(pydantic_v1.BaseModel):
    field_id: str
    title: str


class TypeformForm(pydantic_v1.BaseModel):
    form_id: str
    title: str
    date_created: datetime
    fields: list[TypeformQuestion] = []


class TypeformAnswer(pydantic_v1.BaseModel):
    field_id: str
    choice_id: str | None = None
    text: str | None = None


class TypeformResponse(pydantic_v1.BaseModel):
    response_id: str
    date_submitted: datetime
    phone_number: str | None
    email: str | None
    answers: list[TypeformAnswer]


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.TYPEFORM_BACKEND)
    return backend_class()


def search_forms(search_query: str) -> list[TypeformForm]:
    return _get_backend().search_forms(search_query)


def get_form(form_id: str) -> TypeformForm:
    return _get_backend().get_form(form_id)


def get_responses(
    form_id: str, *, num_results: int = 100, sort: str = "submitted_at,desc", since: datetime | None = None
) -> list[TypeformResponse]:
    return _get_backend().get_responses(
        form_id=form_id,
        num_results=num_results,
        since=since,
        sort=sort,
    )


def get_responses_generator(
    last_date_retriever: typing.Callable[[], datetime | None], form_id: str
) -> typing.Iterator[TypeformResponse]:
    previous_date = object()
    while True:
        last_date = last_date_retriever()
        if last_date == previous_date:
            logger.error(
                "typeform import error: infinite loop detected",
                extra={"last_chronicle_id": str(last_date), "form_id": form_id},
            )
            break
        previous_date = last_date
        forms = get_responses(
            form_id=form_id,
            num_results=settings.TYPEFORM_IMPORT_CHUNK_SIZE,
            sort="submitted_at,asc",
            since=last_date,
        )
        yield from forms

        if len(forms) < settings.TYPEFORM_IMPORT_CHUNK_SIZE:
            break


class BaseBackend:
    def search_forms(self, search_query: str) -> list[TypeformForm]:
        raise NotImplementedError()

    def get_form(self, form_id: str) -> TypeformForm:
        raise NotImplementedError()

    def get_responses(
        self, form_id: str, num_results: int = 100, sort: str = "submitted_at,desc", since: datetime | None = None
    ) -> list[TypeformResponse]:
        raise NotImplementedError()


class TestingBackend(BaseBackend):
    TITLES = ["Opération spéciale", "Jeu concours", "Jury"]
    QUESTIONS = ["Quel est ton prénom ?", "Où habites-tu ?", "Pourquoi veux-tu gagner ?"]

    def search_forms(self, search_query: str) -> list[TypeformForm]:
        return []

    def get_form(self, form_id: str) -> TypeformForm:
        title_index = sum(ord(i) for i in form_id) % len(self.TITLES)
        title = f"{self.TITLES[title_index]} {form_id}"
        return TypeformForm(
            form_id=form_id,
            title=title,
            date_created=datetime.utcnow(),
            fields=[
                TypeformQuestion(field_id=f"{form_id}-{i:04}", title=question)
                for i, question in enumerate(self.QUESTIONS)
            ],
        )

    def get_responses(
        self, form_id: str, num_results: int = 100, sort: str = "submitted_at,desc", since: datetime | None = None
    ) -> list[TypeformResponse]:
        return [
            TypeformResponse(
                response_id=f"{form_id}-response",
                date_submitted=datetime.utcnow(),
                phone_number="0199000123",
                email="spilgrim@example.com",
                answers=[
                    TypeformAnswer(field_id=f"{form_id}-0000", choice_id=None, text="Scott"),
                    TypeformAnswer(field_id=f"{form_id}-0001", choice_id=None, text="Dans le sac de Ramona"),
                    TypeformAnswer(field_id=f"{form_id}-0002", choice_id=None, text="Pour payer le bus"),
                ],
            )
        ]


def _strip(text: str | None) -> str | None:
    return text.strip() if text is not None else None


class TypeformBackend(BaseBackend):
    base_url = "https://api.eu.typeform.com"

    def _get(
        self,
        path: str,
        params: dict | None = None,
        timeout: int | float | None = None,
    ) -> dict:
        url = self.base_url + path
        try:
            response = requests.get(
                url, headers={"Authorization": "Bearer " + settings.TYPEFORM_API_KEY}, params=params, timeout=timeout
            )
        except requests.exceptions.RequestException as exc:
            msg = "Network error on Typeform API"
            logger.exception(msg, extra={"exc": exc, "url": url})
            raise TypeformApiException(msg) from exc

        if response.status_code == 404:
            raise NotFoundException(url)

        if not response.ok:
            logger.error(
                "Error from Typeform API",
                extra={
                    "url": url,
                    "status_code": response.status_code,
                    "message": response.text,
                },
            )
            raise TypeformApiException(f"Error {response.status_code} response from Typeform API: {url}")

        try:
            data = response.json()
        except json.JSONDecodeError:
            raise TypeformApiException("Unexpected non-JSON response from Typeform API")
        return data

    def _extract_questions(self, fields: dict) -> list[TypeformQuestion]:
        questions = []
        for field in fields:
            if "fields" in field.get("properties", {}):
                questions += self._extract_questions(field["properties"]["fields"])
            elif field["type"] not in ("phone_number", "email"):
                questions.append(TypeformQuestion(field_id=field["id"], title=field["title"].strip()))
        return questions

    def _search_forms(self, search_query: str, page: int) -> tuple[list[TypeformForm], int]:
        """
        Documentation: https://www.typeform.com/developers/create/reference/retrieve-forms/
        """
        path = "/forms"
        data = self._get(
            path,
            params={
                "search": search_query,
                "page_size": 200,
                "sort_by": "created_at",
                "order_by": "desc",
                "page": page,
            },
        )
        page_count = data.get("page_count", 1)
        forms = [
            TypeformForm(
                form_id=item["id"],
                title=item["title"].strip(),
                date_created=datetime.fromisoformat(
                    item["created_at"],
                ),
            )
            for item in data.get("items", [])
        ]
        return forms, page_count

    def search_forms(self, search_query: str) -> list[TypeformForm]:
        """
        Handle the pagination for when we need to retrieve more than 200 forms
        """
        forms, page_count = self._search_forms(search_query=search_query, page=1)
        # we already have page 1 and the page index starts at 1
        for page in range(2, page_count + 1):
            forms += self._search_forms(search_query, page=page)[0]
        return forms

    def get_form(self, form_id: str) -> TypeformForm:
        """
        Documentation: https://www.typeform.com/developers/create/reference/retrieve-form/
        """
        path = f"/forms/{form_id}"
        data = self._get(path)
        return TypeformForm(
            form_id=data["id"],
            title=data["title"].strip(),
            date_created=datetime.fromisoformat(data["created_at"]),
            fields=self._extract_questions(data.get("fields", {})),
        )

    def get_responses(
        self, form_id: str, num_results: int = 100, sort: str = "submitted_at,desc", since: datetime | None = None
    ) -> list[TypeformResponse]:
        """
        Documentation: https://www.typeform.com/developers/responses/reference/retrieve-responses/
        """
        path = f"/forms/{form_id}/responses"
        params = {
            "page_size": num_results,
            "response_type": "completed",
            "sort": sort,
        }
        if since is not None:
            params["since"] = since.isoformat()

        data = self._get(path, params=params)

        responses = []

        for item in data.get("items", []):
            phone_number = None
            email = None
            answers = []

            if not item.get("answers"):
                # ignore a response without answers or when `answers` field is null
                continue
            for answer in item["answers"]:
                match answer["type"]:
                    case "phone_number":
                        phone_number = _strip(answer["phone_number"])
                    case "email":
                        email = email_utils.sanitize_email(answer["email"]) if answer["email"] else None
                    case "boolean":
                        answers.append(
                            TypeformAnswer(field_id=answer["field"]["id"], text="Oui" if answer["boolean"] else "Non")
                        )
                    case "choice":
                        answers.append(
                            TypeformAnswer(
                                field_id=answer["field"]["id"],
                                text=answer["choice"].get("label"),
                                choice_id=answer["choice"]["id"],
                            )
                        )
                    case "choices":
                        choice_id = hashlib.sha1(b" ".join(i.encode() for i in answer["choices"]["ids"])).hexdigest()
                        text = "\n".join(answer["choices"]["labels"]) if "labels" in answer["choices"] else None
                        answers.append(
                            TypeformAnswer(
                                field_id=answer["field"]["id"],
                                text=text,
                                choice_id=choice_id,
                            )
                        )
                    case "date":
                        answers.append(
                            TypeformAnswer(
                                field_id=answer["field"]["id"],
                                text=datetime.fromisoformat(answer["date"]).strftime("%d/%m/%Y"),
                            )
                        )
                    case "number" | "text" | "url" | "file_url":
                        answers.append(
                            TypeformAnswer(field_id=answer["field"]["id"], text=_strip(str(answer[answer["type"]])))
                        )
                    case _:
                        raise ValueError("Unexpected answer type from Typeform API: %s" % (answer["type"],))

            if email is None and phone_number is None:
                # Ignore forms not completed (e.g. user does not accept conditions)
                continue

            responses.append(
                TypeformResponse(
                    response_id=item["response_id"],
                    date_submitted=datetime.fromisoformat(item["submitted_at"]),
                    phone_number=phone_number,
                    email=email,
                    answers=answers,
                )
            )

        return responses
