"""Connector to the Claude API (Anthropic) used by the pro assistant.

This is a mere proxy: prompt building, personal data redaction and answer
validation are done in `pcapi.core.pro_assistant`.
"""

import dataclasses
import functools
import json
import logging
import typing

import anthropic

from pcapi import settings
from pcapi.utils import module_loading


logger = logging.getLogger(__name__)

# Answers are short: this also caps the cost of a single request
MAX_OUTPUT_TOKENS = 4096
# Server-side fallback: when the model declines a request, the API retries it on
# the model recommended by Anthropic for that refusal category
SERVER_SIDE_FALLBACK_BETA = "server-side-fallback-2026-07-01"


class ProAssistantApiException(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class LlmUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0


@dataclasses.dataclass(frozen=True)
class LlmResult:
    # Assistant content blocks (thinking blocks included), to be sent back
    # unchanged in the next turn of the conversation
    content: list[dict]
    # Parsed JSON answer, None when the model declined or the answer was truncated
    output: dict | None
    stop_reason: str | None
    model: str
    usage: LlmUsage


def _get_backend() -> "BaseBackend":
    backend_class = module_loading.import_string(settings.PRO_ASSISTANT_BACKEND)
    return backend_class()


def generate(*, system: list[dict], messages: list[dict], output_schema: dict) -> LlmResult:
    return _get_backend().generate(system=system, messages=messages, output_schema=output_schema)


def count_tokens(*, system: list[dict], messages: list[dict]) -> int:
    return _get_backend().count_tokens(system=system, messages=messages)


class BaseBackend:
    def generate(self, *, system: list[dict], messages: list[dict], output_schema: dict) -> LlmResult:
        raise NotImplementedError()

    def count_tokens(self, *, system: list[dict], messages: list[dict]) -> int:
        raise NotImplementedError()


class TestingBackend(BaseBackend):
    def generate(self, *, system: list[dict], messages: list[dict], output_schema: dict) -> LlmResult:
        output = {
            "answer": "Pour créer une offre individuelle, cliquez sur **Créer une offre** puis suivez les étapes.",
            "route_ids": ["individual_offer_creation"],
            "help_article_ids": [],
            "out_of_scope": False,
        }
        return LlmResult(
            content=[{"type": "text", "text": json.dumps(output, ensure_ascii=False)}],
            output=output,
            stop_reason="end_turn",
            model="testing",
            usage=LlmUsage(input_tokens=100, output_tokens=50),
        )

    def count_tokens(self, *, system: list[dict], messages: list[dict]) -> int:
        # Rough estimate, without calling the API
        return len(json.dumps([system, messages], ensure_ascii=False)) // 4


@functools.cache
def _get_client() -> anthropic.Anthropic:
    # Required by the API when the key is not scoped to a workspace
    headers = {"anthropic-workspace-id": settings.ANTHROPIC_WORKSPACE_ID} if settings.ANTHROPIC_WORKSPACE_ID else None
    return anthropic.Anthropic(
        api_key=settings.ANTHROPIC_API_KEY,
        timeout=settings.PRO_ASSISTANT_TIMEOUT_IN_SECONDS,
        max_retries=1,
        default_headers=headers,
    )


def _get_error_message(exc: anthropic.APIStatusError) -> str | None:
    # The API explains what is wrong with the request (never the request content itself)
    error = exc.body.get("error") if isinstance(exc.body, dict) else None
    return str(error.get("message"))[:500] if isinstance(error, dict) else None


def _parse_output(response: anthropic.types.beta.BetaMessage) -> dict | None:
    if response.stop_reason != "end_turn":
        return None
    text = "".join(block.text for block in response.content if block.type == "text")
    try:
        output = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Claude API returned an invalid JSON answer", extra={"stop_reason": response.stop_reason})
        return None
    return output if isinstance(output, dict) else None


class AnthropicBackend(BaseBackend):
    def generate(self, *, system: list[dict], messages: list[dict], output_schema: dict) -> LlmResult:
        try:
            response = _get_client().beta.messages.create(
                model=settings.PRO_ASSISTANT_MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=typing.cast(typing.Any, system),
                messages=typing.cast(typing.Any, messages),
                output_config={
                    "effort": typing.cast(typing.Any, settings.PRO_ASSISTANT_EFFORT),
                    "format": {"type": "json_schema", "schema": output_schema},
                },
                betas=[SERVER_SIDE_FALLBACK_BETA],
                fallbacks="default",
            )
        except anthropic.RateLimitError as exc:
            logger.warning("Claude API rate limit reached", extra={"status_code": exc.status_code})
            raise ProAssistantApiException("rate limited") from exc
        except anthropic.APIStatusError as exc:
            logger.warning(
                "Claude API returned an error",
                extra={
                    "status_code": exc.status_code,
                    "error_type": type(exc).__name__,
                    "error_message": _get_error_message(exc),
                    "request_id": exc.request_id,
                },
            )
            raise ProAssistantApiException(f"status {exc.status_code}") from exc
        except anthropic.APIConnectionError as exc:
            logger.warning("Could not reach Claude API", extra={"error_type": type(exc).__name__})
            raise ProAssistantApiException("connection error") from exc

        if response.stop_reason == "refusal":
            logger.info(
                "Claude API declined a pro assistant request",
                extra={"category": response.stop_details.category if response.stop_details else None},
            )

        usage = response.usage
        return LlmResult(
            content=[block.model_dump(mode="json", by_alias=True, exclude_none=True) for block in response.content],
            output=_parse_output(response),
            stop_reason=response.stop_reason,
            model=response.model,
            usage=LlmUsage(
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                cache_creation_input_tokens=usage.cache_creation_input_tokens or 0,
                cache_read_input_tokens=usage.cache_read_input_tokens or 0,
            ),
        )

    def count_tokens(self, *, system: list[dict], messages: list[dict]) -> int:
        response = _get_client().beta.messages.count_tokens(
            model=settings.PRO_ASSISTANT_MODEL,
            system=typing.cast(typing.Any, system),
            messages=typing.cast(typing.Any, messages),
        )
        return response.input_tokens
