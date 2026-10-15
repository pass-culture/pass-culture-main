import json
import logging
from unittest import mock

import pytest

from pcapi.connectors import pro_assistant as pro_assistant_connector
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.pro_assistant import api
from pcapi.core.pro_assistant import exceptions
from pcapi.core.pro_assistant import knowledge
from pcapi.core.pro_assistant import prompt
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def _llm_result(output: dict | None, stop_reason: str = "end_turn") -> pro_assistant_connector.LlmResult:
    return pro_assistant_connector.LlmResult(
        content=[{"type": "text", "text": json.dumps(output)}] if output else [],
        output=output,
        stop_reason=stop_reason,
        model="claude-opus-5-5",
        usage=pro_assistant_connector.LlmUsage(
            input_tokens=1_000, output_tokens=500, cache_creation_input_tokens=0, cache_read_input_tokens=100_000
        ),
    )


DEFAULT_OUTPUT = {
    "answer": "Rendez-vous sur la page **Guichet**.",
    "route_ids": ["desk"],
    "help_article_ids": [],
    "out_of_scope": False,
}


@pytest.fixture(name="generate")
def generate_fixture():
    with mock.patch(
        "pcapi.connectors.pro_assistant.generate", return_value=_llm_result(DEFAULT_OUTPUT)
    ) as generate_mock:
        yield generate_mock


def _ask(user_id: int, message: str = "Comment valider une contremarque ?", **kwargs) -> api.AssistantAnswer:
    params = {"offerer_id": None, "conversation_id": None, "current_path": "/accueil"} | kwargs
    return api.ask(user_id=user_id, message=message, **params)


