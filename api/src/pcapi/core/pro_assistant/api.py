import dataclasses
import datetime
import logging
import time
import uuid

from pcapi import settings
from pcapi.connectors import pro_assistant as pro_assistant_connector
from pcapi.core.pro_assistant import context as context_module
from pcapi.core.pro_assistant import conversation_store
from pcapi.core.pro_assistant import exceptions
from pcapi.core.pro_assistant import knowledge
from pcapi.core.pro_assistant import portal_map
from pcapi.core.pro_assistant import prompt
from pcapi.core.pro_assistant import redaction
from pcapi.utils import rate_limit
from pcapi.utils.redis import get_redis_client


logger = logging.getLogger(__name__)

MAX_ROUTE_LINKS = 3
MAX_HELP_ARTICLES = 2
MAX_ANSWER_LENGTH = 2000
FALLBACK_ANSWER = (
    "Je ne parviens pas à répondre à cette question pour le moment. "
    "Vous pouvez consulter le centre d'aide ou contacter nos équipes."
)

# USD per million tokens: (input, output, cache read). Cache writes cost 1.25x
# the input price with a 5 minutes TTL, 2x with a 1 hour TTL.
# Unknown models are counted with the most expensive known prices.
_PRICES_PER_MTOK = {
    "claude-opus-5-5": (4.0, 20.0, 0.20),
    "claude-sonnet-5-5": (2.0, 10.0, 0.20),
}
_DEFAULT_PRICES_PER_MTOK = _PRICES_PER_MTOK["claude-opus-5-5"]


@dataclasses.dataclass(frozen=True)
class AssistantLink:
    label: str
    path: str


@dataclasses.dataclass(frozen=True)
class AssistantHelpArticle:
    title: str
    url: str


@dataclasses.dataclass(frozen=True)
class AssistantAnswer:
    conversation_id: str
    answer: str
    links: list[AssistantLink]
    help_articles: list[AssistantHelpArticle]
    out_of_scope: bool


def _check_rate_limits(user_id: int) -> None:
    key = f"pro_assistant:user:{user_id}"
    try:
        with rate_limit.rate_limit(
            key, settings.PRO_ASSISTANT_RATE_LIMIT_SHORT_WINDOW, settings.PRO_ASSISTANT_RATE_LIMIT_SHORT_MAX
        ):
            pass
        with rate_limit.rate_limit(key, 24 * 3600, settings.PRO_ASSISTANT_RATE_LIMIT_DAILY_MAX):
            pass
    except rate_limit.RateLimitedError as exc:
        raise exceptions.ProAssistantRateLimited() from exc


def _get_budget_key() -> str:
    return f"pcapi:pro_assistant:spent_microcents:{datetime.date.today().isoformat()}"


def _check_daily_budget() -> None:
    spent_microcents = int(get_redis_client().get(_get_budget_key()) or 0)
    if spent_microcents >= settings.PRO_ASSISTANT_DAILY_BUDGET_IN_CENTS * 1_000_000:
        logger.warning("Pro assistant daily budget exhausted", extra={"feature": "pro_assistant"})
        raise exceptions.ProAssistantUnavailable()


def estimate_cost_in_microcents(model: str, usage: pro_assistant_connector.LlmUsage) -> int:
    input_price, output_price, cache_read_price = _PRICES_PER_MTOK.get(model, _DEFAULT_PRICES_PER_MTOK)
    cache_write_price = input_price * (2.0 if settings.PRO_ASSISTANT_CACHE_TTL == "1h" else 1.25)
    cost_in_usd = (
        usage.input_tokens * input_price
        + usage.output_tokens * output_price
        + usage.cache_creation_input_tokens * cache_write_price
        + usage.cache_read_input_tokens * cache_read_price
    ) / 1_000_000
    return round(cost_in_usd * 100 * 1_000_000)


def _record_spending(microcents: int) -> None:
    budget_key = _get_budget_key()
    get_redis_client().incrby(budget_key, microcents)
    get_redis_client().expire(budget_key, 2 * 24 * 3600, nx=True)


