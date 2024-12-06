"""
A client for Typeform API.
API Documentation: https://www.typeform.com/developers/
"""

from datetime import datetime
import json
import logging

import pydantic.v1 as pydantic_v1

from pcapi import settings
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
        return []


def _strip(text: str | None) -> str | None:
    return text.strip() if text is not None else None


class TypeformBackend(BaseBackend):
    base_url = "https://api.typeform.com"

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
            logger.error("Error from Typeform API", extra={"url": url, "status_code": response.status_code})
            raise TypeformApiException(f"Error {response.status_code} response from Typeform API: {url}")

        try:
            data = response.json()
        except json.JSONDecodeError:
            raise TypeformApiException("Unexpected non-JSON response from Typeform API")
        return data

    def _extract_questions(self, fields: dict) -> list[TypeformQuestion]:
        questions = []
        for field in fields:
            if "fields" in field["properties"]:
                questions += self._extract_questions(field["properties"]["fields"])
            elif field["type"] in ("multiple_choice", "short_text", "long_text"):
                questions.append(TypeformQuestion(field_id=field["id"], title=field["title"].strip()))
        return questions

    def search_forms(self, search_query: str) -> list[TypeformForm]:
        """
        Documentation: https://www.typeform.com/developers/create/reference/retrieve-forms/
        """
        path = "/forms"
        data = self._get(
            path, params={"search": search_query, "page_size": 20, "sort_by": "created_at", "order_by": "desc"}
        )
        return [
            TypeformForm(
                form_id=item["id"], title=item["title"].strip(), date_created=datetime.fromisoformat(item["created_at"])
            )
            for item in data.get("items", [])
        ]

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
            fields=self._extract_questions(data["fields"]),
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

            for answer in item["answers"]:
                match answer["type"]:
                    case "phone_number":
                        phone_number = _strip(answer["phone_number"])
                    case "email":
                        email = _strip(answer["email"])
                    case "choice":
                        answers.append(
                            TypeformAnswer(
                                field_id=answer["field"]["id"],
                                text=answer["choice"].get("label"),
                                choice_id=answer["choice"]["id"],
                            )
                        )
                    case "number":
                        answers.append(TypeformAnswer(field_id=answer["field"]["id"], text=str(answer["number"])))
                    case "text":
                        answers.append(TypeformAnswer(field_id=answer["field"]["id"], text=_strip(answer["text"])))
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