class AskTest:
    def test_no_personal_data_is_sent_to_the_llm(self, generate):
        user = users_factories.ProFactory(
            email="zebulon.xyzzyquux@exemple.fr", firstName="Zébulon", lastName="Xyzzyquux"
        )
        offerer = offerers_factories.OffererFactory(name="Librairie Plopinette", siren="918273645")
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        _ask(
            user.id,
            message="Je suis zebulon.xyzzyquux@exemple.fr, SIREN 918273645, tel 06 12 34 56 78 : mon IBAN ?",
            offerer_id=offerer.id,
        )

        sent_payload = json.dumps(generate.call_args.kwargs, ensure_ascii=False)
        for personal_data in ("zebulon.xyzzyquux", "Zébulon", "Xyzzyquux", "Plopinette", "918273645", "12 34 56 78"):
            assert personal_data not in sent_payload
        assert "Je suis [EMAIL], SIREN [SIREN], tel [TELEPHONE] : mon IBAN ?" in sent_payload

    def test_send_anonymous_context(self, generate):
        user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory(allowedOnAdage=True)
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        _ask(user.id, offerer_id=offerer.id, current_path="/offres/collectives")

        messages = generate.call_args.kwargs["messages"]
        assert messages[0] == {"role": "user", "content": "Comment valider une contremarque ?"}
        assert messages[1]["role"] == "system"
        assert "page actuelle : Offres collectives réservables (collective_bookable_offers)" in messages[1]["content"]
        assert "référencée sur ADAGE (peut proposer des offres collectives) : oui" in messages[1]["content"]
        assert "compte bancaire validé : non" in messages[1]["content"]

    def test_send_cached_system_prompt_and_output_schema(self, generate):
        user = users_factories.ProFactory()

        _ask(user.id)

        assert generate.call_args.kwargs["system"] == prompt.build_system_blocks()
        assert generate.call_args.kwargs["system"][-1]["cache_control"] == {"type": "ephemeral", "ttl": "5m"}
        assert generate.call_args.kwargs["output_schema"] == prompt.OUTPUT_SCHEMA

    def test_return_whitelisted_links_only(self, generate):
        generate.return_value = _llm_result(
            {
                "answer": "Voici les pages utiles.",
                "route_ids": ["desk", "not_a_page", "desk", "individual_bookings"],
                "help_article_ids": [prompt.CONTACT_SUPPORT_ARTICLE_ID, "999"],
                "out_of_scope": False,
            }
        )
        user = users_factories.ProFactory()

        answer = _ask(user.id)

        assert answer.answer == "Voici les pages utiles."
        assert answer.links == [
            api.AssistantLink(label="Guichet", path="/guichet"),
            api.AssistantLink(label="Réservations individuelles", path="/reservations"),
        ]
        assert [article.url for article in answer.help_articles] == [
            knowledge.get_help_articles()[prompt.CONTACT_SUPPORT_ARTICLE_ID].url
        ]

    def test_out_of_scope_answer_has_no_link(self, generate):
        generate.return_value = _llm_result(
            {"answer": "Je ne peux vous aider que sur le portail.", "route_ids": ["desk"], "out_of_scope": True}
        )
        user = users_factories.ProFactory()

        answer = _ask(user.id, message="Écris-moi un script Python")

        assert answer.out_of_scope
        assert answer.links == []
        assert answer.help_articles == []

    def test_refusal_returns_fallback_answer_and_is_not_saved(self, generate):
        generate.return_value = _llm_result(None, stop_reason="refusal")
        user = users_factories.ProFactory()

        answer = _ask(user.id)
        _ask(user.id, conversation_id=answer.conversation_id)

        assert answer.answer == api.FALLBACK_ANSWER
        assert [article.title for article in answer.help_articles] == [
            "[Acteurs culturels] Quelle équipe contacter selon votre demande ?"
        ]
        # The refused turn was not saved: the second question starts from an empty history
        assert len(generate.call_args.kwargs["messages"]) == 2

    def test_history_is_replayed(self, generate):
        user = users_factories.ProFactory()

        first_answer = _ask(user.id, message="Première question")
        second_answer = _ask(user.id, message="Deuxième question", conversation_id=first_answer.conversation_id)

        assert second_answer.conversation_id == first_answer.conversation_id
        messages = generate.call_args.kwargs["messages"]
        assert [message["role"] for message in messages] == ["user", "system", "assistant", "user", "system"]
        assert messages[0]["content"] == "Première question"
        assert messages[2]["content"] == [{"type": "text", "text": json.dumps(DEFAULT_OUTPUT)}]
        assert messages[3]["content"] == "Deuxième question"

    def test_history_is_scoped_by_user(self, generate):
        user = users_factories.ProFactory()
        other_user = users_factories.ProFactory()

        answer = _ask(user.id, message="Question confidentielle")
        other_answer = _ask(other_user.id, conversation_id=answer.conversation_id)

        assert other_answer.conversation_id != answer.conversation_id
        assert "Question confidentielle" not in json.dumps(generate.call_args.kwargs["messages"])

    @pytest.mark.settings(PRO_ASSISTANT_MAX_TURNS=1)
    def test_conversation_too_long(self, generate):
        user = users_factories.ProFactory()
        answer = _ask(user.id)

        with pytest.raises(exceptions.ConversationTooLong):
            _ask(user.id, conversation_id=answer.conversation_id)

    @pytest.mark.settings(PRO_ASSISTANT_RATE_LIMIT_SHORT_MAX=1)
    def test_rate_limited(self, generate):
        user = users_factories.ProFactory()
        _ask(user.id)

        with pytest.raises(exceptions.ProAssistantRateLimited):
            _ask(user.id)
        assert generate.call_count == 1

    def test_daily_budget_exhausted(self, generate, settings):
        user = users_factories.ProFactory()
        # 1000 input + 500 output + 100,000 cache read tokens with Opus 5.5 = 0.4 + 1 + 2 = 3.4 cents
        settings.PRO_ASSISTANT_DAILY_BUDGET_IN_CENTS = 3
        _ask(user.id)

        with pytest.raises(exceptions.ProAssistantUnavailable):
            _ask(user.id)
        assert generate.call_count == 1

    def test_llm_error(self, generate):
        generate.side_effect = pro_assistant_connector.ProAssistantApiException()
        user = users_factories.ProFactory()

        with pytest.raises(exceptions.ProAssistantUnavailable):
            _ask(user.id)

    def test_log_metrics_without_user_id(self, generate, caplog):
        user = users_factories.ProFactory()

        with caplog.at_level(logging.INFO):
            _ask(user.id, message="Mon email est a@b.fr, comment valider une contremarque ?")

        record = next(record for record in caplog.records if record.message == "Pro assistant answered")
        assert record.extra["avoid_current_user"] is True
        assert record.extra["redacted_question"] == "Mon email est [EMAIL], comment valider une contremarque ?"
        assert record.extra["cache_read_input_tokens"] == 100_000
        assert record.extra["estimated_cost_in_cents"] == pytest.approx(3.4)
        assert record.extra["route_links"] == ["/guichet"]
        assert record.technical_message_id == "pro_assistant.answer"


class EstimateCostTest:
    @pytest.mark.settings(PRO_ASSISTANT_CACHE_TTL="5m")
    def test_opus_cost_with_cache_write(self):
        usage = pro_assistant_connector.LlmUsage(
            input_tokens=1_000_000, output_tokens=1_000_000, cache_creation_input_tokens=1_000_000
        )

        # $4 input + $20 output + $5 cache write (1.25x)
        assert api.estimate_cost_in_microcents("claude-opus-5-5", usage) == 2_900 * 1_000_000

    @pytest.mark.settings(PRO_ASSISTANT_CACHE_TTL="1h")
    def test_unknown_model_uses_opus_prices(self):
        usage = pro_assistant_connector.LlmUsage(
            cache_creation_input_tokens=1_000_000, cache_read_input_tokens=1_000_000
        )

        # $8 cache write (2x with 1 hour TTL) + $0.20 cache read
        assert api.estimate_cost_in_microcents("another-model", usage) == 820 * 1_000_000
