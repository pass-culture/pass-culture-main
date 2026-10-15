from unittest import mock

import anthropic
import httpx2
import pytest
from anthropic.types.beta import BetaMessage

from pcapi.connectors import pro_assistant


SYSTEM = [{"type": "text", "text": "Règles"}]
MESSAGES = [{"role": "user", "content": "Comment créer une offre ?"}]
SCHEMA = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}


def _build_message(content: list[dict], stop_reason: str = "end_turn", **kwargs) -> BetaMessage:
    return BetaMessage.model_validate(
        {
            "id": "msg_1",
            "type": "message",
            "role": "assistant",
            "model": "claude-opus-5-5",
            "content": content,
            "stop_reason": stop_reason,
            "stop_sequence": None,
            "usage": {
                "input_tokens": 120,
                "output_tokens": 80,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 150_000,
            },
            **kwargs,
        }
    )


@pytest.fixture(name="client")
def client_fixture():
    client = mock.MagicMock()
    with mock.patch("pcapi.connectors.pro_assistant._get_client", return_value=client):
        yield client


@pytest.mark.settings(
    PRO_ASSISTANT_BACKEND="pcapi.connectors.pro_assistant.AnthropicBackend",
    PRO_ASSISTANT_MODEL="claude-opus-5-5",
    PRO_ASSISTANT_EFFORT="low",
)
class AnthropicBackendTest:
    def test_generate(self, client):
        client.beta.messages.create.return_value = _build_message(
            [
                {"type": "thinking", "thinking": "", "signature": "sig"},
                {"type": "text", "text": '{"answer": "Bonjour", "route_ids": ["desk"]}'},
            ]
        )

        result = pro_assistant.generate(system=SYSTEM, messages=MESSAGES, output_schema=SCHEMA)

        client.beta.messages.create.assert_called_once_with(
            model="claude-opus-5-5",
            max_tokens=pro_assistant.MAX_OUTPUT_TOKENS,
            system=SYSTEM,
            messages=MESSAGES,
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        assert result.output == {"answer": "Bonjour", "route_ids": ["desk"]}
        assert result.stop_reason == "end_turn"
        assert result.model == "claude-opus-5-5"
        # Thinking blocks are kept, to be sent back unchanged in the next turn
        assert result.content == [
            {"type": "thinking", "thinking": "", "signature": "sig"},
            {"type": "text", "text": '{"answer": "Bonjour", "route_ids": ["desk"]}'},
        ]
        assert result.usage == pro_assistant.LlmUsage(
            input_tokens=120, output_tokens=80, cache_creation_input_tokens=0, cache_read_input_tokens=150_000
        )

    def test_refusal_has_no_output(self, client):
        client.beta.messages.create.return_value = _build_message(
            [],
            stop_reason="refusal",
            stop_details={"type": "refusal", "category": "cyber", "explanation": "..."},
        )

        result = pro_assistant.generate(system=SYSTEM, messages=MESSAGES, output_schema=SCHEMA)

        assert result.output is None
        assert result.stop_reason == "refusal"

    def test_truncated_answer_has_no_output(self, client):
        client.beta.messages.create.return_value = _build_message(
            [{"type": "text", "text": '{"answer": "Bonj'}], stop_reason="max_tokens"
        )

        result = pro_assistant.generate(system=SYSTEM, messages=MESSAGES, output_schema=SCHEMA)

        assert result.output is None

    @pytest.mark.parametrize(
        "error",
        [
            anthropic.RateLimitError(
                "slow down",
                response=httpx2.Response(429, request=httpx2.Request("POST", "https://api.anthropic.com")),
                body=None,
            ),
            anthropic.InternalServerError(
                "boom",
                response=httpx2.Response(500, request=httpx2.Request("POST", "https://api.anthropic.com")),
                body=None,
            ),
            anthropic.APIConnectionError(request=httpx2.Request("POST", "https://api.anthropic.com")),
        ],
    )
    def test_api_errors(self, client, error):
        client.beta.messages.create.side_effect = error

        with pytest.raises(pro_assistant.ProAssistantApiException):
            pro_assistant.generate(system=SYSTEM, messages=MESSAGES, output_schema=SCHEMA)

    def test_log_api_error_message(self, client, caplog):
        client.beta.messages.create.side_effect = anthropic.BadRequestError(
            "invalid",
            response=httpx2.Response(
                400, request=httpx2.Request("POST", "https://api.anthropic.com"), headers={"request-id": "req_1"}
            ),
            body={"type": "error", "error": {"type": "invalid_request_error", "message": "Missing workspace"}},
        )

        with pytest.raises(pro_assistant.ProAssistantApiException):
            pro_assistant.generate(system=SYSTEM, messages=MESSAGES, output_schema=SCHEMA)

        record = next(record for record in caplog.records if record.message == "Claude API returned an error")
        assert record.extra["status_code"] == 400
        assert record.extra["error_message"] == "Missing workspace"
        assert record.extra["request_id"] == "req_1"

    def test_count_tokens(self, client):
        client.beta.messages.count_tokens.return_value = mock.Mock(input_tokens=171_234)

        assert pro_assistant.count_tokens(system=SYSTEM, messages=MESSAGES) == 171_234


class GetClientTest:
    def teardown_method(self):
        pro_assistant._get_client.cache_clear()

    @pytest.mark.settings(ANTHROPIC_API_KEY="sk-test", ANTHROPIC_WORKSPACE_ID="wrkspc_123")
    def test_send_workspace_header(self):
        pro_assistant._get_client.cache_clear()

        client = pro_assistant._get_client()

        assert client.default_headers["anthropic-workspace-id"] == "wrkspc_123"

    @pytest.mark.settings(ANTHROPIC_API_KEY="sk-test", ANTHROPIC_WORKSPACE_ID="")
    def test_no_workspace_header_by_default(self):
        pro_assistant._get_client.cache_clear()

        client = pro_assistant._get_client()

        assert "anthropic-workspace-id" not in client.default_headers