def _build_answer(conversation_id: str, output: dict | None) -> AssistantAnswer:
    if output is None:
        contact_article = knowledge.get_help_articles().get(prompt.CONTACT_SUPPORT_ARTICLE_ID)
        return AssistantAnswer(
            conversation_id=conversation_id,
            answer=FALLBACK_ANSWER,
            links=[],
            help_articles=[AssistantHelpArticle(title=contact_article.title, url=contact_article.url)]
            if contact_article
            else [],
            out_of_scope=False,
        )

    out_of_scope = bool(output.get("out_of_scope"))
    links: list[AssistantLink] = []
    help_articles: list[AssistantHelpArticle] = []
    if not out_of_scope:
        # Never trust the model output: only whitelisted pages and known articles become links
        for route_id in dict.fromkeys(output.get("route_ids") or []):
            page = portal_map.PAGES_BY_ROUTE_ID.get(route_id)
            if page and len(links) < MAX_ROUTE_LINKS:
                links.append(AssistantLink(label=page.title, path=page.path))
        for article_id in dict.fromkeys(output.get("help_article_ids") or []):
            article = knowledge.get_help_articles().get(str(article_id))
            if article and len(help_articles) < MAX_HELP_ARTICLES:
                help_articles.append(AssistantHelpArticle(title=article.title, url=article.url))

    return AssistantAnswer(
        conversation_id=conversation_id,
        answer=str(output.get("answer") or FALLBACK_ANSWER)[:MAX_ANSWER_LENGTH],
        links=links,
        help_articles=help_articles,
        out_of_scope=out_of_scope,
    )


def ask(
    *,
    user_id: int,
    offerer_id: int | None,
    conversation_id: str | None,
    message: str,
    current_path: str | None,
) -> AssistantAnswer:
    """Answer a question of a pro user. `offerer_id` access must have been checked by the caller."""
    _check_rate_limits(user_id)
    _check_daily_budget()

    history = conversation_store.load_messages(user_id, conversation_id) if conversation_id else None
    if conversation_id is None or history is None:
        # Unknown or expired conversation: start a new one
        conversation_id = uuid.uuid4().hex
        history = []
    turn = sum(1 for history_message in history if history_message["role"] == "user") + 1
    if turn > settings.PRO_ASSISTANT_MAX_TURNS:
        raise exceptions.ConversationTooLong()

    question = redaction.redact(message)
    assistant_context = context_module.build_context(offerer_id, current_path)
    # The context goes in a mid-conversation system message: it carries operator
    # authority (users cannot forge it) and stays after the cached prefix.
    # The history is append-only, so that thinking blocks remain valid.
    new_messages = [
        {"role": "user", "content": question},
        {"role": "system", "content": context_module.render_for_prompt(assistant_context)},
    ]

    start = time.perf_counter()
    try:
        result = pro_assistant_connector.generate(
            system=prompt.build_system_blocks(),
            messages=history + new_messages,
            output_schema=prompt.OUTPUT_SCHEMA,
        )
    except pro_assistant_connector.ProAssistantApiException as exc:
        raise exceptions.ProAssistantUnavailable() from exc
    duration_ms = round((time.perf_counter() - start) * 1000)

    cost_in_microcents = estimate_cost_in_microcents(result.model, result.usage)
    _record_spending(cost_in_microcents)

    if result.output is not None:
        conversation_store.save_messages(
            user_id,
            conversation_id,
            history + new_messages + [{"role": "assistant", "content": result.content}],
        )
    answer = _build_answer(conversation_id, result.output)

    # No user id in this log (`avoid_current_user`): the question is redacted and kept
    # to improve the assistant, it must not be linked to a person.
    logger.info(
        "Pro assistant answered",
        extra={
            "avoid_current_user": True,
            "feature": "pro_assistant",
            "action": "answer",
            "conversation_id": conversation_id,
            "turn": turn,
            "redacted_question": question,
            "current_route_id": assistant_context.current_route_id,
            "route_links": [link.path for link in answer.links],
            "help_articles": [article.url for article in answer.help_articles],
            "out_of_scope": answer.out_of_scope,
            "stop_reason": result.stop_reason,
            "model": result.model,
            "input_tokens": result.usage.input_tokens,
            "output_tokens": result.usage.output_tokens,
            "cache_creation_input_tokens": result.usage.cache_creation_input_tokens,
            "cache_read_input_tokens": result.usage.cache_read_input_tokens,
            "estimated_cost_in_cents": cost_in_microcents / 1_000_000,
            "duration_ms": duration_ms,
        },
        technical_message_id="pro_assistant.answer",
    )
    return answer
